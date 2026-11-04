from veo.application.ports import WorkRepository
from veo.domain.models import TaskStatus, WorkItem


class OfficeService:
    def __init__(self, repository: WorkRepository) -> None:
        self._repository = repository

    def create_task(self, item: WorkItem) -> None:
        if item.status is not TaskStatus.BACKLOG:
            raise ValueError("New tasks must enter backlog and await human review")
        if any(existing.task_id == item.task_id for existing in self._repository.list_items()):
            raise ValueError("Duplicate task id")
        self._repository.add_item(item)

    def list_tasks(self) -> list[WorkItem]:
        return self._repository.list_items()
