"""Company service for company management."""

import uuid

from repositories.company_repository import CompanyRepository
from services.company_models import Company


class CompanyService:
    """Business logic for company management."""

    def __init__(self, company_repo: CompanyRepository) -> None:
        """Initialize company service with required dependencies.

        Args:
            company_repo: Repository for company data access.
        """
        self._company_repo = company_repo

    def get_company(self, company_id: uuid.UUID) -> Company:
        """Retrieve a company by ID.

        Args:
            company_id: UUID of the company.

        Returns:
            Company model.
        """
        company = self._company_repo.get_by_id(company_id)
        return Company.model_validate(company)

    def list_companies(self) -> list[Company]:
        """List all companies.

        Returns:
            List of all companies.
        """
        companies = self._company_repo.get_all()
        return [Company.model_validate(c) for c in companies]

    def create_company(self, name: str) -> Company:
        """Create a new company.

        Args:
            name: Company name.

        Returns:
            Created company model.
        """
        from db.models import Company as CompanyDB

        company = CompanyDB(
            id=uuid.uuid4(),
            name=name,
        )

        created_company = self._company_repo.create(company)
        return Company.model_validate(created_company)

    def count_companies(self) -> int:
        """Count total companies.

        Returns:
            Number of companies.
        """
        return self._company_repo.count()
