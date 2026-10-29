"""Tests for monthly research limits."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RateLimitError
from app.models.research import ResearchTask
from app.models.subscription import PlanTier, Subscription
from app.models.user import User
from app.models.workspace import Workspace
from app.services.usage import check_research_limit


async def _add_tasks(db: AsyncSession, user: User, count: int) -> None:
    db.add_all(
        ResearchTask(user_id=user.id, query="What is the AI tools market?")
        for _ in range(count)
    )
    await db.flush()


async def _subscribe(db: AsyncSession, user: User, plan: PlanTier) -> None:
    workspace = Workspace(name="WS", slug=uuid.uuid4().hex, owner_id=user.id)
    db.add(workspace)
    await db.flush()
    db.add(Subscription(workspace_id=workspace.id, plan=plan))
    await db.flush()


async def test_free_plan_blocks_after_limit(db: AsyncSession, user: User) -> None:
    await _add_tasks(db, user, 3)
    with pytest.raises(RateLimitError):
        await check_research_limit(user, db)


async def test_free_plan_allows_under_limit(db: AsyncSession, user: User) -> None:
    await _add_tasks(db, user, 2)
    await check_research_limit(user, db)


@pytest.mark.parametrize("plan", [PlanTier.TEAM, PlanTier.ENTERPRISE])
async def test_unlimited_plans_never_block(
    db: AsyncSession, user: User, plan: PlanTier
) -> None:
    await _subscribe(db, user, plan)
    await _add_tasks(db, user, 501)
    await check_research_limit(user, db)
