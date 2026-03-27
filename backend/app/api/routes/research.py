import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth import CurrentUser
from app.core.exceptions import ForbiddenError, NotFoundError
from app.database import get_db
from app.models.research import ResearchTask, TaskStatus
from app.schemas.research import (
    ResearchCreateRequest,
    ResearchTaskListResponse,
    ResearchTaskResponse,
)
from app.services.usage import check_research_limit
from app.tasks.research import run_research_task

router = APIRouter(prefix="/research", tags=["research"])

DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=ResearchTaskResponse, status_code=202)
async def create_research(
    body: ResearchCreateRequest,
    current_user: CurrentUser,
    db: DB,
) -> ResearchTaskResponse:
    await check_research_limit(current_user, db)

    task = ResearchTask(
        user_id=current_user.id,
        query=body.query,
        depth=body.depth,
        agent_config={"agents": body.agents} if body.agents else None,
    )
    db.add(task)
    await db.flush()

    # Dispatch to Celery
    celery_result = run_research_task.delay(str(task.id))
    task.celery_task_id = celery_result.id
    await db.flush()

    await db.refresh(task, ["agent_runs"])
    return ResearchTaskResponse.model_validate(task)


@router.get("", response_model=ResearchTaskListResponse)
async def list_research(
    current_user: CurrentUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ResearchTaskListResponse:
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count()).where(ResearchTask.user_id == current_user.id)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(ResearchTask)
        .where(ResearchTask.user_id == current_user.id)
        .options(selectinload(ResearchTask.agent_runs))
        .order_by(ResearchTask.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    tasks = result.scalars().all()

    return ResearchTaskListResponse(
        items=[ResearchTaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{task_id}", response_model=ResearchTaskResponse)
async def get_research(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    db: DB,
) -> ResearchTaskResponse:
    result = await db.execute(
        select(ResearchTask)
        .where(ResearchTask.id == task_id)
        .options(selectinload(ResearchTask.agent_runs))
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise NotFoundError("ResearchTask", str(task_id))
    if task.user_id != current_user.id:
        raise ForbiddenError()
    return ResearchTaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def cancel_research(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    db: DB,
) -> None:
    result = await db.execute(
        select(ResearchTask).where(ResearchTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise NotFoundError("ResearchTask", str(task_id))
    if task.user_id != current_user.id:
        raise ForbiddenError()
    if task.status == TaskStatus.RUNNING and task.celery_task_id:
        from app.celery_app import celery_app
        celery_app.control.revoke(task.celery_task_id, terminate=True)
    task.status = TaskStatus.CANCELED
