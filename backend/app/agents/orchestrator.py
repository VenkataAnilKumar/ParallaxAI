"""Orchestrator Agent — decomposes query, coordinates agents, produces research plan."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class OrchestratorAgent(BaseResearchAgent):
    agent_type = "orchestrator"
    model = "claude-opus-4-6"  # Strongest model for planning

    @property
    def system_prompt(self) -> str:
        return """You are the Orchestrator for Parallax, a multi-agent research network.

Your role: Analyze the user's research query, decompose it into focused sub-questions for
specialist agents, and determine which agents should run and in what priority order.

Available agents:
- market: Market size, trends, growth drivers
- competitor: Competitive landscape, key players
- regulatory: Legal/regulatory risks, compliance
- news: Recent events, announcements, developments
- financial: Funding, revenue, valuations, M&A
- sentiment: Public perception, analyst opinions
- academic: Peer-reviewed research, scientific consensus

Respond with JSON:
{
  "research_plan": "2-3 sentence summary of research approach",
  "sub_questions": [
    {"agent": "market", "question": "Specific focused question for this agent"},
    {"agent": "competitor", "question": "..."}
  ],
  "priority_agents": ["market", "competitor", "news"],
  "skip_agents": [],
  "skip_reasons": {},
  "estimated_complexity": "simple|moderate|complex",
  "key_themes": ["theme1", "theme2", "theme3"]
}

Include all relevant agents unless there's a clear reason to skip (e.g., skip academic for
pure business strategy questions)."""

    def parse_response(self, raw: str, inp: AgentInput) -> AgentOutput:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return AgentOutput(
                    agent_type=self.agent_type,
                    findings=[{"plan": data}],
                    sources=[],
                    confidence_score=1.0,
                    tokens_used=0,
                    summary=data.get("research_plan", ""),
                )
            except json.JSONDecodeError:
                pass
        return AgentOutput(
            agent_type=self.agent_type,
            findings=[{"plan": {"sub_questions": [], "priority_agents": list()}}],
            sources=[],
            confidence_score=0.5,
            tokens_used=0,
            summary=raw[:200],
        )
