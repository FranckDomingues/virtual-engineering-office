"""Atomic JSON persistence for agent tasks and local execution records."""
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from veo.domain.agent_tasks import (
    AgentRole,
    AgentTask,
    AgentTaskStatus,
    ExecutionRecord,
)


class JsonAgentTaskRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list_tasks(self) -> list[AgentTask]:
        return [self._task_from_json(data) for data in self._load().get("tasks", [])]

    def get_task(self, task_id: str) -> AgentTask | None:
        return next((task for task in self.list_tasks() if task.task_id == task_id), None)

    def save_task(self, task: AgentTask) -> None:
        data = self._load()
        tasks = data.setdefault("tasks", [])
        for index, stored in enumerate(tasks):
            if stored["task_id"] == task.task_id:
                tasks[index] = self._task_to_json(task)
                self._save(data)
                return
        tasks.append(self._task_to_json(task))
        self._save(data)

    def get_execution(self, task_id: str) -> ExecutionRecord | None:
        data = self._load().get("executions", {}).get(task_id)
        return self._execution_from_json(data) if data else None

    def save_execution(self, record: ExecutionRecord) -> None:
        data = self._load()
        executions = data.setdefault("executions", {})
        executions[record.task_id] = self._execution_to_json(record)
        self._save(data)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"tasks": [], "executions": {}}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
            raise TypeError("Invalid agent task store format")
        if not isinstance(data.get("executions", {}), dict):
            raise TypeError("Invalid execution record store format")
        return data

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".agent-tasks-",
                delete=False,
            ) as temp:
                tmp_path = Path(temp.name)
                os.chmod(tmp_path, 0o600)
                json.dump(data, temp, indent=2)
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(tmp_path, self.path)
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()

    @staticmethod
    def _task_to_json(task: AgentTask) -> dict[str, Any]:
        data = asdict(task)
        data["assigned_role"] = task.assigned_role.value
        data["status"] = task.status.value
        return data

    @staticmethod
    def _task_from_json(data: dict[str, Any]) -> AgentTask:
        return AgentTask(
            **{
                **data,
                "allowed_paths": tuple(data["allowed_paths"]),
                "assigned_role": AgentRole(data["assigned_role"]),
                "status": AgentTaskStatus(data["status"]),
            }
        )

    @staticmethod
    def _execution_to_json(record: ExecutionRecord) -> dict[str, Any]:
        data = asdict(record)
        data["assigned_agent"] = record.assigned_agent.value
        data["status"] = record.status.value
        return data

    @staticmethod
    def _execution_from_json(data: dict[str, Any]) -> ExecutionRecord:
        return ExecutionRecord(
            **{
                **data,
                "assigned_agent": AgentRole(data["assigned_agent"]),
                "status": AgentTaskStatus(data["status"]),
                "output_references": tuple(data.get("output_references", ())),
            }
        )
