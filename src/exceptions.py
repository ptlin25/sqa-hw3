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


class InvalidUsernameError(TodoAppError):
    EMPTY = "username cannot be empty"
    TYPE = "username must be a string"
    TOO_LONG = "username too long"
    def __init__(self, reason):
        super().__init__(f"Invalid username: {reason}")

class InvalidPasswordError(TodoAppError):
    TYPE = "password must be a string"
    TOO_SHORT = "password too short"
    TOO_LONG = "password too long"
    def __init__(self, reason):
        super().__init__(f"Invalid password: {reason}")


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
