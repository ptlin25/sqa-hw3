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
        task = task_service.create_task(USER_A, "Task")

        # Assert
        assert task.title == "Task"
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
        task = task_service.create_task(USER_A, "Task")

        # Assert
        assert task.priority == Priority.MEDIUM
        assert task.due_date is None
        assert task.completed is False
        assert task.category == ""


class TestGetTask:
    def test_returns_correct_task(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Task")

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


class TestUpdateTask:
    def test_updates_specified_field(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Old title")

        # Act
        task_service.update_task(USER_A, task.id, title="New title")

        # Assert
        assert task.title == "New title"

    def test_unspecified_fields_are_unchanged(self, task_service):
        """Business Logic: only supplied fields are mutated"""
        # Arrange
        task = task_service.create_task(
            USER_A, 
            "Task", 
            priority=Priority.HIGH, 
            category="work"
        )

        # Act
        task_service.update_task(USER_A, task.id, title="Updated")

        # Assert
        assert task.priority == Priority.HIGH
        assert task.category == "work"

    def test_due_date_can_be_cleared_to_none(self, task_service):
        """Business Logic"""
        # Arrange
        task = task_service.create_task(USER_A, "Task", due_date=datetime(2026, 6, 1))

        # Act
        task_service.update_task(USER_A, task.id, due_date=None)

        # Assert
        assert task.due_date is None

    def test_no_fields_passed_remains_unchanged(self, task_service):
        """Equivalence Class: no fields passed"""
        # Arrange
        due = datetime(2026, 6, 1)
        task = task_service.create_task(
            USER_A, 
            "Task", 
            priority=Priority.HIGH, 
            category="work",
            due_date=due
        )

        # Act
        task_service.update_task(USER_A, task.id)

        # Assert
        assert task.title == "Task"
        assert task.priority == Priority.HIGH
        assert task.category == "work"
        assert task.due_date == due
    
    def test_one_field_passed_changes_one_field(self, task_service):
        """Equivalence Class: one field passed"""
        # Arrange
        due = datetime(2026, 6, 1)
        task = task_service.create_task(
            USER_A, 
            "Task", 
            priority=Priority.HIGH, 
            category="work",
            due_date=due
        )

        # Act
        task_service.update_task(USER_A, task.id, category="grocery")

        # Assert
        assert task.title == "Task"
        assert task.priority == Priority.HIGH
        assert task.category == "grocery"
        assert task.due_date == due
    
    def test_multiple_field_passed_changes_multiple_fields(self, task_service):
        """Equivalence Class: multiple fields passed"""
        # Arrange
        due = datetime(2026, 6, 1)
        task = task_service.create_task(
            USER_A, 
            "Task", 
            priority=Priority.HIGH, 
            category="work",
            due_date=due
        )

        # Act
        task_service.update_task(
            USER_A, 
            task.id, 
            title="Buy milk", 
            category="grocery", 
            priority=Priority.LOW
        )

        # Assert
        assert task.title == "Buy milk"
        assert task.priority == Priority.LOW
        assert task.category == "grocery"
        assert task.due_date == due


class TestDeleteTask:
    def test_task_no_longer_retrievable(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Task")

        # Act
        task_service.delete_task(USER_A, task.id)

        # Assert
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(USER_A, task.id)

    def test_nonexistent_task_raises(self, task_service):
        """Exception Handling"""
        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            task_service.delete_task(USER_A, "bad-id")

    def test_other_users_task_raises(self, task_service):
        """Business Logic: a user cannot delete a task they do not own"""
        # Arrange
        task = task_service.create_task(USER_A, "Private task")

        # Act + Assert
        with pytest.raises(UnauthorizedTaskAccessError):
            task_service.delete_task(USER_B, task.id)
