import pytest
from datetime import datetime

from exceptions import TaskNotFoundError, UnauthorizedTaskAccessError
from models import Priority
from tasks import SortBy

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
        """Equivalence Classes: no fields passed"""
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
        """Equivalence Classes: one field passed"""
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
        """Equivalence Classes: multiple fields passed"""
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


class TestMarkComplete:
    def test_mark_complete(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Buy milk")

        # Act
        task_service.mark_complete(USER_A, task.id)

        # Assert
        assert task.completed is True

    
    def test_mark_complete_nonexistent_task_raises(self, task_service):
        """Exception Handling"""
        # Arrange
        # use task_service fixture

        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            task_service.mark_complete(USER_A, "bad-id")

    def test_mark_incomplete(self, task_service):
        """Happy Path"""
        # Arrange
        task = task_service.create_task(USER_A, "Buy milk")
        task_service.mark_complete(USER_A, task.id)

        # Act
        task_service.mark_incomplete(USER_A, task.id)

        # Assert
        assert task.completed is False

    def test_mark_incomplete_nonexistent_task_raises(self, task_service):
        """Exception Handling"""
        # Arrange
        # use task_service fixture

        # Act + Assert
        with pytest.raises(TaskNotFoundError):
            task_service.mark_incomplete(USER_A, "bad-id")


class TestListTasks:
    def test_sort_by_priority_high_first(self, task_service):
        """Business Logic: sorting by priority should return high priority first"""
        # Arrange
        task_service.create_task(USER_A, "Low", priority=Priority.LOW)
        task_service.create_task(USER_A, "High", priority=Priority.HIGH)
        task_service.create_task(USER_A, "Medium", priority=Priority.MEDIUM)

        # Act
        tasks = task_service.list_tasks(USER_A, sort_by=SortBy.PRIORITY)

        # Assert
        assert [t.priority for t in tasks] == [Priority.HIGH, Priority.MEDIUM, Priority.LOW]

    def test_sort_by_due_date_none_last(self, task_service):
        """Business Logic: tasks without a due date sort after all dated tasks"""
        # Arrange
        no_date = task_service.create_task(USER_A, "No date")
        later   = task_service.create_task(USER_A, "Later",  due_date=datetime(2026, 12, 1))
        sooner  = task_service.create_task(USER_A, "Sooner", due_date=datetime(2026, 1, 1))

        # Act
        tasks = task_service.list_tasks(USER_A, sort_by=SortBy.DUE_DATE)

        # Assert
        assert tasks[0].id == sooner.id
        assert tasks[1].id == later.id
        assert tasks[2].id == no_date.id

    def test_sort_by_completion_incomplete_first(self, task_service):
        """Business Logic: incomplete tasks come before complete tasks"""
        # Arrange
        incomplete = task_service.create_task(USER_A, "Incomplete")
        complete = task_service.create_task(USER_A, "Complete")
        task_service.mark_complete(USER_A, complete.id)
        

        # Act
        tasks = task_service.list_tasks(USER_A, sort_by=SortBy.COMPLETION)

        # Assert
        assert tasks[0].id == incomplete.id
        assert tasks[1].id == complete.id

    def test_filter_by_category(self, task_service):
        """Business Logic: filter by category"""
        # Arrange
        work = task_service.create_task(USER_A, "Report", category="work")
        task_service.create_task(USER_A, "Gym", category="personal")

        # Act
        results = task_service.list_tasks(USER_A, category="work")

        # Assert
        assert len(results) == 1
        assert results[0].id == work.id

    def test_keyword_search_is_case_insensitive(self, task_service):
        """Business Logic: keyword match ignores letter case"""
        # Arrange
        task_service.create_task(USER_A, "Buy Milk")
        task_service.create_task(USER_A, "Buy eggs")

        # Act
        results = task_service.list_tasks(USER_A, keyword="milk")

        # Assert
        assert len(results) == 1
        assert results[0].title == "Buy Milk"

    def test_only_own_tasks_returned(self, task_service):
        """Business Logic: list_tasks must not leak tasks belonging to another user"""
        # Arrange
        task_service.create_task(USER_A, "Alice's task")
        task_service.create_task(USER_B, "Bob's task")

        # Act
        results = task_service.list_tasks(USER_A)

        # Assert
        assert len(results) == 1
        assert results[0].title == "Alice's task"
