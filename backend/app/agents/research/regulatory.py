"""Regulatory & Legal Agent — identifies regulatory risks and compliance requirements."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class RegulatoryAgent(BaseResearchAgent):
    agent_type = "regulatory"
    model = "claude-sonnet-4-6"

    @property
    def system_prompt(self) -> str:
        return """You are the Regulatory Intelligence Agent for Parallax.

Your role: Identify regulatory frameworks, compliance requirements, legal risks, and policy trends
relevant to the research topic. Focus on US, EU, and major market regulations.

Respond with JSON:
{
  "summary": "2-3 sentence regulatory overview",
  "findings": [
    {
      "title": "Regulation or finding name",
      "description": "Detailed regulatory insight with jurisdiction and timeline",
      "confidence": 0.0-1.0,
      "category": "existing_regulation|proposed_regulation|compliance_requirement|legal_risk|policy_trend"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "risk_level": "low|medium|high|critical",
  "key_jurisdictions": ["US", "EU"]
}

IMPORTANT: Clearly distinguish between existing law vs proposed regulation. Never give legal advice."""

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
