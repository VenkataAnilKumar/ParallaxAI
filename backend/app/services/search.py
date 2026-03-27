"""Unified web search service — Tavily primary, Exa fallback."""

from dataclasses import dataclass

import structlog

from app.config import settings

log = structlog.get_logger()


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: float = 0.0
    published_date: str = ""


def search_tavily(query: str, max_results: int = 8) -> list[SearchResult]:
    """Search via Tavily API — optimized for AI agents."""
    if not settings.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_raw_content=False,
        )
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", "")[:800],
                score=r.get("score", 0.0),
                published_date=r.get("published_date", ""),
            )
            for r in response.get("results", [])
        ]
    except Exception as exc:
        log.warning("tavily_search_failed", query=query[:60], error=str(exc))
        return []


def search_exa(query: str, max_results: int = 5) -> list[SearchResult]:
    """Search via Exa API — semantic/neural search for high-quality sources."""
    if not settings.EXA_API_KEY:
        return []
    try:
        from exa_py import Exa
        client = Exa(api_key=settings.EXA_API_KEY)
        response = client.search_and_contents(
            query=query,
            num_results=max_results,
            text={"max_characters": 800},
            use_autoprompt=True,
        )
        return [
            SearchResult(
                title=r.title or "",
                url=r.url or "",
                content=r.text or "",
                score=r.score or 0.0,
                published_date=getattr(r, "published_date", "") or "",
            )
            for r in response.results
        ]
    except Exception as exc:
        log.warning("exa_search_failed", query=query[:60], error=str(exc))
        return []


def web_search(
    query: str,
    max_results: int = 8,
    use_exa: bool = False,
) -> list[SearchResult]:
    """
    Search the web. Uses Tavily by default (better for news/market data).
    Use Exa for academic/semantic queries.
    Falls back gracefully if API keys are missing.
    """
    if use_exa and settings.EXA_API_KEY:
        results = search_exa(query, max_results)
        if results:
            return results
    # Primary: Tavily
    results = search_tavily(query, max_results)
    if results:
        return results
    # Fallback: Exa if Tavily failed
    if settings.EXA_API_KEY and not use_exa:
        return search_exa(query, max_results)
    return []


def format_results_for_prompt(results: list[SearchResult]) -> str:
    """Format search results into a clean block for Claude's context."""
    if not results:
        return "No web search results available. Use your training knowledge."

    lines = ["## Live Web Search Results\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"**[{i}] {r.title}**")
        if r.url:
            lines.append(f"URL: {r.url}")
        if r.published_date:
            lines.append(f"Date: {r.published_date}")
        lines.append(r.content.strip())
        lines.append("")
    return "\n".join(lines)
