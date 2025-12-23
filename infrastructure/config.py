"""Infrastructure configuration."""

import os
import subprocess

# GitHub OIDC Configuration
GITHUB_REPO_OWNER = "brandonvio"  # Replace with your GitHub organization
GITHUB_REPO_NAME = "brightthread"  # Replace with your repository name

# IAM Role Configuration
GITHUB_ACTIONS_ROLE_NAME = "brightthread-github-actions-role"

# Stack Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Get current git commit SHA for artifact versioning
try:
    GIT_COMMIT_SHA = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
except (subprocess.CalledProcessError, FileNotFoundError):
    GIT_COMMIT_SHA = "unknown"

# Backend Service Configuration
BACKEND_CONFIG = {
    "function_name": "brightthread-order-support-agent",
    "memory_mb": int(os.getenv("LAMBDA_MEMORY", "512")),
    "timeout_sec": int(os.getenv("LAMBDA_TIMEOUT", "60")),
    "artifact_bucket": os.getenv(
        "DEPLOY_ARTIFACTS_BUCKET", "brightthread-deploy-artifacts"
    ),
    # Artifact key uses current git commit SHA
    "artifact_key": os.getenv(
        "BACKEND_ARTIFACT_KEY",
        f"backend/lambda-code-{GIT_COMMIT_SHA}.zip",
    ),
}

# S3 Deployment Artifacts Configuration
DEPLOY_ARTIFACTS_CONFIG = {
    "bucket_name": BACKEND_CONFIG["artifact_bucket"],
    "removal_policy": "destroy",  # For development, destroy bucket on stack removal
}

# RDS Configuration (Free Tier Eligible)
# Free tier: db.t3.micro, 20GB storage, single-AZ, PostgreSQL
RDS_CONFIG = {
    "db_name": os.getenv("DB_NAME", "brightthread"),
    # Allowed IPs for direct database access (development only)
    "allowed_ips": [
        "72.35.139.106/32",  # Brandon's IP
    ],
}

# DynamoDB Configuration
DYNAMODB_CONFIG = {
    "conversations_table_name": os.getenv(
        "CONVERSATIONS_TABLE_NAME", "brightthread-conversations"
    ),
    "checkpoints_table_name": os.getenv(
        "CHECKPOINTS_TABLE_NAME", "brightthread-checkpoints"
    ),
}

# IAM Configuration
IAM_CONFIG = {
    "lambda_role_name": os.getenv(
        "LAMBDA_ROLE_NAME", "brightthread-backend-lambda-role"
    ),
}

# OpenSearch Configuration (Free Tier Eligible)
# Free tier: t3.small.search, 10GB EBS storage (first 12 months)
OPENSEARCH_CONFIG = {
    "domain_name": os.getenv("OPENSEARCH_DOMAIN_NAME", "brightthread"),
    # Allowed IPs for direct access (development only)
    "allowed_ips": [
        "72.35.139.106/32",  # Brandon's IP
    ],
}
