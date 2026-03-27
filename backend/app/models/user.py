import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True  # Matches Supabase auth.users.id
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    workspaces: Mapped[list["Workspace"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Workspace", back_populates="owner"
    )
    research_tasks: Mapped[list["ResearchTask"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "ResearchTask", back_populates="user"
    )
