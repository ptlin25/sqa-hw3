import hashlib
import uuid

from exceptions import (
    EmptyPasswordError,
    EmptyUsernameError,
    InvalidCredentialsError, 
    UserAlreadyExistsError, 
    UserNotFoundError)
from models import User


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    """Manages user accounts. All state is in-memory; no persistence layer."""

    def __init__(self) -> None:
        self._by_username: dict[str, User] = {}
        self._by_id: dict[str, User] = {}

    def sign_up(self, username: str, password: str) -> User:
        if not username:
            raise EmptyUsernameError
        if not password:
            raise EmptyPasswordError
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
