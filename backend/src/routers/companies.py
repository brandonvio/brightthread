"""Company management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import CreateCompanyRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.company_repository import CompanyRepository
from services.company_models import Company
from services.company_service import CompanyService

router = APIRouter(prefix="/v1/companies", tags=["BrightThread Companies"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class CompanyListResponse(BaseModel):
    """Response for list of companies."""

    companies: list[Company]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_company_service(session: Session = Depends(get_db_session)) -> CompanyService:
    """Create CompanyService with injected dependencies."""
    company_repo = CompanyRepository(session)
    return CompanyService(company_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=CompanyListResponse)
def list_companies(
    auth: AuthenticatedUser,
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyListResponse:
    """List all companies."""
    logger.info("GET /v1/companies")

    companies = company_service.list_companies()
    return CompanyListResponse(companies=companies, total=len(companies))


@router.get("/{company_id}", response_model=Company)
def get_company(
    company_id: str,
    auth: AuthenticatedUser,
    company_service: CompanyService = Depends(get_company_service),
) -> Company:
    """Get company by ID."""
    logger.info(f"GET /v1/companies/{company_id}")

    company_uuid = uuid.UUID(company_id)
    return company_service.get_company(company_uuid)


@router.post("", response_model=Company, status_code=201)
def create_company(
    request: CreateCompanyRequest,
    auth: AuthenticatedUser,
    company_service: CompanyService = Depends(get_company_service),
) -> Company:
    """Create a new company."""
    logger.info("POST /v1/companies")

    return company_service.create_company(name=request.name)
