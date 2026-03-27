"""Usage tracking and rate limiting."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RateLimitError
from app.models.research import ResearchTask, TaskStatus
from app.models.subscription import PlanTier, Subscription
from app.models.user import User
from app.models.workspace import Workspace

PLAN_MONTHLY_LIMITS = {
    PlanTier.FREE: 3,
    PlanTier.STARTER: 30,
    PlanTier.PRO: 100,
    PlanTier.TEAM: 500,
    PlanTier.ENTERPRISE: 999_999,
}


async def check_research_limit(user: User, db: AsyncSession) -> None:
    """Raise RateLimitError if user has exceeded their monthly research limit."""
    # Get user's subscription via their primary workspace
    result = await db.execute(
        select(Subscription)
        .join(Workspace)
        .where(Workspace.owner_id == user.id)
        .limit(1)
    )
    subscription = result.scalar_one_or_none()
    plan = subscription.plan if subscription else PlanTier.FREE
    limit = PLAN_MONTHLY_LIMITS.get(plan, 3)

    # Count tasks this calendar month
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    count_result = await db.execute(
        select(func.count())
        .where(
            ResearchTask.user_id == user.id,
            ResearchTask.created_at >= month_start,
            ResearchTask.status != TaskStatus.CANCELED,
        )
    )
    used = count_result.scalar_one()

    if used >= limit:
        raise RateLimitError(
            f"You have used {used}/{limit} research tasks this month. "
            "Upgrade your plan to continue."
        )
