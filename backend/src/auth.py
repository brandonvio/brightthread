"""Authentication module for extracting user identity from bearer tokens."""

import base64
import json
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Decoded bearer token payload."""

    user_id: str


security = HTTPBearer()


def decode_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """Decode base64 bearer token and extract user identity.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        TokenPayload with user_id

    Raises:
        HTTPException: If token is invalid or cannot be decoded
    """
    token = credentials.credentials
    decoded_bytes = base64.b64decode(token)
    decoded_str = decoded_bytes.decode("utf-8")
    payload_dict = json.loads(decoded_str)
    return TokenPayload(**payload_dict)


# Type alias for dependency injection
AuthenticatedUser = Annotated[TokenPayload, Depends(decode_bearer_token)]
