import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.research import ResearchDepth, TaskStatus


class ResearchCreateRequest(BaseModel):
    query: str = Field(..., min_length=10, max_length=500)
    depth: ResearchDepth = ResearchDepth.STANDARD
    agents: list[str] | None = None  # None = run all agents


class AgentRunSummary(BaseModel):
    agent_type: str
    status: str
    duration_seconds: float | None
    sources_found: int
    tokens_used: int

    model_config = {"from_attributes": True}


class ResearchTaskResponse(BaseModel):
    id: uuid.UUID
    query: str
    depth: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    tokens_used: int
    cost_usd: float
    agent_runs: list[AgentRunSummary] = []

    model_config = {"from_attributes": True}


class ResearchTaskListResponse(BaseModel):
    items: list[ResearchTaskResponse]
    total: int
    page: int
    page_size: int
