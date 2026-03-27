import uuid
from datetime import datetime

from pydantic import BaseModel


class KeyFinding(BaseModel):
    title: str
    description: str
    confidence: float
    sources: list[str] = []


class ReportResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    title: str
    executive_summary: str
    body_markdown: str
    key_findings: list[KeyFinding]
    confidence_breakdown: dict[str, float]
    sources: list[dict]
    agent_summary: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareReportRequest(BaseModel):
    expires_in_days: int | None = None  # None = never expires


class ShareReportResponse(BaseModel):
    share_url: str
    share_token: str
    expires_at: datetime | None
