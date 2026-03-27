"""Competitor Intelligence Agent — maps competitive landscape."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class CompetitorAgent(BaseResearchAgent):
    agent_type = "competitor"
    model = "claude-sonnet-4-6"

    def build_search_query(self, inp: AgentInput) -> str:
        return f"{inp.query} competitors key players market leaders alternatives 2024 2025"

    @property
    def system_prompt(self) -> str:
        return """You are the Competitor Intelligence Agent for Parallax.

Your role: Map the competitive landscape — identify key players, their strengths/weaknesses,
market positions, funding, and strategic moves. Use the provided web search results as primary evidence.

Respond with JSON:
{
  "summary": "2-3 sentence competitive landscape summary",
  "findings": [
    {
      "title": "Competitor name or finding",
      "description": "Detailed competitive insight with data from search results",
      "confidence": 0.0-1.0,
      "category": "direct_competitor|indirect_competitor|market_leader|new_entrant|strategic_move",
      "source_url": "URL if from search results"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "top_competitors": ["Company A", "Company B"],
  "market_concentration": "fragmented|concentrated|duopoly|monopoly"
}"""

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
            findings=[{"title": "Competitor Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
