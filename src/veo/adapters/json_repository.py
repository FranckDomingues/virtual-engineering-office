"""Local, atomic JSON adapter. Stores no credentials and never invokes external services."""
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from veo.domain.models import TaskStatus, WorkItem


class JsonWorkRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list_items(self) -> list[WorkItem]:
        if not self.path.exists():
            return []
        items = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise TypeError("Invalid work queue format")
        return [WorkItem(**{**item, "status": TaskStatus(item["status"])}) for item in items]

    def add_item(self, item: WorkItem) -> None:
        records = self.list_items()
        if any(record.task_id == item.task_id for record in records):
            raise ValueError("Duplicate task id")
        records.append(item)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement; disk failure may require manual recovery.
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".queue-", delete=False) as temp:
                tmp_path = Path(temp.name)
                os.chmod(tmp_path, 0o600)
                json.dump([asdict(record) for record in records], temp, indent=2)
                temp.flush()
                os.fsync(temp.fileno())
            os.replace(tmp_path, self.path)
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
