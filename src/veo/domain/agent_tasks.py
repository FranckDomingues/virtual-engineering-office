"""Domain model for human-supervised local agent task handoffs."""
import re
from dataclasses import dataclass
from enum import Enum


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DEVELOPER = "developer"
    QA_SECURITY = "qa-security"


class AgentTaskStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


ALLOWED_TRANSITIONS: dict[AgentTaskStatus, frozenset[AgentTaskStatus]] = {
    AgentTaskStatus.DRAFT: frozenset({AgentTaskStatus.READY}),
    AgentTaskStatus.READY: frozenset({AgentTaskStatus.IN_PROGRESS}),
    AgentTaskStatus.IN_PROGRESS: frozenset({AgentTaskStatus.REVIEW}),
    AgentTaskStatus.REVIEW: frozenset(
        {AgentTaskStatus.APPROVED, AgentTaskStatus.REJECTED}
    ),
    AgentTaskStatus.APPROVED: frozenset(),
    AgentTaskStatus.REJECTED: frozenset(),
}


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    title: str
    milestone: str
    objective: str
    scope: str
    allowed_paths: tuple[str, ...]
    pass_criteria: str
    restrictions: str
    assigned_role: AgentRole = AgentRole.ORCHESTRATOR
    status: AgentTaskStatus = AgentTaskStatus.DRAFT
    reviewer: str | None = None
    review_notes: str | None = None

    def __post_init__(self) -> None:
        if not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*", self.task_id
        ):
            raise ValueError(
                "task_id must contain only letters, numbers, hyphens, underscores, and dots"
            )
        for field_name in (
            "task_id",
            "title",
            "milestone",
            "objective",
            "scope",
            "pass_criteria",
            "restrictions",
        ):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")
        if not self.allowed_paths:
            raise ValueError("at least one allowed path is required")
        if len(set(self.allowed_paths)) != len(self.allowed_paths):
            raise ValueError("allowed paths must be unique")
        for path in self.allowed_paths:
            if not path.strip():
                raise ValueError("allowed paths must not be empty")
            if path.startswith("/") or "\\" in path:
                raise ValueError("allowed paths must be relative POSIX paths")
            if any(part in {"", ".", ".."} for part in path.split("/")):
                raise ValueError("allowed paths must be normalized and stay in workspace")

    def transition(self, target: AgentTaskStatus) -> "AgentTask":
        if target not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"Invalid task transition: {self.status.value} -> {target.value}")
        return AgentTask(
            task_id=self.task_id,
            title=self.title,
            milestone=self.milestone,
            objective=self.objective,
            scope=self.scope,
            allowed_paths=self.allowed_paths,
            pass_criteria=self.pass_criteria,
            restrictions=self.restrictions,
            assigned_role=self.assigned_role,
            status=target,
            reviewer=self.reviewer,
            review_notes=self.review_notes,
        )

    def reviewed(self, decision: ReviewDecision, reviewer: str, notes: str) -> "AgentTask":
        if not reviewer.strip():
            raise ValueError("human reviewer name is required")
        target = (
            AgentTaskStatus.APPROVED
            if decision is ReviewDecision.APPROVE
            else AgentTaskStatus.REJECTED
        )
        transitioned = self.transition(target)
        return AgentTask(
            task_id=transitioned.task_id,
            title=transitioned.title,
            milestone=transitioned.milestone,
            objective=transitioned.objective,
            scope=transitioned.scope,
            allowed_paths=transitioned.allowed_paths,
            pass_criteria=transitioned.pass_criteria,
            restrictions=transitioned.restrictions,
            assigned_role=transitioned.assigned_role,
            status=transitioned.status,
            reviewer=reviewer.strip(),
            review_notes=notes.strip() or None,
        )


@dataclass(frozen=True)
class ExecutionRecord:
    task_id: str
    assigned_agent: AgentRole
    started_at: str
    status: AgentTaskStatus
    handoff_path: str
    completed_at: str | None = None
    output_references: tuple[str, ...] = ()
    result_summary: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.handoff_path.strip():
            raise ValueError("execution task_id and handoff_path must not be empty")
        if self.status not in {
            AgentTaskStatus.IN_PROGRESS,
            AgentTaskStatus.REVIEW,
            AgentTaskStatus.APPROVED,
            AgentTaskStatus.REJECTED,
        }:
            raise ValueError("execution record status must represent a prepared execution")
        if self.status is AgentTaskStatus.REVIEW and not self.completed_at:
            raise ValueError("review records require a completion timestamp")


ROLE_GUIDANCE: dict[AgentRole, str] = {
    AgentRole.ORCHESTRATOR: (
        "Clarify the approved scope, propose small steps, and report blockers. "
        "Do not edit files or start sub-agents."
    ),
    AgentRole.DEVELOPER: (
        "Implement only the approved task in allowed paths. Do not run commands, "
        "access the network, or change scope. Return a concise diff summary."
    ),
    AgentRole.QA_SECURITY: (
        "Review only the approved scope and allowed paths. Do not edit, execute "
        "commands, access the network, or approve/merge changes. Report evidence."
    ),
}
