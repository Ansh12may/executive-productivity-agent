from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    UNOWNED = "unowned"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Evidence(BaseModel):
    source_type: str
    source_id: str
    content: str




class Task(BaseModel):

    id: str

    title: str

    owner: Optional[str] = None

    stakeholder: Optional[str] = None

    deadline: Optional[str] = None

    status: TaskStatus = TaskStatus.OPEN

    priority: Priority = Priority.MEDIUM

    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    evidence: List[Evidence] = Field(default_factory=list)


class TaskList(BaseModel):

    tasks: List[Task]


class CalendarEvent(BaseModel):
    person: str
    date: str
    start_time: str
    end_time: str
    title: str


class AgentState(BaseModel):
    user_query: str

    tasks: List[Task] = Field(default_factory=list)
    calendar_events: List[CalendarEvent] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)

    conflicts: List[str] = Field(default_factory=list)

    final_response: str = ""