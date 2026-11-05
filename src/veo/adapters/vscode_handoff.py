"""Markdown handoff adapter; it never invokes an AI model or executes commands."""
from pathlib import Path

from veo.application.agent_ports import PromptWriter
from veo.domain.agent_tasks import ROLE_GUIDANCE, AgentTask


class MarkdownPromptWriter(PromptWriter):
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root.resolve()

    def write_prompt(self, task: AgentTask, destination: Path) -> Path:
        target = destination.resolve()
        try:
            target.relative_to(self.workspace_root)
        except ValueError as exc:
            raise ValueError("handoff destination must be inside the workspace") from exc

        resolved_paths: list[str] = []
        for relative in task.allowed_paths:
            candidate = (self.workspace_root / relative).resolve()
            try:
                candidate.relative_to(self.workspace_root)
            except ValueError as exc:
                raise ValueError(f"allowed path escapes workspace: {relative}") from exc
            resolved_paths.append(relative)

        content = "\n".join(
            [
                f"# Task {task.task_id}: {task.title}",
                "",
                "> Human-supervised handoff. This file does not invoke a model, run commands, or grant permissions.",
                "",
                "## Assignment",
                f"- Role: **{task.assigned_role.value}**",
                f"- Task status: `{task.status.value}`",
                f"- Milestone: {task.milestone}",
                "",
                "## Role guidance",
                ROLE_GUIDANCE[task.assigned_role],
                "",
                "## Objective and scope",
                task.objective,
                "",
                task.scope,
                "",
                "## Allowed paths",
                *(f"- `{path}`" for path in resolved_paths),
                "",
                "## PASS criteria",
                task.pass_criteria,
                "",
                "## Restrictions",
                task.restrictions,
                "- Do not execute arbitrary shell commands or access the network.",
                "- Do not access or modify files outside the allowed paths.",
                "- Do not approve, merge, deploy, or expand task scope.",
                "- Return a summary and evidence for human review.",
                "",
                "## Use in VS Code",
                (
                    "Review this prompt, then manually copy it into the approved VS Code Copilot "
                    "chat/agent. No automatic model invocation occurs."
                ),
                "",
            ]
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target
