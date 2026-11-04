from dataclasses import replace

import pytest

from veo.application.use_cases import OfficeService
from veo.domain.models import TaskStatus, WorkItem


class FakeRepository:
    def __init__(self):
        self.items = []
    def list_items(self):
        return list(self.items)
    def add_item(self, item):
        self.items.append(item)


def sample():
    return WorkItem("OFFICE-01.1", "Bootstrap", "OFFICE-01", "Create structure", "Tests pass", "No API calls")


def test_create():
    repo = FakeRepository()
    service = OfficeService(repo)
    service.create_task(sample())
    assert service.list_tasks() == [sample()]


def test_duplicate_rejected():
    service = OfficeService(FakeRepository())
    service.create_task(sample())
    with pytest.raises(ValueError, match="Duplicate"):
        service.create_task(sample())


def test_approval_not_bypassed():
    service = OfficeService(FakeRepository())
    with pytest.raises(ValueError, match="backlog"):
        service.create_task(replace(sample(), status=TaskStatus.APPROVED))


def test_required_scope():
    with pytest.raises(ValueError, match="out_of_scope"):
        replace(sample(), out_of_scope="")
