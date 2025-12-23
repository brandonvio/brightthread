"""Unit tests for authentication module."""

import base64
import json
import sys
from unittest.mock import MagicMock

import pytest

# Mock FastAPI dependencies before importing auth module
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.security"] = MagicMock()

from src.auth import TokenPayload, decode_bearer_token


def _encode_token(payload: dict) -> str:
    """Helper to create base64-encoded token."""
    json_str = json.dumps(payload)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def test_decode_bearer_token_valid() -> None:
    """Test decoding a valid bearer token."""
    user_id = "019b4460-cc8b-7533-bc75-67d1e47a9f87"
    token = _encode_token({"user_id": user_id})

    credentials = MagicMock()
    credentials.credentials = token

    result = decode_bearer_token(credentials)

    assert isinstance(result, TokenPayload)
    assert result.user_id == user_id


def test_decode_bearer_token_with_whitespace() -> None:
    """Test decoding token with whitespace in JSON."""
    user_id = "test-user-123"
    # JSON with whitespace/newlines
    json_str = f'{{\n  "user_id": "{user_id}"\n}}'
    token = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    credentials = MagicMock()
    credentials.credentials = token

    result = decode_bearer_token(credentials)

    assert result.user_id == user_id


def test_decode_bearer_token_invalid_base64() -> None:
    """Test that invalid base64 raises exception."""
    credentials = MagicMock()
    credentials.credentials = "not-valid-base64!!!"

    with pytest.raises(Exception):
        decode_bearer_token(credentials)


def test_decode_bearer_token_invalid_json() -> None:
    """Test that invalid JSON raises exception."""
    token = base64.b64encode(b"not valid json").decode("utf-8")

    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(Exception):
        decode_bearer_token(credentials)


def test_decode_bearer_token_missing_user_id() -> None:
    """Test that missing user_id raises validation error."""
    token = _encode_token({"other_field": "value"})

    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(Exception):
        decode_bearer_token(credentials)


def test_token_payload_model() -> None:
    """Test TokenPayload pydantic model."""
    payload = TokenPayload(user_id="test-123")
    assert payload.user_id == "test-123"
