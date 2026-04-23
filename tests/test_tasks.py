import pytest
from datetime import datetime

from exceptions import (
    TaskNotFoundError,
    UnauthorizedTaskAccessError,
)
from models import Priority

USER_A = "user-a"
USER_B = "user-b"


class TestCreateTask:
    def test_returns_task_with_title_and_ownership(self, task_service):
        """Happy Path"""
        # Arrange
        # use task_service fixture

        # Act
        task = task_service.create_task(USER_A, "Buy milk")

        # Assert
        assert task.title == "Buy milk"
        assert task.user_id == USER_A
        assert task.id is not None
    
    def test_all_fields_stored(self, task_service):
        """Happy Path"""
        # Arrange
        due = datetime(2026, 6, 1)

        # Act
        task = task_service.create_task(
            USER_A,
            "Buy milk",
            description="Go to Target",
            priority=Priority.LOW,
            due_date=due,
            category="errands",
        )

        # Assert
        assert task.description == "Go to Target"
        assert task.priority == Priority.LOW
        assert task.due_date == due
        assert task.category == "errands"

    def test_optional_fields_default_correctly(self, task_service):
        """Happy Path"""
        # Arrange + Act
        task = task_service.create_task(USER_A, "Buy milk")

        # Assert
        assert task.priority == Priority.MEDIUM
        assert task.due_date is None
        assert task.completed is False
        assert task.category == ""


class TestGetTask:
    def test_returns_correct_task(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Buy milk")

        # Act
        returned = task_service.get_task(USER_A, task.id)

        # Assert
        assert returned.id == task.id
        assert returned.title == task.title
    
    def test_nonexistent_task_raises(self, task_service):
        """Exception Handling"""
        # Arrange
        # use task_service fixture

        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(USER_A, "bad-id")

    def test_other_users_task_raises(self, task_service):
        """Business Logic"""
        # Arrange
        task = task_service.create_task(USER_A, "Private task")

        # Act + Assert
        with pytest.raises(UnauthorizedTaskAccessError):
            task_service.get_task(USER_B, task.id)
