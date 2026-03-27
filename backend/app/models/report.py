import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Report(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "reports"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    confidence_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    sources: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    agent_summary: Mapped[dict] = mapped_column(JSONB, default=dict)

    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="report")  # type: ignore[name-defined]  # noqa: F821
    shares: Mapped[list["ReportShare"]] = relationship(
        "ReportShare", back_populates="report", cascade="all, delete-orphan"
    )


class ReportShare(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "report_shares"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    share_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    view_count: Mapped[int] = mapped_column(default=0, nullable=False)

    report: Mapped["Report"] = relationship("Report", back_populates="shares")
