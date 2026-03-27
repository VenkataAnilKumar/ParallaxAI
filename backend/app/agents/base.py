"""Base agent class for all Parallax research agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.services.search import SearchResult, format_results_for_prompt, web_search

log = structlog.get_logger()


@dataclass
class AgentInput:
    query: str
    depth: str  # quick | standard | deep
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    agent_type: str
    findings: list[dict[str, Any]]
    sources: list[dict[str, str]]
    confidence_score: float
    tokens_used: int
    summary: str
    raw_response: str = ""


# Search result counts by depth
SEARCH_RESULTS_BY_DEPTH = {
    "quick": 5,
    "standard": 8,
    "deep": 12,
}


class BaseResearchAgent(ABC):
    """All research agents inherit from this base."""

    agent_type: str = "base"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096

    # Override in subclasses to use Exa (better for academic/semantic queries)
    use_exa_search: bool = False

    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.log = log.bind(agent=self.agent_type)

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Each agent defines its own system prompt."""
        ...

    def build_search_query(self, inp: AgentInput) -> str:
        """
        Build a focused search query for this agent's specialty.
        Subclasses override this to get domain-specific results.
        Default falls back to the raw user query.
        """
        return inp.query

    def fetch_search_results(self, inp: AgentInput) -> list[SearchResult]:
        """Run web search and return results. Graceful no-op if keys missing."""
        query = self.build_search_query(inp)
        max_results = SEARCH_RESULTS_BY_DEPTH.get(inp.depth, 8)
        results = web_search(query, max_results=max_results, use_exa=self.use_exa_search)
        self.log.info(
            "search_completed",
            query=query[:80],
            results=len(results),
            source="exa" if self.use_exa_search else "tavily",
        )
        return results

    def build_user_message(self, inp: AgentInput, search_results: list[SearchResult]) -> str:
        """Build the user turn message, injecting live search results."""
        depth_instructions = {
            "quick": "Provide a concise analysis focusing on the most critical points. Aim for speed.",
            "standard": "Provide a thorough analysis covering key aspects with supporting evidence.",
            "deep": "Provide an exhaustive analysis. Leave no stone unturned. Include edge cases.",
        }

        search_block = format_results_for_prompt(search_results)

        return (
            f"Research Query: {inp.query}\n\n"
            f"Depth: {depth_instructions.get(inp.depth, depth_instructions['standard'])}\n\n"
            f"{search_block}\n\n"
            "Using the web search results above as your primary sources (cite URLs where possible), "
            "perform your specialist analysis. Where search results are insufficient, supplement "
            "with your training knowledge and clearly flag those as 'Based on training data'."
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_claude(self, system: str, user_message: str) -> tuple[str, int]:
        """Call Claude API with retry logic. Returns (content, tokens_used)."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return content, tokens

    @abstractmethod
    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        """Parse Claude's raw response into structured AgentOutput."""
        ...

    def run(self, inp: AgentInput) -> AgentOutput:
        self.log.info("agent_started", query=inp.query[:80], depth=inp.depth)
        try:
            # Step 1: Fetch live web data
            search_results = self.fetch_search_results(inp)

            # Step 2: Build prompt with search context injected
            user_message = self.build_user_message(inp, search_results)

            # Step 3: Claude analysis
            raw, tokens = self._call_claude(self.system_prompt, user_message)

            # Step 4: Parse and enrich output
            output = self.parse_response(raw, inp)
            output.tokens_used = tokens
            output.raw_response = raw

            # Merge search result sources with agent-extracted sources
            search_sources = [
                {"title": r.title, "url": r.url, "reliability": "high"}
                for r in search_results
                if r.url
            ]
            # Deduplicate by URL (agent sources take precedence)
            existing_urls = {s.get("url", "") for s in output.sources}
            for s in search_sources:
                if s["url"] not in existing_urls:
                    output.sources.append(s)

            self.log.info(
                "agent_completed",
                findings=len(output.findings),
                sources=len(output.sources),
                confidence=output.confidence_score,
                tokens=tokens,
            )
            return output
        except Exception as exc:
            self.log.error("agent_failed", error=str(exc))
            raise
