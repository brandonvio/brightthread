"""User service for user management."""

import uuid

import bcrypt

from repositories.user_repository import UserRepository
from services.user_models import User


class UserService:
    """Business logic for user management."""

    def __init__(self, user_repo: UserRepository) -> None:
        """Initialize user service with required dependencies.

        Args:
            user_repo: Repository for user data access.
        """
        self._user_repo = user_repo

    def get_user(self, user_id: uuid.UUID) -> User:
        """Retrieve a user by ID.

        Args:
            user_id: UUID of the user.

        Returns:
            User model.
        """
        user = self._user_repo.get_by_id(user_id)
        return User.model_validate(user)

    def get_user_by_email(self, email: str) -> User:
        """Retrieve a user by email.

        Args:
            email: Email address of the user.

        Returns:
            User model.
        """
        user = self._user_repo.get_by_email(email)
        return User.model_validate(user)

    def list_users_by_company(self, company_id: uuid.UUID) -> list[User]:
        """List all users belonging to a company.

        Args:
            company_id: UUID of the company.

        Returns:
            List of users.
        """
        users = self._user_repo.get_by_company_id(company_id)
        return [User.model_validate(u) for u in users]

    def create_user(self, company_id: uuid.UUID, email: str, password: str) -> User:
        """Create a new user with hashed password.

        Args:
            company_id: UUID of the company.
            email: Email address.
            password: Plain text password.

        Returns:
            Created user model.
        """
        password_hash = self._hash_password(password)

        from db.models import User as UserDB

        user = UserDB(
            id=uuid.uuid4(),
            company_id=company_id,
            email=email,
            password_hash=password_hash,
        )

        created_user = self._user_repo.create(user)
        return User.model_validate(created_user)

    def get_all_users(self) -> list[User]:
        """Retrieve all users.

        Returns:
            List of all users.
        """
        users = self._user_repo.get_all()
        return [User.model_validate(u) for u in users]

    def verify_password(self, email: str, password: str) -> User | None:
        """Verify user credentials and return user if valid.

        Args:
            email: User email.
            password: Plain text password.

        Returns:
            User model if valid, None if invalid.
        """
        user = self._user_repo.get_by_email(email)
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            return User.model_validate(user)
        return None

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password.

        Returns:
            Hashed password.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
