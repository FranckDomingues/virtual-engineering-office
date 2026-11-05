"""Offline CLI. Deliberately lacks network, code execution and agent-autonomy commands."""
import argparse
from pathlib import Path

from veo.adapters.agent_json_repository import JsonAgentTaskRepository
from veo.adapters.json_repository import JsonWorkRepository
from veo.adapters.local_clock import SystemClock
from veo.adapters.vscode_handoff import MarkdownPromptWriter
from veo.application.agent_use_cases import AgentTaskService
from veo.application.use_cases import OfficeService
from veo.domain.agent_tasks import AgentRole, ReviewDecision
from veo.domain.models import WorkItem


def main() -> None:
    parser = argparse.ArgumentParser(prog="veo", description="Virtual Engineering Office")
    parser.add_argument("--db", type=Path, default=Path(".veo/queue.json"))
    parser.add_argument("--state", type=Path, default=Path(".veo/agent-tasks.json"))
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("status")
    add = subs.add_parser("add-task")
    for field in ("task-id", "title", "milestone", "objective", "pass-criteria", "out-of-scope"):
        add.add_argument("--" + field, required=True)
    subs.add_parser("tasks", help="List supervised agent tasks")
    task_cmds = subs.add_parser("task", help="Manage supervised agent tasks")
    task_subs = task_cmds.add_subparsers(dest="task_command", required=True)
    create = task_subs.add_parser("create")
    create.add_argument("--task-id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--milestone", required=True)
    create.add_argument("--objective", required=True)
    create.add_argument("--scope", required=True)
    create.add_argument("--allowed-path", action="append", required=True)
    create.add_argument("--pass-criteria", required=True)
    create.add_argument("--restrictions", required=True)
    create.add_argument("--role", choices=[role.value for role in AgentRole], default=AgentRole.ORCHESTRATOR.value)
    prepare = task_subs.add_parser("prepare")
    prepare.add_argument("task_id")
    prepare.add_argument("--output", type=Path)
    report = task_subs.add_parser("report")
    report.add_argument("task_id")
    report.add_argument("--summary", required=True)
    report.add_argument("--output-reference", action="append", default=[])
    review = task_subs.add_parser("review")
    review.add_argument("task_id")
    review.add_argument("--decision", choices=[decision.value for decision in ReviewDecision], required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", default="")
    args = parser.parse_args()
    office = OfficeService(JsonWorkRepository(args.db))
    agent_tasks = AgentTaskService(
        JsonAgentTaskRepository(args.state),
        MarkdownPromptWriter(Path.cwd()),
        SystemClock(),
        Path.cwd(),
    )
    if args.command == "add-task":
        office.create_task(WorkItem(args.task_id, args.title, args.milestone,
                                    args.objective, args.pass_criteria, args.out_of_scope))
        print(f"CREATED: {args.task_id} (backlog, human approval required)")
    elif args.command == "status":
        items = office.list_tasks()
        if not items:
            print("EMPTY: no tasks scheduled; autonomous execution disabled")
        for task in items:
            print(f"{task.task_id}: {task.status.value} | {task.milestone} | {task.title}")
    elif args.command == "tasks":
        tasks = agent_tasks.list_tasks()
        if not tasks:
            print("EMPTY: no supervised tasks")
        for task in tasks:
            print(f"{task.task_id}: {task.status.value} | {task.assigned_role.value} | {task.title}")
    elif args.command == "task":
        if args.task_command == "create":
            task = agent_tasks.create_task(
                task_id=args.task_id,
                title=args.title,
                milestone=args.milestone,
                objective=args.objective,
                scope=args.scope,
                allowed_paths=tuple(args.allowed_path),
                pass_criteria=args.pass_criteria,
                restrictions=args.restrictions,
                role=AgentRole(args.role),
            )
            print(f"CREATED: {task.task_id} (draft; human-supervised)")
        elif args.task_command == "prepare":
            destination = args.output or Path("handoffs") / f"{args.task_id}.md"
            record = agent_tasks.prepare_task(args.task_id, destination)
            print(f"PREPARED: {record.handoff_path}")
            print("No model was invoked; open or copy the Markdown prompt manually in VS Code.")
        elif args.task_command == "report":
            record = agent_tasks.report_task(
                args.task_id,
                result_summary=args.summary,
                output_references=tuple(args.output_reference),
            )
            print(f"REPORTED: {record.task_id} (review required; {record.status.value})")
        elif args.task_command == "review":
            task = agent_tasks.review_task(
                args.task_id,
                decision=ReviewDecision(args.decision),
                reviewer=args.reviewer,
                notes=args.notes,
            )
            print(f"REVIEWED: {task.task_id} ({task.status.value}; reviewer={task.reviewer})")


if __name__ == "__main__":
    main()
