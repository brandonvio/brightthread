#!/usr/bin/env python3
"""Validate access to the BrightThread OpenSearch instance.

This script:
1. Retrieves OpenSearch credentials from AWS Secrets Manager
2. Connects to the OpenSearch cluster
3. Runs validation queries to check connectivity and k-NN support
4. Reports success or failure with diagnostic information

Usage:
    python validate_opensearch_access.py [--region REGION] [--profile PROFILE]

Environment variables:
    AWS_REGION: AWS region (default: us-west-2)
    AWS_PROFILE: AWS profile to use (default: brightthread)
"""

import argparse
import json
import os
import sys
from typing import Any

import boto3
import requests
from botocore.exceptions import ClientError
from requests.auth import HTTPBasicAuth

DEFAULT_REGION = "us-west-2"
DEFAULT_PROFILE = "brightthread"
OPENSEARCH_ENDPOINT = (
    "vpc-brightthread-deg56yxa4lb57j736szlq6uscm.us-west-2.es.amazonaws.com"
)
SECRET_NAME = "OpenSearchDomainMasterUserD-S6f1350ZLbPO"


def get_boto3_session(profile: str | None, region: str) -> boto3.Session:
    """Create a boto3 session with optional profile."""
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)


def get_secret(session: boto3.Session, secret_id: str) -> dict[str, Any]:
    """Retrieve OpenSearch credentials from Secrets Manager."""
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


def validate_opensearch_connection(
    endpoint: str,
    username: str,
    password: str,
) -> dict[str, Any]:
    """Connect to OpenSearch and run validation queries."""
    results: dict[str, Any] = {
        "connected": False,
        "cluster_name": None,
        "version": None,
        "cluster_health": None,
        "knn_enabled": False,
        "indices": [],
        "error": None,
    }

    base_url = f"https://{endpoint}"
    auth = HTTPBasicAuth(username, password)
    headers = {"Content-Type": "application/json"}

    try:
        # Test basic connectivity and get cluster info
        response = requests.get(base_url, auth=auth, headers=headers, timeout=10)
        response.raise_for_status()
        cluster_info = response.json()
        results["connected"] = True
        results["cluster_name"] = cluster_info.get("cluster_name")
        results["version"] = cluster_info.get("version", {}).get("number")

        # Get cluster health
        health_response = requests.get(
            f"{base_url}/_cluster/health", auth=auth, headers=headers, timeout=10
        )
        health_response.raise_for_status()
        health = health_response.json()
        results["cluster_health"] = health.get("status")

        # Check if k-NN plugin is available
        plugins_response = requests.get(
            f"{base_url}/_cat/plugins?format=json",
            auth=auth,
            headers=headers,
            timeout=10,
        )
        plugins_response.raise_for_status()
        plugins = plugins_response.json()
        results["knn_enabled"] = any(
            "knn" in plugin.get("component", "").lower() for plugin in plugins
        )

        # List indices
        indices_response = requests.get(
            f"{base_url}/_cat/indices?format=json",
            auth=auth,
            headers=headers,
            timeout=10,
        )
        indices_response.raise_for_status()
        indices = indices_response.json()
        results["indices"] = [idx.get("index") for idx in indices if idx.get("index")]

    except requests.exceptions.ConnectionError as e:
        results["error"] = f"Connection failed: {e}"
    except requests.exceptions.Timeout:
        results["error"] = "Connection timed out"
    except requests.exceptions.HTTPError as e:
        results["error"] = f"HTTP error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        results["error"] = f"Unexpected error: {e}"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate access to BrightThread OpenSearch instance"
    )
    parser.add_argument(
        "--endpoint",
        default=OPENSEARCH_ENDPOINT,
        help=f"OpenSearch endpoint (default: {OPENSEARCH_ENDPOINT})",
    )
    parser.add_argument(
        "--region",
        default=DEFAULT_REGION,
        help=f"AWS region (default: {DEFAULT_REGION})",
    )
    parser.add_argument(
        "--profile",
        default=os.environ.get("AWS_PROFILE", DEFAULT_PROFILE),
        help=f"AWS profile (default: {DEFAULT_PROFILE})",
    )
    args = parser.parse_args()

    print("BrightThread OpenSearch Access Validator")
    print("=" * 45)

    session = get_boto3_session(args.profile, args.region)

    print(f"\n      Region: {args.region}")
    print(f"      Profile: {args.profile}")
    print(f"      Endpoint: {args.endpoint}")

    # Step 1: Get credentials from Secrets Manager
    print("\n[1/2] Retrieving credentials from Secrets Manager...")
    print(f"      Secret: {SECRET_NAME}")

    try:
        secret = get_secret(session, SECRET_NAME)
        print("      Status: OK")
        print(f"      Username: {secret.get('username', 'unknown')}")
    except RuntimeError as e:
        print(f"      Status: FAILED - {e}")
        return 1

    # Step 2: Validate OpenSearch connection
    print("\n[2/2] Validating OpenSearch connection...")

    results = validate_opensearch_connection(
        endpoint=args.endpoint,
        username=secret["username"],
        password=secret["password"],
    )

    # Report results
    print("\n" + "=" * 45)
    print("Results:")
    print("=" * 45)

    if results["connected"]:
        print("  Connection:     SUCCESS")
        print(f"  Cluster Name:   {results['cluster_name']}")
        print(f"  Version:        {results['version']}")
        print(f"  Cluster Health: {results['cluster_health']}")
        print(f"  k-NN Enabled:   {results['knn_enabled']}")

        if results["indices"]:
            print(f"  Indices:        {', '.join(results['indices'])}")
        else:
            print("  Indices:        (none)")

        print("\nOpenSearch access validated successfully.")
        return 0
    else:
        print("  Connection: FAILED")
        print(f"  Error:      {results['error']}")
        print("\nTroubleshooting tips:")
        print("  - OpenSearch is in a VPC - direct access requires VPN/bastion")
        print("  - Check security group allows your IP on port 443")
        print("  - Verify credentials are correct in Secrets Manager")
        print("  - Ensure your AWS credentials have Secrets Manager access")
        return 1


if __name__ == "__main__":
    sys.exit(main())
