import json

import pytest

from veo.adapters.json_repository import JsonWorkRepository
from veo.domain.models import WorkItem


def test_roundtrip(tmp_path):
    repo = JsonWorkRepository(tmp_path / "queue.json")
    item = WorkItem("T-1", "Task", "OFFICE-01", "Do", "PASS", "No deployment")
    repo.add_item(item)
    assert repo.list_items() == [item]
    assert json.loads(repo.path.read_text())[0]["status"] == "backlog"


def test_duplicate_at_adapter(tmp_path):
    repo = JsonWorkRepository(tmp_path / "queue.json")
    item = WorkItem("T-1", "Task", "OFFICE-01", "Do", "PASS", "No deployment")
    repo.add_item(item)
    with pytest.raises(ValueError, match="Duplicate"):
        repo.add_item(item)
