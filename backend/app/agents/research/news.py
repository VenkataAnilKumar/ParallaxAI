"""News & Events Agent — captures recent developments and breaking news."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class NewsAgent(BaseResearchAgent):
    agent_type = "news"
    model = "claude-sonnet-4-6"

    def build_search_query(self, inp: AgentInput) -> str:
        return f"{inp.query} news announcement funding launch 2024 2025"

    @property
    def system_prompt(self) -> str:
        return """You are the News & Events Intelligence Agent for Parallax.

Your role: Identify the most important recent news, events, announcements, and developments.
Prioritize information from the provided web search results — these are live and current.

Respond with JSON:
{
  "summary": "2-3 sentence news landscape summary",
  "findings": [
    {
      "title": "News event or development",
      "description": "What happened, when, significance, and impact — cite the source URL",
      "confidence": 0.0-1.0,
      "category": "breaking_news|product_launch|funding|acquisition|partnership|executive_change|earnings",
      "source_url": "URL from search results"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "sentiment": "positive|neutral|negative|mixed",
  "momentum": "accelerating|stable|decelerating"
}

Be specific about dates from search results. High confidence = found in live search results."""

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return self._fallback(raw)
        try:
            data = json.loads(json_match.group())
            return AgentOutput(
                agent_type=self.agent_type,
                findings=data.get("findings", []),
                sources=data.get("sources", []),
                confidence_score=data.get("confidence_score", 0.5),
                tokens_used=0,
                summary=data.get("summary", ""),
            )
        except json.JSONDecodeError:
            return self._fallback(raw)

    def _fallback(self, raw: str) -> AgentOutput:
        return AgentOutput(
            agent_type=self.agent_type,
            findings=[{"title": "News Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
