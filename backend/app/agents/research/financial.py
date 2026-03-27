"""Financial Intelligence Agent — analyzes financial metrics and investment landscape."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class FinancialAgent(BaseResearchAgent):
    agent_type = "financial"
    model = "claude-sonnet-4-6"

    @property
    def system_prompt(self) -> str:
        return """You are the Financial Intelligence Agent for Parallax.

Your role: Analyze financial data — revenue, growth rates, funding rounds, valuations,
M&A activity, investor activity, and financial health of key players.

Respond with JSON:
{
  "summary": "2-3 sentence financial landscape summary",
  "findings": [
    {
      "title": "Financial finding",
      "description": "Detailed financial insight with specific numbers and dates",
      "confidence": 0.0-1.0,
      "category": "revenue|funding|valuation|acquisition|ipo|financial_health|investor_activity"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "total_funding_in_space": "e.g., $2.3B in 2024",
  "investor_sentiment": "bullish|neutral|bearish"
}

Always cite the source and year for financial data. Use ranges when exact figures are unknown."""

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
            findings=[{"title": "Financial Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
