#!/usr/bin/env python3
"""Validate access to the BrightThread RDS PostgreSQL instance.

This script:
1. Retrieves database credentials from AWS Secrets Manager
2. Connects to the RDS instance
3. Runs a simple query to validate connectivity
4. Reports success or failure with diagnostic information

Usage:
    python validate_rds_access.py [--endpoint ENDPOINT] [--region REGION]

Environment variables:
    AWS_REGION: AWS region (default: us-west-2)
    AWS_PROFILE: AWS profile to use (optional)
"""

import argparse
import json
import os
import sys
from typing import Any

import boto3
import psycopg2
from botocore.exceptions import ClientError


DEFAULT_REGION = "us-west-2"
DEFAULT_DB_NAME = "brightthread"
SECRET_ARN = "arn:aws:secretsmanager:us-west-2:233569452394:secret:brightthread/rds/credentials-PIhuSF"


def get_boto3_session(profile: str | None, region: str) -> boto3.Session:
    """Create a boto3 session with optional profile."""
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)


def get_secret(session: boto3.Session, secret_id: str) -> dict[str, Any]:
    """Retrieve database credentials from Secrets Manager."""
    client = session.client("secretsmanager")

    try:
        response = client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            raise RuntimeError(f"Secret '{secret_id}' not found") from e
        if error_code == "AccessDeniedException":
            raise RuntimeError(f"Access denied to secret '{secret_id}'") from e
        raise RuntimeError(f"Failed to retrieve secret: {e}") from e

    return json.loads(response["SecretString"])


def validate_connection(
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
) -> dict[str, Any]:
    """Connect to PostgreSQL and run validation queries."""
    results: dict[str, Any] = {
        "connected": False,
        "version": None,
        "current_database": None,
        "current_user": None,
        "tables": [],
        "error": None,
    }

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=10,
        )
        results["connected"] = True

        with conn.cursor() as cur:
            # Get PostgreSQL version
            cur.execute("SELECT version()")
            results["version"] = cur.fetchone()[0]

            # Get current database
            cur.execute("SELECT current_database()")
            results["current_database"] = cur.fetchone()[0]

            # Get current user
            cur.execute("SELECT current_user")
            results["current_user"] = cur.fetchone()[0]

            # List tables in public schema
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            results["tables"] = [row[0] for row in cur.fetchall()]

        conn.close()

    except psycopg2.OperationalError as e:
        results["error"] = f"Connection failed: {e}"
    except psycopg2.Error as e:
        results["error"] = f"Database error: {e}"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate access to BrightThread RDS instance"
    )
    parser.add_argument(
        "--endpoint",
        help="RDS endpoint (auto-detected from CloudFormation if not provided)",
    )
    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help=f"AWS region (default: {DEFAULT_REGION})",
    )
    parser.add_argument(
        "--database",
        default=None,
        help="Database name (default: from secret or 'brightthread')",
    )
    args = parser.parse_args()

    print("BrightThread RDS Access Validator")
    print("=" * 40)

    # Get AWS profile from environment
    profile = os.environ.get("AWS_PROFILE")
    session = get_boto3_session(profile, args.region)

    print(f"\n      Region: {args.region}")
    if profile:
        print(f"      Profile: {profile}")

    # Step 1: Get credentials from Secrets Manager
    print("\n[1/3] Retrieving credentials from Secrets Manager...")
    print(f"      Secret: {SECRET_ARN.split(':')[-1]}")

    try:
        secret = get_secret(session, SECRET_ARN)
        print("      Status: OK")
    except RuntimeError as e:
        print(f"      Status: FAILED - {e}")
        return 1

    # Step 2: Get RDS endpoint
    print("\n[2/3] Getting RDS endpoint...")

    endpoint = args.endpoint or secret.get("host")
    if not endpoint:
        print("      Status: FAILED - No host in secret and no --endpoint provided")
        return 1
    print(f"      Host: {endpoint}")

    # Step 3: Validate connection
    database = args.database or secret.get("dbname", DEFAULT_DB_NAME)
    print("\n[3/3] Validating database connection...")
    print(f"      Host: {endpoint}")
    print(f"      Port: {secret.get('port', 5432)}")
    print(f"      Database: {database}")
    print(f"      Username: {secret.get('username', 'unknown')}")

    results = validate_connection(
        host=endpoint,
        port=int(secret.get("port", 5432)),
        database=database,
        username=secret["username"],
        password=secret["password"],
    )

    # Report results
    print("\n" + "=" * 40)
    print("Results:")
    print("=" * 40)

    if results["connected"]:
        print("  Connection: SUCCESS")
        print(f"  PostgreSQL: {results['version']}")
        print(f"  Database:   {results['current_database']}")
        print(f"  User:       {results['current_user']}")

        if results["tables"]:
            print(f"  Tables:     {', '.join(results['tables'])}")
        else:
            print("  Tables:     (none)")

        print("\nRDS access validated successfully.")
        return 0
    else:
        print("  Connection: FAILED")
        print(f"  Error:      {results['error']}")
        print("\nTroubleshooting tips:")
        print("  - Check security group allows your IP on port 5432")
        print("  - Verify RDS instance is publicly accessible")
        print("  - Ensure your AWS credentials have Secrets Manager access")
        return 1


if __name__ == "__main__":
    sys.exit(main())
