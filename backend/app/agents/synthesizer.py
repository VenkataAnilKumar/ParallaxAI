"""Synthesis Agent — produces the final comprehensive research report."""

import json
import re
from typing import Any

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class SynthesisAgent(BaseResearchAgent):
    agent_type = "synthesis"
    model = "claude-opus-4-6"
    max_tokens = 8192  # Reports can be long

    @property
    def system_prompt(self) -> str:
        return """You are the Synthesis Agent for Parallax, a multi-agent research network.

Your role: Synthesize validated findings from all specialist agents into a comprehensive,
executive-quality research report. The report should be actionable, well-structured, and
cite confidence levels for key claims.

Output a JSON object:
{
  "title": "Compelling research report title",
  "executive_summary": "3-4 paragraph executive summary covering key findings and implications",
  "key_findings": [
    {
      "title": "Finding title",
      "description": "Detailed finding with context and implications",
      "confidence": 0.0-1.0,
      "sources": ["Agent type or source name"]
    }
  ],
  "body_sections": [
    {
      "heading": "Section heading",
      "content": "Full section content in markdown"
    }
  ],
  "confidence_breakdown": {
    "market": 0.85,
    "competitor": 0.78,
    "regulatory": 0.90
  },
  "strategic_implications": ["Implication 1", "Implication 2"],
  "risks_to_watch": ["Risk 1", "Risk 2"],
  "recommended_next_steps": ["Step 1", "Step 2"],
  "overall_confidence": 0.0-1.0
}

Write in clear, professional prose. Use markdown for the body sections.
Be direct about what is known with high confidence vs. what is uncertain."""

    def synthesize(
        self,
        query: str,
        agent_outputs: list[dict[str, Any]],
        validation_output: dict[str, Any] | None = None,
    ) -> AgentOutput:
        outputs_text = json.dumps(agent_outputs, indent=2)
        validation_text = json.dumps(validation_output, indent=2) if validation_output else "N/A"

        inp = AgentInput(query=query, depth="standard")
        user_message = (
            f"Research Query: {query}\n\n"
            f"Agent Research Outputs:\n{outputs_text[:10000]}\n\n"
            f"Cross-Validation Results:\n{validation_text[:3000]}\n\n"
            "Synthesize these into a comprehensive research report."
        )
        raw, tokens = self._call_claude(self.system_prompt, user_message)
        output = self.parse_response(raw, inp)
        output.tokens_used = tokens
        output.raw_response = raw
        return output

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                # Build markdown body from sections
                sections = data.get("body_sections", [])
                body_md = "\n\n".join(
                    f"## {s['heading']}\n\n{s['content']}" for s in sections
                )
                return AgentOutput(
                    agent_type=self.agent_type,
                    findings=data.get("key_findings", []),
                    sources=[],
                    confidence_score=data.get("overall_confidence", 0.8),
                    tokens_used=0,
                    summary=data.get("executive_summary", "")[:500],
                    raw_response=json.dumps({**data, "body_markdown": body_md}),
                )
            except json.JSONDecodeError:
                pass
        return AgentOutput(
            agent_type=self.agent_type,
            findings=[],
            sources=[],
            confidence_score=0.5,
            tokens_used=0,
            summary="Synthesis completed.",
            raw_response=raw,
        )
