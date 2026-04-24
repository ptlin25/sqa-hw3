import pytest
from datetime import datetime
from unittest.mock import Mock

from exceptions import TaskNotFoundError, UnauthorizedTaskAccessError
from models import Priority, Task
from reminders import ReminderService

USER_A = "user-a"
USER_B = "user-b"
TASK_ID = "task-id"


class FakeTaskService:
    """A fake TaskService prepopulated with one task"""
    def __init__(self):
        task = Task(
            id=TASK_ID,
            user_id=USER_A,
            title="Task",
            description="",
            priority=Priority.MEDIUM,
            due_date=None,
            completed=False,
            category=""
        )
        self.tasks = {TASK_ID: task}

    def get_task(self, user_id: str, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        if task.user_id != user_id:
            raise UnauthorizedTaskAccessError(task_id)
        return task



class TestSetReminder:
    def test_returns_reminder_linked_to_task(self):
        """Happy Path"""
        # Arrange
        task_service = FakeTaskService()
        reminder_sender = Mock()
        reminder_service = ReminderService(task_service, reminder_sender)

        # Act
        reminder = reminder_service.set_reminder(USER_A, TASK_ID, datetime(2026, 6, 1))

        # Assert
        assert reminder.task_id == TASK_ID
        assert reminder.remind_at == datetime(2026, 6, 1)
        assert reminder.id is not None

    def test_nonexistent_task_raises(self):
        """Exception Handling"""
        # Arrange
        task_service = FakeTaskService()
        reminder_sender = Mock()
        reminder_service = ReminderService(task_service, reminder_sender)

        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            reminder_service.set_reminder(USER_A, "bad-id", datetime(2026, 6, 1))

    def test_unauthorized_task_raises(self, task_service, reminder_service):
        """Exception Handling: cannot set a reminder on another user's task"""
        # Arrange
        task = task_service.create_task(USER_A, "Private task")

        # Act + Assert
        with pytest.raises(UnauthorizedTaskAccessError):
            reminder_service.set_reminder(USER_B, task.id, datetime(2026, 6, 1))