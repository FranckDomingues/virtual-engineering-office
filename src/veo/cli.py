"""Offline CLI. Deliberately lacks network, code execution and agent-autonomy commands."""
import argparse
from pathlib import Path

from veo.adapters.json_repository import JsonWorkRepository
from veo.application.use_cases import OfficeService
from veo.domain.models import WorkItem


def main() -> None:
    parser = argparse.ArgumentParser(prog="veo", description="Virtual Engineering Office")
    parser.add_argument("--db", type=Path, default=Path(".veo/queue.json"))
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("status")
    add = subs.add_parser("add-task")
    for field in ("task-id", "title", "milestone", "objective", "pass-criteria", "out-of-scope"):
        add.add_argument("--" + field, required=True)
    args = parser.parse_args()
    office = OfficeService(JsonWorkRepository(args.db))
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


if __name__ == "__main__":
    main()
