"""Use cases for locally orchestrated, human-supervised tasks."""
from pathlib import Path

from veo.application.agent_ports import AgentTaskRepository, Clock, PromptWriter
from veo.domain.agent_tasks import (
    AgentRole,
    AgentTask,
    AgentTaskStatus,
    ExecutionRecord,
    ReviewDecision,
)


class AgentTaskService:
    def __init__(
        self,
        repository: AgentTaskRepository,
        prompt_writer: PromptWriter,
        clock: Clock,
        workspace_root: Path,
    ) -> None:
        self.repository = repository
        self.prompt_writer = prompt_writer
        self.clock = clock
        self.workspace_root = workspace_root.resolve()

    def create_task(
        self,
        *,
        task_id: str,
        title: str,
        milestone: str,
        objective: str,
        scope: str,
        allowed_paths: tuple[str, ...],
        pass_criteria: str,
        restrictions: str,
        role: AgentRole,
    ) -> AgentTask:
        if self.repository.get_task(task_id):
            raise ValueError(f"Duplicate task id: {task_id}")
        task = AgentTask(
            task_id=task_id,
            title=title,
            milestone=milestone,
            objective=objective,
            scope=scope,
            allowed_paths=allowed_paths,
            pass_criteria=pass_criteria,
            restrictions=restrictions,
            assigned_role=role,
        )
        self.repository.save_task(task)
        return task

    def list_tasks(self) -> list[AgentTask]:
        return self.repository.list_tasks()

    def prepare_task(self, task_id: str, destination: Path) -> ExecutionRecord:
        task = self._require_task(task_id)
        if task.status is AgentTaskStatus.DRAFT:
            task = task.transition(AgentTaskStatus.READY)
            self.repository.save_task(task)
        if task.status is not AgentTaskStatus.READY:
            raise ValueError("Only a draft or ready task can be prepared")
        if not destination.is_absolute():
            destination = self.workspace_root / destination
        handoff = self.prompt_writer.write_prompt(task, destination)
        started = self.clock.now()
        record = ExecutionRecord(
            task_id=task.task_id,
            assigned_agent=task.assigned_role,
            started_at=started,
            status=AgentTaskStatus.IN_PROGRESS,
            handoff_path=str(handoff),
        )
        self.repository.save_execution(record)
        self.repository.save_task(task.transition(AgentTaskStatus.IN_PROGRESS))
        return record

    def report_task(
        self,
        task_id: str,
        *,
        result_summary: str,
        output_references: tuple[str, ...],
    ) -> ExecutionRecord:
        task = self._require_task(task_id)
        record = self.repository.get_execution(task_id)
        if task.status is not AgentTaskStatus.IN_PROGRESS or record is None:
            raise ValueError("Task has no in-progress execution to report")
        self._validate_output_references(
            task, output_references, self.workspace_root
        )
        completed = self.clock.now()
        updated_record = ExecutionRecord(
            task_id=record.task_id,
            assigned_agent=record.assigned_agent,
            started_at=record.started_at,
            status=AgentTaskStatus.REVIEW,
            handoff_path=record.handoff_path,
            completed_at=completed,
            output_references=output_references,
            result_summary=result_summary.strip(),
        )
        self.repository.save_execution(updated_record)
        self.repository.save_task(task.transition(AgentTaskStatus.REVIEW))
        return updated_record

    def review_task(
        self,
        task_id: str,
        *,
        decision: ReviewDecision,
        reviewer: str,
        notes: str,
    ) -> AgentTask:
        task = self._require_task(task_id)
        reviewed = task.reviewed(decision, reviewer, notes)
        record = self.repository.get_execution(task_id)
        if record is None or record.status is not AgentTaskStatus.REVIEW:
            raise ValueError("No reported execution is waiting for review")
        self.repository.save_task(reviewed)
        self.repository.save_execution(
            ExecutionRecord(
                task_id=record.task_id,
                assigned_agent=record.assigned_agent,
                started_at=record.started_at,
                status=reviewed.status,
                handoff_path=record.handoff_path,
                completed_at=record.completed_at,
                output_references=record.output_references,
                result_summary=record.result_summary,
            )
        )
        return reviewed

    def _require_task(self, task_id: str) -> AgentTask:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError(f"Unknown task: {task_id}")
        return task

    def _validate_output_references(
        self,
        task: AgentTask,
        output_references: tuple[str, ...],
        workspace_root: Path,
    ) -> None:
        allowed_roots = task.allowed_paths
        for reference in output_references:
            path = Path(reference)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Output reference is outside allowed workspace paths: {reference}")
            resolved = (workspace_root / path).resolve()
            try:
                resolved.relative_to(workspace_root)
            except ValueError as exc:
                raise ValueError(f"Output reference escapes workspace: {reference}") from exc
            authorized = any(
                resolved == (workspace_root / root).resolve()
                or (workspace_root / root).resolve() in resolved.parents
                for root in allowed_roots
            )
            if not authorized:
                raise ValueError(f"Output reference is outside allowed paths: {reference}")
