import uuid
from datetime import datetime
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    MARKET = "market"
    COMPETITOR = "competitor"
    REGULATORY = "regulatory"
    NEWS = "news"
    FINANCIAL = "financial"
    SENTIMENT = "sentiment"
    ACADEMIC = "academic"
    CROSS_VALIDATOR = "cross_validator"
    SYNTHESIS = "synthesis"


class ResearchTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="SET NULL")
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    depth: Mapped[str] = mapped_column(
        String(20), default=ResearchDepth.STANDARD, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TaskStatus.PENDING, nullable=False
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255))
    agent_config: Mapped[dict | None] = mapped_column(JSONB)  # which agents to run
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="research_tasks")  # type: ignore[name-defined]  # noqa: F821
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun", back_populates="task", cascade="all, delete-orphan"
    )
    findings: Mapped[list["ResearchFinding"]] = relationship(
        "ResearchFinding", back_populates="task", cascade="all, delete-orphan"
    )
    report: Mapped["Report | None"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Report", back_populates="task", uselist=False
    )


class AgentRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "agent_runs"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=TaskStatus.PENDING, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sources_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    raw_output: Mapped[dict | None] = mapped_column(JSONB)

    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="agent_runs")


class ResearchFinding(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_findings"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    source_title: Mapped[str | None] = mapped_column(String(512))
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata: Mapped[dict | None] = mapped_column(JSONB)

    task: Mapped["ResearchTask"] = relationship("ResearchTask", back_populates="findings")

    __table_args__ = (
        Index("ix_research_findings_embedding", "embedding", postgresql_using="ivfflat"),
    )


class CrossValidation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cross_validations"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_agents: Mapped[list[str]] = mapped_column(JSONB, default=list)
    contradicting_agents: Mapped[list[str]] = mapped_column(JSONB, default=list)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)  # verified/disputed/uncertain
    reasoning: Mapped[str | None] = mapped_column(Text)
