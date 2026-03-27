"""Cross-Validator Agent — finds contradictions and conflicting evidence across agent outputs."""

import json
import re
from typing import Any

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class CrossValidatorAgent(BaseResearchAgent):
    agent_type = "cross_validator"
    model = "claude-opus-4-6"

    @property
    def system_prompt(self) -> str:
        return """You are the Cross-Validator for Parallax, a multi-agent research network.

Your role: Analyze outputs from multiple research agents, identify contradictions,
conflicting data points, and claims that need verification. Assign a confidence score
to each major claim based on how many agents support or contradict it.

Respond with JSON:
{
  "validation_summary": "2-3 sentences on overall consistency of findings",
  "validated_claims": [
    {
      "claim": "Specific claim from agent outputs",
      "supporting_agents": ["market", "news"],
      "contradicting_agents": ["financial"],
      "confidence": 0.0-1.0,
      "verdict": "verified|disputed|uncertain",
      "notes": "Why this confidence level"
    }
  ],
  "contradictions": [
    {
      "topic": "What the contradiction is about",
      "agent_a": "market",
      "claim_a": "What market agent said",
      "agent_b": "financial",
      "claim_b": "What financial agent said",
      "resolution": "How to interpret this conflict"
    }
  ],
  "overall_confidence": 0.0-1.0,
  "data_quality": "high|medium|low"
}"""

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return AgentOutput(
                    agent_type=self.agent_type,
                    findings=data.get("validated_claims", []),
                    sources=[],
                    confidence_score=data.get("overall_confidence", 0.7),
                    tokens_used=0,
                    summary=data.get("validation_summary", ""),
                )
            except json.JSONDecodeError:
                pass
        return AgentOutput(
            agent_type=self.agent_type,
            findings=[],
            sources=[],
            confidence_score=0.5,
            tokens_used=0,
            summary="Validation completed with limited structured output.",
        )

    def validate(self, query: str, agent_outputs: list[dict[str, Any]]) -> AgentOutput:
        """Validate a collection of agent outputs against each other."""
        outputs_text = json.dumps(agent_outputs, indent=2)
        inp = AgentInput(query=query, depth="standard")
        user_message = (
            f"Original Research Query: {query}\n\n"
            f"Agent Outputs to Validate:\n{outputs_text[:8000]}\n\n"
            "Cross-validate these findings and identify contradictions."
        )
        raw, tokens = self._call_claude(self.system_prompt, user_message)
        output = self.parse_response(raw, inp)
        output.tokens_used = tokens
        output.raw_response = raw
        return output
