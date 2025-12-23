"""User repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import User


class UserRepository:
    """Data access layer for users."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[User]:
        """Retrieve all users from database.

        Returns:
            List of all User entities.
        """
        return list(self._session.query(User).order_by(User.email).all())

    def get_by_id(self, user_id: uuid.UUID) -> User:
        """Retrieve a user by its ID.

        Args:
            user_id: UUID of the user.

        Returns:
            User entity.

        Raises:
            NoResultFound: If user does not exist.
        """
        return self._session.query(User).filter(User.id == user_id).one()

    def get_by_email(self, email: str) -> User:
        """Retrieve a user by email address.

        Args:
            email: Email address of the user.

        Returns:
            User entity.

        Raises:
            NoResultFound: If user does not exist.
        """
        return self._session.query(User).filter(User.email == email).one()

    def get_by_company_id(self, company_id: uuid.UUID) -> list[User]:
        """Retrieve all users belonging to a company.

        Args:
            company_id: UUID of the company.

        Returns:
            List of User entities.
        """
        return list(
            self._session.query(User)
            .filter(User.company_id == company_id)
            .order_by(User.email)
            .all()
        )

    def create(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: User entity to create.

        Returns:
            Created User entity.
        """
        self._session.add(user)
        self._session.flush()
        return user

    def count(self) -> int:
        """Count total users in database.

        Returns:
            Number of users.
        """
        return self._session.query(User).count()
