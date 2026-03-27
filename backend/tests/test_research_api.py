"""Tests for research API endpoints."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.fixture
def mock_user(db) -> User:
    user = User(id=uuid.uuid4(), email="test@parallax.app", full_name="Test User")
    return user


@pytest.fixture
def auth_headers() -> dict:
    # In tests, we patch get_current_user directly
    return {"Authorization": "Bearer test-token"}


class TestResearchEndpoints:
    async def test_create_research_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/research",
            json={"query": "What is the AI market size?", "depth": "standard"},
        )
        assert resp.status_code == 403

    @patch("app.api.routes.research.check_research_limit", new_callable=AsyncMock)
    @patch("app.api.routes.research.run_research_task")
    @patch("app.core.auth.get_current_user")
    async def test_create_research_success(
        self,
        mock_auth,
        mock_celery,
        mock_limit,
        client: AsyncClient,
        mock_user: User,
        auth_headers: dict,
    ):
        mock_auth.return_value = mock_user
        mock_celery.delay.return_value = MagicMock(id="celery-task-123")

        resp = await client.post(
            "/api/v1/research",
            json={"query": "What is the AI research tools market size?", "depth": "standard"},
            headers=auth_headers,
        )
        assert resp.status_code in (200, 202)

    async def test_list_research_empty(self, client: AsyncClient, auth_headers: dict):
        with patch("app.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value = User(
                id=uuid.uuid4(), email="new@parallax.app", full_name="New User"
            )
            resp = await client.get("/api/v1/research", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 0


class TestAgents:
    def test_market_agent_parses_valid_json(self):
        from app.agents.research.market import MarketAgent
        from app.agents.base import AgentInput

        agent = MarketAgent()
        raw = """{
            "summary": "Large market",
            "findings": [{"title": "TAM", "description": "$45B", "confidence": 0.8, "category": "market_size"}],
            "sources": [],
            "confidence_score": 0.8,
            "market_size_estimate": "$45B",
            "growth_rate": "23% CAGR"
        }"""
        output = agent.parse_response(raw, AgentInput(query="test", depth="standard"))
        assert output.confidence_score == 0.8
        assert len(output.findings) == 1
        assert output.summary == "Large market"

    def test_market_agent_handles_malformed_json(self):
        from app.agents.research.market import MarketAgent
        from app.agents.base import AgentInput

        agent = MarketAgent()
        output = agent.parse_response("not json at all", AgentInput(query="test", depth="standard"))
        assert output.confidence_score == 0.3
        assert output.agent_type == "market"
