import pytest
from users import UserService
from exceptions import InvalidUsernameError, InvalidPasswordError


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
        """Happy Path + Business Logic: passwords not saved as plaintext"""
        # Arrange + Act
        user = user_service.sign_up("alice", "password")

        # Assert
        assert user.password_hash != "password"

    def test_empty_username_raises(self, user_service):
        """Invalid Input + Boundary/Edge: username cannot be empty"""
        # Arrange
        # Use user_service fixture
        
        # Act + Assert
        with pytest.raises(InvalidUsernameError) as error:
            user_service.sign_up("", "password")
        assert InvalidUsernameError.EMPTY in str(error.value)
    
    def test_1_character_username_is_valid(self, user_service):
        """Boundary/Edge: 1 character username is valid"""
        # Arrange
        # Use user_service fixture

        # Act
        user = user_service.sign_up("a", "password")

        # Assert
        assert user.username == "a"
        assert user.id is not None
