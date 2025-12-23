"""User management endpoints for BrightThread."""

import uuid

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.models import CreateUserRequest
from auth import AuthenticatedUser
from db.session import get_db_session
from repositories.user_repository import UserRepository
from services.user_models import User
from services.user_service import UserService

router = APIRouter(prefix="/v1/users", tags=["BrightThread Users"])


# =============================================================================
# Response Models (thin wrappers for list responses with counts)
# =============================================================================


class UserListResponse(BaseModel):
    """Response for list of users."""

    users: list[User]
    total: int


# =============================================================================
# Dependency Injection
# =============================================================================


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    """Create UserService with injected dependencies."""
    user_repo = UserRepository(session)
    return UserService(user_repo)


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=UserListResponse)
def list_users(
    auth: AuthenticatedUser,
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """List all users."""
    logger.info("GET /v1/users")

    users = user_service.get_all_users()
    return UserListResponse(users=users, total=len(users))


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: str,
    auth: AuthenticatedUser,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Get user by ID."""
    logger.info(f"GET /v1/users/{user_id}")

    user_uuid = uuid.UUID(user_id)
    return user_service.get_user(user_uuid)


@router.post("", response_model=User, status_code=201)
def create_user(
    request: CreateUserRequest,
    auth: AuthenticatedUser,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Create a new user."""
    logger.info("POST /v1/users")

    return user_service.create_user(
        company_id=request.company_id,
        email=request.email,
        password=request.password,
    )


@router.get("/company/{company_id}", response_model=UserListResponse)
def list_users_by_company(
    company_id: str,
    auth: AuthenticatedUser,
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """List all users for a company."""
    logger.info(f"GET /v1/users/company/{company_id}")

    company_uuid = uuid.UUID(company_id)
    users = user_service.list_users_by_company(company_uuid)
    return UserListResponse(users=users, total=len(users))
