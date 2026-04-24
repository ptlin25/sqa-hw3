import pytest
from datetime import datetime
from unittest.mock import Mock
from dataclasses import dataclass

from exceptions import (
    ReminderNotFoundError, 
    TaskNotFoundError, 
    UnauthorizedTaskAccessError,
)
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
    

@dataclass
class Services():
    task_service: FakeTaskService
    reminder_sender: Mock
    reminder_service: ReminderService
    

@pytest.fixture
def services():
    task_service = FakeTaskService()
    reminder_sender = Mock()
    reminder_service = ReminderService(task_service, reminder_sender)
    return Services(
        task_service=task_service,
        reminder_sender=reminder_sender,
        reminder_service=reminder_service
    )



class TestSetReminder:
    def test_returns_reminder_linked_to_task(self, services):
        """Happy Path"""
        # Arrange
        reminder_service = services.reminder_service

        # Act
        reminder = reminder_service.set_reminder(USER_A, TASK_ID, datetime(2026, 6, 1))

        # Assert
        assert reminder.task_id == TASK_ID
        assert reminder.remind_at == datetime(2026, 6, 1)
        assert reminder.id is not None

    def test_nonexistent_task_raises(self, services):
        """Exception Handling"""
        # Arrange
        reminder_service = services.reminder_service
        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            reminder_service.set_reminder(USER_A, "bad-id", datetime(2026, 6, 1))

    def test_unauthorized_task_raises(self, services):
        """Exception Handling: cannot set a reminder on another user's task"""
        # Arrange
        reminder_service = services.reminder_service

        # Act + Assert
        with pytest.raises(UnauthorizedTaskAccessError):
            reminder_service.set_reminder(USER_B, TASK_ID, datetime(2026, 6, 1))


class TestRemoveReminder:
    def test_removed_reminder_raises_on_second_remove(self, services):
        """Happy Path"""
       # Arrange
        reminder_service = services.reminder_service
        reminder = reminder_service.set_reminder(USER_A, TASK_ID, datetime(2026, 6, 1))

        # Act
        reminder_service.remove_reminder(USER_A, reminder.id)

        # Assert
        with pytest.raises(ReminderNotFoundError):
            reminder_service.remove_reminder(USER_A, reminder.id)

    def test_nonexistent_reminder_raises(self, services):
        """Exception Handling"""
       # Arrange
        reminder_service = services.reminder_service
        
        # Act + Assert
        with pytest.raises(ReminderNotFoundError) as exc_info:
            reminder_service.remove_reminder(USER_A, "bad-id")
        assert exc_info.value.reminder_id == "bad-id"

    def test_other_users_reminder_raises(self, services):
        """Exception Handling: a user cannot remove another user's reminder"""
        # Arrange
        reminder_service = services.reminder_service
        reminder = reminder_service.set_reminder(USER_A, TASK_ID, datetime(2026, 6, 1))

        # Act + Assert
        with pytest.raises(UnauthorizedTaskAccessError):
            reminder_service.remove_reminder(USER_B, reminder.id)
