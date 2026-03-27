"""Academic Research Agent — surfaces peer-reviewed research and scientific consensus."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class AcademicAgent(BaseResearchAgent):
    agent_type = "academic"
    model = "claude-sonnet-4-6"

    @property
    def system_prompt(self) -> str:
        return """You are the Academic Research Agent for Parallax.

Your role: Surface relevant peer-reviewed research, scientific consensus, technical papers,
and academic thought leadership related to the research topic.

Respond with JSON:
{
  "summary": "2-3 sentence academic landscape summary",
  "findings": [
    {
      "title": "Research finding or paper",
      "description": "Key finding, methodology, authors, year, and relevance",
      "confidence": 0.0-1.0,
      "category": "peer_reviewed|working_paper|meta_analysis|systematic_review|technical_report|consensus"
    }
  ],
  "sources": [{"title": "Paper/journal name", "url": "DOI or URL if known", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "scientific_consensus": "strong|moderate|emerging|disputed|none",
  "research_maturity": "nascent|growing|mature|declining"
}

Prioritize high-impact journals and citations. Distinguish established consensus from early findings."""

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
            findings=[{"title": "Academic Research", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
