import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from exceptions import TaskNotFoundError, UnauthorizedTaskAccessError
from models import Priority, Task

_UNSET: object = object()  # sentinel for "caller did not supply this field"


class SortBy(Enum):
    PRIORITY = "priority"
    DUE_DATE = "due_date"
    COMPLETION = "completion"


class TaskService:
    """CRUD, sorting, and filtering for tasks. Each operation takes a user_id
    so that ownership is checked on every mutating call."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_task(
        self,
        user_id: str,
        title: str,
        *,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        due_date: datetime | None = None,
        category: str = "",
    ) -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
        )
        self._tasks[task.id] = task
        return task

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_task(self, user_id: str, task_id: str) -> Task:
        return self._require_owned(user_id, task_id)

    def list_tasks(
        self,
        user_id: str,
        *,
        sort_by: SortBy | None = None,
        category: str | None = None,
        keyword: str | None = None,
    ) -> list[Task]:
        tasks = [t for t in self._tasks.values() if t.user_id == user_id]

        if category is not None:
            tasks = [t for t in tasks if t.category == category]

        if keyword is not None:
            kw = keyword.lower()
            tasks = [
                t for t in tasks
                if kw in t.title.lower() or kw in t.description.lower()
            ]

        if sort_by is SortBy.PRIORITY:
            # HIGH (3) first, LOW (1) last
            tasks.sort(key=lambda t: t.priority.value, reverse=True)
        elif sort_by is SortBy.DUE_DATE:
            # Earliest due date first; tasks without a due date go last.
            tasks.sort(key=lambda t: (t.due_date is None, t.due_date))
        elif sort_by is SortBy.COMPLETION:
            # Incomplete (False) first, complete (True) last.
            tasks.sort(key=lambda t: t.completed)

        return tasks

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def update_task(
        self,
        user_id: str,
        task_id: str,
        *,
        title: object = _UNSET,
        description: object = _UNSET,
        priority: object = _UNSET,
        due_date: object = _UNSET,
        category: object = _UNSET,
    ) -> Task:
        task = self._require_owned(user_id, task_id)
        if title is not _UNSET:
            task.title = title  # type: ignore[assignment]
        if description is not _UNSET:
            task.description = description  # type: ignore[assignment]
        if priority is not _UNSET:
            task.priority = priority  # type: ignore[assignment]
        if due_date is not _UNSET:
            task.due_date = due_date  # type: ignore[assignment]
        if category is not _UNSET:
            task.category = category  # type: ignore[assignment]
        return task

    def delete_task(self, user_id: str, task_id: str) -> None:
        self._require_owned(user_id, task_id)
        del self._tasks[task_id]

    def mark_complete(self, user_id: str, task_id: str) -> Task:
        task = self._require_owned(user_id, task_id)
        task.completed = True
        return task

    def mark_incomplete(self, user_id: str, task_id: str) -> Task:
        task = self._require_owned(user_id, task_id)
        task.completed = False
        return task

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_owned(self, user_id: str, task_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        if task.user_id != user_id:
            raise UnauthorizedTaskAccessError(task_id)
        return task

    def _get_by_id(self, task_id: str) -> Task | None:
        """Package-internal lookup that skips the ownership check."""
        return self._tasks.get(task_id)
