import pytest
from unittest.mock import Mock

from reminders import ReminderSender, ReminderService
from tasks import TaskService
from users import UserService


@pytest.fixture
def user_service():
    return UserService()


@pytest.fixture
def task_service():
    return TaskService()


@pytest.fixture
def sender():
    return Mock(spec=ReminderSender)


@pytest.fixture
def reminder_service(task_service, sender):
    return ReminderService(task_service, sender)
