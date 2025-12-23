"""Authentication endpoints for BrightThread."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db_session
from repositories.user_repository import UserRepository
from services.user_models import User
from services.user_service import UserService

router = APIRouter(prefix="/v1/auth", tags=["BrightThread Auth"])


class LoginRequest(BaseModel):
    """Login request payload."""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response with user data."""

    user: User


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    """Create UserService with injected dependencies."""
    user_repo = UserRepository(session)
    return UserService(user_repo)


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    user_service: UserService = Depends(get_user_service),
) -> LoginResponse:
    """Authenticate user and return user data."""
    logger.info(f"POST /v1/auth/login - email={request.email}")

    user = user_service.verify_password(request.email, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return LoginResponse(user=user)
