"""Base agent class for all Parallax research agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

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


class BaseResearchAgent(ABC):
    """All research agents inherit from this base."""

    agent_type: str = "base"
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096

    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.log = log.bind(agent=self.agent_type)

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Each agent defines its own system prompt."""
        ...

    def build_user_message(self, inp: AgentInput) -> str:
        """Build the user turn message from AgentInput."""
        depth_instructions = {
            "quick": "Provide a concise analysis focusing on the most critical points. Aim for speed.",
            "standard": "Provide a thorough analysis covering key aspects with supporting evidence.",
            "deep": "Provide an exhaustive analysis. Leave no stone unturned. Include edge cases.",
        }
        return (
            f"Research Query: {inp.query}\n\n"
            f"Depth: {depth_instructions.get(inp.depth, depth_instructions['standard'])}\n\n"
            f"Additional context: {inp.context}"
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
            user_message = self.build_user_message(inp)
            raw, tokens = self._call_claude(self.system_prompt, user_message)
            output = self.parse_response(raw, inp)
            output.tokens_used = tokens
            output.raw_response = raw
            self.log.info(
                "agent_completed",
                findings=len(output.findings),
                confidence=output.confidence_score,
                tokens=tokens,
            )
            return output
        except Exception as exc:
            self.log.error("agent_failed", error=str(exc))
            raise
