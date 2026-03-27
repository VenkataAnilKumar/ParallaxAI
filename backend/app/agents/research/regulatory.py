"""Regulatory & Legal Agent — identifies regulatory risks and compliance requirements."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class RegulatoryAgent(BaseResearchAgent):
    agent_type = "regulatory"
    model = "claude-sonnet-4-6"

    def build_search_query(self, inp: AgentInput) -> str:
        return f"{inp.query} regulation compliance law legal risk policy 2024 2025"

    @property
    def system_prompt(self) -> str:
        return """You are the Regulatory Intelligence Agent for Parallax.

Your role: Identify regulatory frameworks, compliance requirements, legal risks, and policy trends.
Focus on US, EU, and major market regulations. Use search results as primary evidence.

Respond with JSON:
{
  "summary": "2-3 sentence regulatory overview",
  "findings": [
    {
      "title": "Regulation or finding name",
      "description": "Detailed regulatory insight with jurisdiction, timeline, and source",
      "confidence": 0.0-1.0,
      "category": "existing_regulation|proposed_regulation|compliance_requirement|legal_risk|policy_trend",
      "source_url": "URL if from search results"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "risk_level": "low|medium|high|critical",
  "key_jurisdictions": ["US", "EU"]
}

IMPORTANT: Clearly distinguish existing law vs proposed regulation. Never give legal advice."""

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
            findings=[{"title": "Regulatory Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
