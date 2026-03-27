import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.auth import CurrentUser
from app.core.exceptions import ForbiddenError, NotFoundError
from app.database import get_db
from app.models.report import Report, ReportShare
from app.models.research import ResearchTask
from app.schemas.report import (
    ReportResponse,
    ShareReportRequest,
    ShareReportResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])

DB = Annotated[AsyncSession, Depends(get_db)]


async def _get_report_for_user(
    report_id: uuid.UUID,
    current_user: "User",  # type: ignore[name-defined]  # noqa: F821
    db: AsyncSession,
) -> Report:
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.task))
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise NotFoundError("Report", str(report_id))
    if report.task.user_id != current_user.id:
        raise ForbiddenError()
    return report


@router.get("/research/{task_id}", response_model=ReportResponse)
async def get_report_by_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    db: DB,
) -> ReportResponse:
    result = await db.execute(
        select(Report)
        .join(ResearchTask)
        .where(ResearchTask.id == task_id, ResearchTask.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise NotFoundError("Report")
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/share", response_model=ShareReportResponse)
async def share_report(
    report_id: uuid.UUID,
    body: ShareReportRequest,
    current_user: CurrentUser,
    db: DB,
) -> ShareReportResponse:
    report = await _get_report_for_user(report_id, current_user, db)

    token = secrets.token_urlsafe(32)
    expires_at = None
    if body.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

    share = ReportShare(
        report_id=report.id,
        share_token=token,
        expires_at=expires_at,
    )
    db.add(share)
    await db.flush()

    share_url = f"{settings.FRONTEND_URL}/share/{token}"
    return ShareReportResponse(
        share_url=share_url,
        share_token=token,
        expires_at=expires_at,
    )


@router.get("/{report_id}/export")
async def export_report(
    report_id: uuid.UUID,
    current_user: CurrentUser,
    db: DB,
    format: Literal["markdown", "pdf"] = Query("markdown"),
) -> Response:
    report = await _get_report_for_user(report_id, current_user, db)

    if format == "markdown":
        content = f"# {report.title}\n\n{report.executive_summary}\n\n{report.body_markdown}"
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="report-{report_id}.md"'},
        )

    # PDF export would integrate a headless browser or reportlab
    return Response(
        content=report.body_markdown,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="report-{report_id}.txt"'},
    )
