"""Unit tests for UserRepository."""

import uuid
from unittest.mock import Mock

import pytest

from db.models import User
from repositories.user_repository import UserRepository


@pytest.fixture
def mock_session() -> Mock:
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def user_repository(mock_session: Mock) -> UserRepository:
    """Create UserRepository with mocked session."""
    return UserRepository(mock_session)


def test_get_by_id_success(user_repository: UserRepository, mock_session: Mock) -> None:
    """Test successful retrieval of user by ID."""
    user_id = uuid.uuid4()
    expected_user = User(
        id=user_id,
        company_id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hashed",
    )

    mock_query = Mock()
    mock_query.filter.return_value.one.return_value = expected_user
    mock_session.query.return_value = mock_query

    result = user_repository.get_by_id(user_id)

    assert result == expected_user
    mock_session.query.assert_called_once_with(User)


def test_get_by_email_success(
    user_repository: UserRepository, mock_session: Mock
) -> None:
    """Test successful retrieval of user by email."""
    expected_user = User(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        email="test@example.com",
        password_hash="hashed",
    )

    mock_query = Mock()
    mock_query.filter.return_value.one.return_value = expected_user
    mock_session.query.return_value = mock_query

    result = user_repository.get_by_email("test@example.com")

    assert result == expected_user


def test_create_user_success(
    user_repository: UserRepository, mock_session: Mock
) -> None:
    """Test successful user creation."""
    user = User(
        id=uuid.uuid4(),
        company_id=uuid.uuid4(),
        email="new@example.com",
        password_hash="hashed",
    )

    result = user_repository.create(user)

    assert result == user
    mock_session.add.assert_called_once_with(user)
    mock_session.flush.assert_called_once()


def test_get_all_returns_list(
    user_repository: UserRepository, mock_session: Mock
) -> None:
    """Test get_all returns list of users."""
    users = [
        User(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            email="user1@example.com",
            password_hash="hash1",
        ),
        User(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            email="user2@example.com",
            password_hash="hash2",
        ),
    ]

    mock_query = Mock()
    mock_query.order_by.return_value.all.return_value = users
    mock_session.query.return_value = mock_query

    result = user_repository.get_all()

    assert len(result) == 2
    assert result == users
