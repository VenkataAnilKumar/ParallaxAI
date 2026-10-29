"""Tests for research API endpoints."""

import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentInput
from app.agents.research.market import MarketAgent
from app.config import settings
from app.core.exceptions import RateLimitError
from app.models.research import AgentRun, ResearchTask
from app.models.user import User

QUERY = {"query": "What is the AI research tools market size?", "depth": "standard"}


class TestAuth:
    async def test_research_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/research", json=QUERY)
        assert resp.status_code in (401, 403)

    async def test_invalid_token_rejected(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/me", headers={"Authorization": "Bearer not-a-jwt"}
        )
        assert resp.status_code == 401

    async def test_valid_token_auto_provisions_user(
        self, client: AsyncClient, db: AsyncSession
    ) -> None:
        user_id = uuid.uuid4()
        token = jwt.encode(
            {
                "sub": str(user_id),
                "email": "new@parallax.app",
                "aud": "authenticated",
                "exp": int(time.time()) + 3600,
                "user_metadata": {"full_name": "New User"},
            },
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256",
        )
        resp = await client.get(
            "/api/v1/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "new@parallax.app"
        assert await db.get(User, user_id) is not None


class TestResearchEndpoints:
    @patch("app.api.routes.research.run_research_task")
    async def test_create_research_success(
        self, mock_celery: MagicMock, auth_client: AsyncClient, db: AsyncSession
    ) -> None:
        mock_celery.delay.return_value = MagicMock(id="celery-task-123")

        resp = await auth_client.post("/api/v1/research", json=QUERY)

        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "pending"
        assert body["query"] == QUERY["query"]
        mock_celery.delay.assert_called_once_with(body["id"])
        task = await db.get(ResearchTask, uuid.UUID(body["id"]))
        assert task is not None
        assert task.celery_task_id == "celery-task-123"

    async def test_create_research_validates_query(
        self, auth_client: AsyncClient
    ) -> None:
        resp = await auth_client.post("/api/v1/research", json={"query": "short"})
        assert resp.status_code == 422

    @patch(
        "app.api.routes.research.check_research_limit",
        new_callable=AsyncMock,
        side_effect=RateLimitError(),
    )
    async def test_create_research_rate_limited(
        self, _limit: AsyncMock, auth_client: AsyncClient
    ) -> None:
        resp = await auth_client.post("/api/v1/research", json=QUERY)
        assert resp.status_code == 429

    async def test_list_research_empty(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.get("/api/v1/research")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_get_research_with_agent_runs(
        self, auth_client: AsyncClient, db: AsyncSession, user: User
    ) -> None:
        task = ResearchTask(user_id=user.id, query=QUERY["query"], depth="quick")
        db.add(task)
        await db.flush()
        db.add(
            AgentRun(
                task_id=task.id,
                agent_type="market",
                status="completed",
                duration_seconds=1.5,
                sources_found=3,
                tokens_used=100,
            )
        )
        await db.flush()

        resp = await auth_client.get(f"/api/v1/research/{task.id}")
        assert resp.status_code == 200
        runs = resp.json()["agent_runs"]
        assert runs == [
            {
                "agent_type": "market",
                "status": "completed",
                "duration_seconds": 1.5,
                "sources_found": 3,
                "tokens_used": 100,
            }
        ]

    async def test_get_research_not_found(self, auth_client: AsyncClient) -> None:
        resp = await auth_client.get(f"/api/v1/research/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_get_research_of_other_user_forbidden(
        self, auth_client: AsyncClient, db: AsyncSession
    ) -> None:
        other = User(id=uuid.uuid4(), email="other@parallax.app")
        db.add(other)
        await db.flush()
        task = ResearchTask(user_id=other.id, query=QUERY["query"])
        db.add(task)
        await db.flush()

        resp = await auth_client.get(f"/api/v1/research/{task.id}")
        assert resp.status_code == 403

    @patch("app.api.routes.research.celery_app")
    async def test_cancel_pending_research(
        self,
        mock_celery_app: MagicMock,
        auth_client: AsyncClient,
        db: AsyncSession,
        user: User,
    ) -> None:
        task = ResearchTask(
            user_id=user.id, query=QUERY["query"], celery_task_id="celery-1"
        )
        db.add(task)
        await db.flush()

        resp = await auth_client.delete(f"/api/v1/research/{task.id}")

        assert resp.status_code == 204
        mock_celery_app.control.revoke.assert_called_once_with(
            "celery-1", terminate=True
        )
        result = await db.execute(
            select(ResearchTask.status).where(ResearchTask.id == task.id)
        )
        assert result.scalar_one() == "canceled"


class TestAgents:
    def test_market_agent_parses_valid_json(self) -> None:
        agent = MarketAgent()
        raw = """{
            "summary": "Large market",
            "findings": [{"title": "TAM", "description": "$45B", "confidence": 0.8}],
            "sources": [],
            "confidence_score": 0.8
        }"""
        output = agent.parse_response(raw, AgentInput(query="test", depth="standard"))
        assert output.confidence_score == 0.8
        assert len(output.findings) == 1
        assert output.summary == "Large market"

    def test_market_agent_handles_malformed_json(self) -> None:
        agent = MarketAgent()
        output = agent.parse_response(
            "not json at all", AgentInput(query="test", depth="standard")
        )
        assert output.confidence_score == 0.3
        assert output.agent_type == "market"
