import hashlib
import uuid

from exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
    InvalidCredentialsError, 
    UserAlreadyExistsError, 
    UserNotFoundError)
from models import User

MIN_USERNAME_LEN = 1
MAX_USERNAME_LEN = 32
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 64


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    """Manages user accounts. All state is in-memory; no persistence layer."""

    def __init__(self) -> None:
        self._by_username: dict[str, User] = {}
        self._by_id: dict[str, User] = {}

    def sign_up(self, username: str, password: str) -> User:
        if not username:
            raise InvalidUsernameError(InvalidUsernameError.EMPTY)
        elif len(username) > MAX_USERNAME_LEN:
            raise InvalidUsernameError(InvalidUsernameError.TOO_LONG)
        
        if len(password) < MIN_PASSWORD_LEN:
            raise InvalidPasswordError(InvalidPasswordError.TOO_SHORT)
        elif len(password) > MAX_PASSWORD_LEN:
            raise InvalidPasswordError(InvalidPasswordError.TOO_LONG)

        if username in self._by_username:
            raise UserAlreadyExistsError(username)
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=_hash(password),
        )
        self._by_username[username] = user
        self._by_id[user.id] = user
        return user

    def log_in(self, username: str, password: str) -> User:
        user = self._by_username.get(username)
        if user is None:
            raise UserNotFoundError(username)
        if user.password_hash != _hash(password):
            raise InvalidCredentialsError(username)
        return user

    def get_by_id(self, user_id: str) -> User:
        user = self._by_id.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
