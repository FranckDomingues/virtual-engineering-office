from pathlib import Path

import pytest

from veo.adapters.agent_json_repository import JsonAgentTaskRepository
from veo.adapters.vscode_handoff import MarkdownPromptWriter
from veo.application.agent_use_cases import AgentTaskService
from veo.domain.agent_tasks import (
    AgentRole,
    AgentTask,
    AgentTaskStatus,
    ExecutionRecord,
    ReviewDecision,
)


class FixedClock:
    def now(self) -> str:
        return "2026-01-02T03:04:05+00:00"


def sample_task(**overrides) -> AgentTask:
    values = {
        "task_id": "OFFICE-02.1",
        "title": "Implement bounded task runtime",
        "milestone": "OFFICE-02.1",
        "objective": "Implement a local supervised workflow",
        "scope": "Only approved source and tests",
        "allowed_paths": ("src/veo", "tests"),
        "pass_criteria": "Deterministic tests pass",
        "restrictions": "No shell, network, credentials, or autonomous approvals",
        "assigned_role": AgentRole.DEVELOPER,
    }
    values.update(overrides)
    return AgentTask(**values)


def service_for(tmp_path: Path) -> AgentTaskService:
    return AgentTaskService(
        JsonAgentTaskRepository(tmp_path / "tasks.json"),
        MarkdownPromptWriter(tmp_path),
        FixedClock(),
        tmp_path,
    )


def test_domain_transitions_and_human_review_required():
    task = sample_task()
    ready = task.transition(AgentTaskStatus.READY)
    in_progress = ready.transition(AgentTaskStatus.IN_PROGRESS)
    review = in_progress.transition(AgentTaskStatus.REVIEW)
    with pytest.raises(ValueError, match="Invalid task transition"):
        task.transition(AgentTaskStatus.APPROVED)
    with pytest.raises(ValueError, match="reviewer"):
        review.reviewed(ReviewDecision.APPROVE, "  ", "")
    approved = review.reviewed(ReviewDecision.APPROVE, "Human reviewer", "Evidence checked")
    assert approved.status is AgentTaskStatus.APPROVED
    assert approved.reviewer == "Human reviewer"
    rejected = review.reviewed(ReviewDecision.REJECT, "Human reviewer", "Needs changes")
    assert rejected.status is AgentTaskStatus.REJECTED


def test_task_id_and_allowed_paths_reject_traversal():
    with pytest.raises(ValueError, match="task_id"):
        sample_task(task_id="../outside")
    with pytest.raises(ValueError, match="normalized"):
        sample_task(allowed_paths=("src/../outside",))


def test_full_lifecycle_persists_prompt_and_review(tmp_path):
    service = service_for(tmp_path)
    created = service.create_task(
        task_id="OFFICE-02.1",
        title="Implement bounded task runtime",
        milestone="OFFICE-02.1",
        objective="Implement a local supervised workflow",
        scope="Only approved source and tests",
        allowed_paths=("src/veo", "tests"),
        pass_criteria="Deterministic tests pass",
        restrictions="No shell or network",
        role=AgentRole.DEVELOPER,
    )
    assert created.status is AgentTaskStatus.DRAFT
    record = service.prepare_task(
        created.task_id, tmp_path / "handoffs/OFFICE-02.1.md"
    )
    assert service.list_tasks()[0].status is AgentTaskStatus.IN_PROGRESS
    prompt = (tmp_path / record.handoff_path).read_text(encoding="utf-8")
    assert "No automatic model invocation" in prompt
    assert "src/veo" in prompt
    reported = service.report_task(
        created.task_id,
        result_summary="Implementation completed manually",
        output_references=("src/veo/application/agent_use_cases.py",),
    )
    assert reported.status is AgentTaskStatus.REVIEW
    approved = service.review_task(
        created.task_id,
        decision=ReviewDecision.APPROVE,
        reviewer="Local human",
        notes="Reviewed the diff and tests",
    )
    assert approved.status is AgentTaskStatus.APPROVED
    repo = JsonAgentTaskRepository(tmp_path / "tasks.json")
    assert repo.get_task(created.task_id) == approved
    assert repo.get_execution(created.task_id).status is AgentTaskStatus.APPROVED
    assert (tmp_path / "tasks.json").stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError, match="Invalid task transition"):
        service.review_task(
            created.task_id,
            decision=ReviewDecision.APPROVE,
            reviewer="Second reviewer",
            notes="No duplicate review",
        )


def test_report_rejects_paths_outside_scope_and_symlink_escape(tmp_path):
    service = service_for(tmp_path)
    service.create_task(
        task_id="SAFE-1",
        title="Bounded change",
        milestone="M1",
        objective="Work inside src",
        scope="Only src/veo",
        allowed_paths=("src/veo",),
        pass_criteria="Pass",
        restrictions="No commands",
        role=AgentRole.DEVELOPER,
    )
    service.prepare_task("SAFE-1", tmp_path / "handoffs/SAFE-1.md")
    with pytest.raises(ValueError, match="outside allowed"):
        service.report_task("SAFE-1", result_summary="x", output_references=("README.md",))

    external = tmp_path.parent / "outside"
    external.mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "veo").symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes workspace"):
        service.report_task(
            "SAFE-1",
            result_summary="x",
            output_references=("src/veo/secret.txt",),
        )


def test_review_requires_reported_execution_without_partial_task_write(tmp_path):
    service = service_for(tmp_path)
    task = service.create_task(
        task_id="SAFE-2",
        title="Bounded change",
        milestone="M1",
        objective="Work inside src",
        scope="Only src/veo",
        allowed_paths=("src/veo",),
        pass_criteria="Pass",
        restrictions="No commands",
        role=AgentRole.DEVELOPER,
    )
    repo = JsonAgentTaskRepository(tmp_path / "tasks.json")
    review_task = task
    for status in (
        AgentTaskStatus.READY,
        AgentTaskStatus.IN_PROGRESS,
        AgentTaskStatus.REVIEW,
    ):
        review_task = review_task.transition(status)
    repo.save_task(review_task)
    with pytest.raises(ValueError, match="waiting for review"):
        service.review_task(
            "SAFE-2",
            decision=ReviewDecision.APPROVE,
            reviewer="Human",
            notes="",
        )
    assert repo.get_task("SAFE-2").status is AgentTaskStatus.REVIEW


def test_execution_record_requires_valid_state():
    with pytest.raises(ValueError, match="prepared execution"):
        ExecutionRecord(
            "T-1",
            AgentRole.DEVELOPER,
            "now",
            AgentTaskStatus.DRAFT,
            "handoffs/T-1.md",
        )
