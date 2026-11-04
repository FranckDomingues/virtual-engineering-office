"""Ports define collaboration boundaries. Infrastructure implements them."""
from typing import Protocol

from veo.domain.models import WorkItem


class WorkRepository(Protocol):
    def list_items(self) -> list[WorkItem]: ...
    def add_item(self, item: WorkItem) -> None: ...


class ReportWriter(Protocol):
    def write(self, content: str) -> str: ...
