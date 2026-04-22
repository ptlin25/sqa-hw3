class TodoAppError(Exception):
    """Base class for all application-level errors."""


class UserAlreadyExistsError(TodoAppError):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username already taken: {username!r}")


class UserNotFoundError(TodoAppError):
    # identifier is either a username or a user_id depending on the lookup
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"User not found: {identifier!r}")


class InvalidCredentialsError(TodoAppError):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Invalid credentials for user: {username!r}")


class TaskNotFoundError(TodoAppError):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id!r}")


class UnauthorizedTaskAccessError(TodoAppError):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Unauthorized access to task: {task_id!r}")


class ReminderNotFoundError(TodoAppError):
    def __init__(self, reminder_id: str) -> None:
        self.reminder_id = reminder_id
        super().__init__(f"Reminder not found: {reminder_id!r}")
