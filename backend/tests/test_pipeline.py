"""End-to-end test of the research Celery task with Claude and search stubbed."""

import json
import uuid
from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine

from app.agents.base import BaseResearchAgent
from app.services.search import SearchResult
from app.tasks import research as research_task


def fake_claude(self: BaseResearchAgent, system: str, user_message: str) -> tuple[str, int]:
    if self.agent_type == "orchestrator":
        payload: dict[str, Any] = {
            "research_plan": "Look at market and news.",
            "skip_agents": ["academic"],
        }
    elif self.agent_type == "cross_validator":
        payload = {"validation_summary": "Consistent.", "overall_confidence": 0.8}
    elif self.agent_type == "synthesis":
        payload = {
            "title": "AI Tools Report",
            "executive_summary": "The market is growing.",
            "key_findings": [
                {"title": "Growth", "description": "Fast", "confidence": 0.9}
            ],
            "body_sections": [{"heading": "Market", "content": "Big and growing."}],
            "confidence_breakdown": {"market": 0.9},
            "strategic_implications": ["Move fast"],
        }
    elif self.agent_type == "news":
        raise RuntimeError("news provider down")
    else:
        payload = {
            "summary": f"{self.agent_type} summary",
            "findings": [{"title": "F", "description": "D", "confidence": 0.7}],
            "sources": [],
            "confidence_score": 0.7,
        }
    # Wrap in a code fence like real model output sometimes is
    return f"```json\n{json.dumps(payload)}\n```", 100


def fake_search(*args: Any, **kwargs: Any) -> list[SearchResult]:
    return [SearchResult(title="Src", url="https://example.com/a", content="text")]


@pytest.fixture
def task_id(engine: AsyncEngine) -> Generator[str, None, None]:
    """Committed user + task rows (the worker uses its own sync connection)."""
    sync_engine = research_task._get_engine()
    user_id, tid = str(uuid.uuid4()), str(uuid.uuid4())
    with sync_engine.begin() as conn:
        conn.execute(
            sa.text(
                "INSERT INTO users (id, email, is_active, created_at, updated_at) "
                "VALUES (:id, :email, true, now(), now())"
            ),
            {"id": user_id, "email": f"{user_id}@parallax.app"},
        )
        conn.execute(
            sa.text(
                "INSERT INTO research_tasks (id, user_id, query, depth, status, "
                "tokens_used, cost_usd, created_at, updated_at) "
                "VALUES (:id, :uid, 'AI research tools market', 'quick', 'pending', "
                "0, 0, now(), now())"
            ),
            {"id": tid, "uid": user_id},
        )
    yield tid
    with sync_engine.begin() as conn:
        conn.execute(sa.text("DELETE FROM users WHERE id=:id"), {"id": user_id})


@patch("app.agents.base.web_search", side_effect=fake_search)
@patch.object(BaseResearchAgent, "_call_claude", fake_claude)
def test_research_pipeline_persists_results(_search: Any, task_id: str) -> None:
    result = research_task.run_research_task.run(task_id)

    assert result["status"] == "completed"
    with research_task._get_engine().connect() as conn:
        task = conn.execute(
            sa.text("SELECT status, tokens_used FROM research_tasks WHERE id=:id"),
            {"id": task_id},
        ).one()
        runs = conn.execute(
            sa.text(
                "SELECT agent_type, status, sources_found FROM agent_runs "
                "WHERE task_id=:id"
            ),
            {"id": task_id},
        ).all()
        report = conn.execute(
            sa.text(
                "SELECT title, body_markdown, key_findings, agent_summary "
                "FROM reports WHERE task_id=:id"
            ),
            {"id": task_id},
        ).one()

    assert task.status == "completed"
    # orchestrator + 5 successful agents + validator + synthesis
    assert task.tokens_used == 800

    by_agent = {r.agent_type: r for r in runs}
    assert "academic" not in by_agent  # skipped by the orchestrator plan
    assert by_agent["news"].status == "failed"
    assert by_agent["market"].status == "completed"
    assert by_agent["market"].sources_found == 1

    assert report.title == "AI Tools Report"
    assert report.body_markdown == "## Market\n\nBig and growing."
    assert report.key_findings[0]["title"] == "Growth"
    assert report.agent_summary["strategic_implications"] == ["Move fast"]


def test_canceled_task_is_skipped(task_id: str) -> None:
    research_task._update_task_status(task_id, "canceled")
    result = research_task.run_research_task.run(task_id)
    assert result["status"] == "canceled"


def claude_with_failing_orchestrator(
    self: BaseResearchAgent, system: str, user_message: str
) -> tuple[str, int]:
    if self.agent_type == "orchestrator":
        raise RuntimeError("planner unavailable")
    return fake_claude(self, system, user_message)


@patch("app.agents.base.web_search", side_effect=fake_search)
@patch.object(BaseResearchAgent, "_call_claude", claude_with_failing_orchestrator)
def test_orchestrator_failure_runs_all_agents(_search: Any, task_id: str) -> None:
    result = research_task.run_research_task.run(task_id)

    assert result["status"] == "completed"
    with research_task._get_engine().connect() as conn:
        agents = conn.execute(
            sa.text("SELECT agent_type FROM agent_runs WHERE task_id=:id"),
            {"id": task_id},
        ).scalars().all()
    assert set(agents) == {
        "market", "competitor", "regulatory", "news", "financial", "sentiment", "academic"
    }
