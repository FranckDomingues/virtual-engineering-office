"""Pure domain: does not import storage, GitHub clients, or LLM SDKs."""
from dataclasses import dataclass
from enum import Enum


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"


@dataclass(frozen=True)
class WorkItem:
    task_id: str
    title: str
    milestone: str
    objective: str
    pass_criteria: str
    out_of_scope: str
    status: TaskStatus = TaskStatus.BACKLOG

    def __post_init__(self) -> None:
        for field in ("task_id", "title", "milestone", "objective", "pass_criteria", "out_of_scope"):
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must not be empty")


@dataclass(frozen=True)
class Recommendation:
    title: str
    evidence: str
    risk: str
    smallest_test: str
    requires_approval: bool = True
