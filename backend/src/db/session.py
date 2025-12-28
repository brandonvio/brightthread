"""Database session management."""

import json
import os
from collections.abc import Generator
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


@lru_cache
def get_database_url() -> str:
    """Build DATABASE_URL from environment variables and Secrets Manager.

    For local development: Uses DATABASE_URL environment variable directly.
    For Lambda: Fetches credentials from Secrets Manager and constructs URL
    from DB_HOST, DB_PORT, DB_NAME environment variables.

    Returns:
        PostgreSQL connection string.

    Raises:
        RuntimeError: If neither DATABASE_URL nor DB_SECRET_ARN is configured.
    """
    # For local development with .env
    if url := os.environ.get("DATABASE_URL"):
        return url

    # For Lambda: construct from components
    secret_arn = os.environ.get("DB_SECRET_ARN")
    if not secret_arn:
        raise RuntimeError("Neither DATABASE_URL nor DB_SECRET_ARN configured")

    # Fetch credentials from Secrets Manager
    import boto3

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])

    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]

    raise RuntimeError(
        f"Database URL: {secret['username']}:{secret['password']}@{host}:{port}/{db_name}"
    )
    url = f"postgresql://{secret['username']}:{secret['password']}@{host}:{port}/{db_name}"
    print(f"Database URL: {url}")
    return url


def _get_engine():
    """Create SQLAlchemy engine lazily."""
    try:
        return create_engine(get_database_url())
    except RuntimeError:
        return None


def _get_session_local():
    """Create sessionmaker lazily."""
    engine = _get_engine()
    return sessionmaker(bind=engine) if engine else None


def get_db_session() -> Generator[Session, None, None]:
    """Provide database session for dependency injection.

    Commits the transaction on successful request completion.
    Rolls back on exception.

    Yields:
        SQLAlchemy session.

    Raises:
        RuntimeError: If DATABASE_URL is not configured.
    """
    session_local = _get_session_local()
    if session_local is None:
        raise RuntimeError("DATABASE_URL not configured")
    session = session_local()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
