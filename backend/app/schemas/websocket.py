from enum import Enum
from typing import Any

from pydantic import BaseModel


class WSEventType(str, Enum):
    TASK_STARTED = "task.started"
    AGENT_STARTED = "agent.started"
    AGENT_PROGRESS = "agent.progress"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    SYNTHESIS_STARTED = "synthesis.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


class WSEvent(BaseModel):
    event: WSEventType
    task_id: str
    data: dict[str, Any] = {}
    timestamp: str
