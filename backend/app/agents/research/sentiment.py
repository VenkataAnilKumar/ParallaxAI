"""Sentiment Agent — analyzes public perception, social signals, and brand sentiment."""

import json
import re

from app.agents.base import AgentInput, AgentOutput, BaseResearchAgent


class SentimentAgent(BaseResearchAgent):
    agent_type = "sentiment"
    model = "claude-sonnet-4-6"

    def build_search_query(self, inp: AgentInput) -> str:
        return f"{inp.query} reviews opinions sentiment Reddit Twitter community reaction"

    @property
    def system_prompt(self) -> str:
        return """You are the Sentiment Intelligence Agent for Parallax.

Your role: Analyze public perception, social media sentiment, community discussions,
customer reviews, analyst opinions, and media coverage tone. Use search results as evidence.

Respond with JSON:
{
  "summary": "2-3 sentence sentiment overview",
  "findings": [
    {
      "title": "Sentiment finding",
      "description": "Specific signal with audience, platform, and context — cite URL",
      "confidence": 0.0-1.0,
      "category": "social_media|analyst_opinion|customer_feedback|media_coverage|community_sentiment",
      "source_url": "URL from search results"
    }
  ],
  "sources": [{"title": "...", "url": "...", "reliability": "high|medium|low"}],
  "confidence_score": 0.0-1.0,
  "overall_sentiment": "very_positive|positive|neutral|negative|very_negative|mixed",
  "sentiment_trend": "improving|stable|declining",
  "key_themes": ["theme1", "theme2"]
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
            findings=[{"title": "Sentiment Analysis", "description": raw[:500], "confidence": 0.3}],
            sources=[],
            confidence_score=0.3,
            tokens_used=0,
            summary=raw[:200],
        )
