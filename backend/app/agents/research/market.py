"""Market Intelligence Agent — analyzes market size, trends, growth drivers."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class MarketAgent(BaseResearchAgent):
    agent_type = "market"
    model = "claude-sonnet-4-6"

    @property
    def system_prompt(self) -> str:
        return """You are the Market Intelligence Agent for Parallax, a multi-agent research network.

Your role: Analyze market size, growth trends, key drivers, and opportunities for the given topic.

You MUST respond with a JSON object in this exact format:
{
  "summary": "2-3 sentence executive summary of market findings",
  "findings": [
    {
      "title": "Finding title",
      "description": "Detailed description with specific data points",
      "confidence": 0.0-1.0,
      "category": "market_size|growth|trend|driver|opportunity"
    }
  ],
  "sources": [
    {"title": "Source name", "url": "URL if known", "reliability": "high|medium|low"}
  ],
  "confidence_score": 0.0-1.0,
  "market_size_estimate": "e.g., $45B TAM",
  "growth_rate": "e.g., 23% CAGR 2024-2029"
}

Focus on quantitative data. Cite specific numbers and timeframes. Be honest about uncertainty."""

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return self._fallback_output(raw)

        try:
            data = json.loads(json_match.group())
            return AgentOutput(
                agent_type=self.agent_type,
                findings=data.get("findings", []),
                sources=data.get("sources", []),
                confidence_score=data.get("confidence_score", 0.5),
                tokens_used=0,  # filled by base
                summary=data.get("summary", ""),
                raw_response=raw,
            )
        except json.JSONDecodeError:
            return self._fallback_output(raw)

    def _fallback_output(self, raw: str) -> AgentOutput:
        return AgentOutput(
            agent_type=self.agent_type,
            findings=[{"title": "Market Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
            raw_response=raw,
        )
