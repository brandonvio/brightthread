"""Company repository for database access."""

import uuid

from sqlalchemy.orm import Session

from db.models import Company


class CompanyRepository:
    """Data access layer for companies."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self._session = session

    def get_all(self) -> list[Company]:
        """Retrieve all companies from database.

        Returns:
            List of all Company entities.
        """
        return list(self._session.query(Company).order_by(Company.name).all())

    def get_by_id(self, company_id: uuid.UUID) -> Company:
        """Retrieve a company by its ID.

        Args:
            company_id: UUID of the company.

        Returns:
            Company entity.

        Raises:
            NoResultFound: If company does not exist.
        """
        return self._session.query(Company).filter(Company.id == company_id).one()

    def count(self) -> int:
        """Count total companies in database.

        Returns:
            Number of companies.
        """
        return self._session.query(Company).count()
