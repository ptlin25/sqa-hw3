import pytest
from users import UserService
from exceptions import (
    InvalidCredentialsError,
    InvalidUsernameError,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


@pytest.fixture
def user_service():
    return UserService()


class TestSignUp:
    def test_returns_user_with_correct_username(self, user_service):
        """Happy Path"""
        # Arrange + Act
        user = user_service.sign_up("alice", "password")

        # Assert
        assert user.username == "alice"
        assert user.id is not None

    def test_password_not_stored_as_plaintext(self, user_service):
        """Business Logic: passwords not saved as plaintext"""
        # Arrange + Act
        user = user_service.sign_up("alice", "password")

        # Assert
        assert user.password_hash != "password"

    def test_not_string_username_raises(self, user_service):
        """Invalid Input"""
        # Arrange
        # Use user_service fixture

        # Act + Assert
        with pytest.raises(InvalidUsernameError):
            user_service.sign_up(1, "password")

    def test_empty_username_raises(self, user_service):
        """Boundary/Edge: username cannot be empty"""
        # Arrange
        # Use user_service fixture

        # Act + Assert
        with pytest.raises(InvalidUsernameError):
            user_service.sign_up("", "password")

    def test_1_character_username_is_valid(self, user_service):
        """Boundary/Edge: 1 character username is valid"""
        # Arrange
        # Use user_service fixture

        # Act
        user = user_service.sign_up("a", "password")

        # Assert
        assert user.username == "a"
        assert user.id is not None

    def test_32_character_username_is_valid(self, user_service):
        """Boundary/Edge: 32 character username is valid"""
        # Arrange
        username = "a" * 32

        # Act
        user = user_service.sign_up(username, "password")

        # Assert
        assert user.username == username
        assert user.id is not None

    def test_33_character_username_raises(self, user_service):
        """Boundary/Edge: 33 character username is invalid"""
        # Arrange
        username = "a" * 33

        # Act + Assert
        with pytest.raises(InvalidUsernameError):
            user_service.sign_up(username, "password")

    def test_not_string_password_raises(self, user_service):
        """Invalid Input"""
        # Arrange
        # Use user_service fixture

        # Act + Assert
        with pytest.raises(InvalidPasswordError):
            user_service.sign_up("alice", 1)

    def test_7_character_password_is_valid(self, user_service):
        """Boundary/Edge: 7 character password is invalid"""
        # Arrange
        password = "p" * 7

        # Act + Assert
        with pytest.raises(InvalidPasswordError):
            user_service.sign_up("alice", password)

    def test_8_character_password_is_valid(self, user_service):
        """Boundary/Edge: 8 character password is valid"""
        # Arrange
        password = "p" * 8

        # Act
        user = user_service.sign_up("alice", password)

        # Assert
        assert user.username == "alice"
        assert user.id is not None

    def test_64_character_password_is_valid(self, user_service):
        """Boundary/Edge: 64 character password is valid"""
        # Arrange
        password = "p" * 64

        # Act
        user = user_service.sign_up("alice", password)

        # Assert
        assert user.username == "alice"
        assert user.id is not None

    def test_65_character_password_raises(self, user_service):
        """Boundary/Edge: 65 character password is invalid"""
        # Arrange
        password = "p" * 65

        # Act + Assert
        with pytest.raises(InvalidPasswordError):
            user_service.sign_up("alice", password)

    def test_duplicate_username_raises(self, user_service):
        """Exception Handling"""
        # Arrange
        user_service.sign_up("alice", "password")

        # Act + Assert
        with pytest.raises(UserAlreadyExistsError):
            user_service.sign_up("alice", "other_password")

    def test_two_users_get_distinct_ids(self, user_service):
        """Business Logic"""
        # Arrange + Act
        alice = user_service.sign_up("alice", "password")
        bob = user_service.sign_up("bob", "password")

        # Assert
        assert alice.id != bob.id


class TestLogin:
    def test_correct_credentials_returns_same_user(self, user_service):
        """Happy Path"""
        # Arrange
        signed_up = user_service.sign_up("alice", "password")

        # Act
        logged_in = user_service.log_in("alice", "password")

        # Assert
        assert logged_in.id == signed_up.id
        assert logged_in.username == signed_up.username
    
    def test_wrong_password_raises(self, user_service):
        """Exception Handling"""
        # Arrange
        user_service.sign_up("alice", "correct_password")

        # Act + Assert
        with pytest.raises(InvalidCredentialsError):
            user_service.log_in("alice", "wrong_password")
    
    def test_unknown_username_raises(self, user_service):
        """Exception Handling"""
        # Arrange
        # use user_service fixture

        # Act + Assert
        with pytest.raises(UserNotFoundError):
            user_service.log_in("nonexistent-user", "password")

    def test_not_string_username_raises(self, user_service):
        """Invalid Input"""
        # Arrange
        # use user_service fixture

        # Act + Assert
        with pytest.raises(InvalidUsernameError):
            user_service.log_in(1, "password")
    
    def test_not_string_username_raises(self, user_service):
        """Invalid Input"""
        # Arrange
        # use user_service fixture

        # Act + Assert
        with pytest.raises(InvalidPasswordError):
            user_service.log_in("alice", 1)