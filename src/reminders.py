import uuid
from datetime import datetime
from typing import Protocol

from exceptions import (
    ReminderNotFoundError,
    TaskNotFoundError,
    UnauthorizedTaskAccessError,
)
from models import Reminder, Task
from tasks import TaskService


class ReminderSender(Protocol):
    """Outgoing side-effect interface. Implement this to deliver reminders by
    email, push notification, or any other channel. Tests supply a spy/stub."""

    def send(self, reminder: Reminder, task: Task) -> None: ...


class ReminderService:
    """Manages reminder creation and delivery. Delivery is delegated to an
    injected ReminderSender so tests can observe or suppress the side effect."""

    def __init__(self, task_service: TaskService, sender: ReminderSender) -> None:
        self._task_service = task_service
        self._sender = sender
        self._reminders: dict[str, Reminder] = {}

    def set_reminder(self, user_id: str, task_id: str, remind_at: datetime) -> Reminder:
        # Validates that the task exists and belongs to user_id.
        self._task_service.get_task(user_id, task_id)
        reminder = Reminder(
            id=str(uuid.uuid4()), user_id=user_id, task_id=task_id, remind_at=remind_at
        )
        self._reminders[reminder.id] = reminder
        return reminder

    def remove_reminder(self, user_id: str, reminder_id: str) -> None:
        reminder = self._reminders.get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)
        # Re-validate ownership: user must still own the task.
        self._task_service.get_task(user_id, reminder.task_id)
        del self._reminders[reminder_id]

    def deliver_due_reminders(self, now: datetime) -> list[Reminder]:
        """Send every un-delivered reminder whose time has come and mark it
        delivered so it is not sent again. Returns the list of sent reminders."""
        delivered: list[Reminder] = []
        for reminder in list(self._reminders.values()):
            if reminder.delivered or reminder.remind_at > now:
                continue
            try:
                task = self._task_service.get_task(reminder.user_id, reminder.task_id)
            except (TaskNotFoundError, UnauthorizedTaskAccessError):
                continue
            self._sender.send(reminder, task)
            reminder.delivered = True
            delivered.append(reminder)
        return delivered
