#!/usr/bin/env python3
import os

import aws_cdk as cdk

from config import (
    GITHUB_REPO_OWNER,
    GITHUB_REPO_NAME,
    GITHUB_ACTIONS_ROLE_NAME,
    BACKEND_CONFIG,
    RDS_CONFIG,
    DYNAMODB_CONFIG,
    IAM_CONFIG,
    OPENSEARCH_CONFIG,
)
from stacks.oidc_stack import OidcStack
from stacks.infrastructure_stack import InfrastructureStack
from stacks.cdn_stack import CDNStack
from stacks.backend_service_stack import BackendServiceStack
from stacks.route53_stack import Route53Stack
from stacks.certificate_stack import CertificateStack
from stacks.rds_stack import RDSStack
from stacks.dynamodb_stack import DynamoDBStack
from stacks.iam_stack import IAMStack
from stacks.opensearch_stack import OpenSearchStack
from stacks.data_dashboard_stack import DataDashboardStack


app = cdk.App()

env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

OidcStack(
    app,
    "OidcStack",
    github_repo_owner=GITHUB_REPO_OWNER,
    github_repo_name=GITHUB_REPO_NAME,
    role_name=GITHUB_ACTIONS_ROLE_NAME,
    env=env,
)

InfrastructureStack(
    app,
    "InfrastructureStack",
    env=env,
)

# Hosted zone ID from Route53Stack deployment
# Note: Hardcoded to avoid cross-region stack reference issues
HOSTED_ZONE_ID = "Z09464061UA1TPI1KPH87"

# Create ACM certificates in both regions BEFORE CDNStack
# Primary region (us-west-2)
cert_primary = CertificateStack(
    app,
    "CertificateStackPrimary",
    domain_name="brightthread.design",
    hosted_zone_id=HOSTED_ZONE_ID,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-west-2",
    ),
)

# Secondary region (us-east-1) - required for CloudFront
# Must be deployed before CDNStack
cert_us_east_1 = CertificateStack(
    app,
    "CertificateStackUsEast1",
    domain_name="brightthread.design",
    hosted_zone_id=HOSTED_ZONE_ID,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

cdn_stack = CDNStack(
    app,
    "CDNStack",
    cloudfront_certificate_arn="arn:aws:acm:us-east-1:233569452394:certificate/5e9ff4ad-6d84-4505-9603-8192bad76958",
    env=env,
)

# RDS PostgreSQL instance (free tier eligible)
rds_stack = RDSStack(
    app,
    "RDSStack",
    db_name=RDS_CONFIG["db_name"],
    allowed_ips=RDS_CONFIG.get("allowed_ips", []),
    env=env,
)

# DynamoDB tables for agent conversation history
dynamodb_stack = DynamoDBStack(
    app,
    "DynamoDBStack",
    conversations_table_name=DYNAMODB_CONFIG["conversations_table_name"],
    checkpoints_table_name=DYNAMODB_CONFIG["checkpoints_table_name"],
    env=env,
)

# IAM roles for Lambda (imports DynamoDB table ARNs)
iam_stack = IAMStack(
    app,
    "IAMStack",
    lambda_role_name=IAM_CONFIG["lambda_role_name"],
    env=env,
)

# OpenSearch single-node cluster (free tier eligible, vector search enabled)
opensearch_stack = OpenSearchStack(
    app,
    "OpenSearchStack",
    domain_name=OPENSEARCH_CONFIG["domain_name"],
    allowed_ips=OPENSEARCH_CONFIG.get("allowed_ips", []),
    env=env,
)

backend_stack = BackendServiceStack(
    app,
    "BackendServiceStack",
    artifact_bucket_name=BACKEND_CONFIG["artifact_bucket"],
    artifact_key=BACKEND_CONFIG["artifact_key"],
    function_name=BACKEND_CONFIG["function_name"],
    memory_mb=BACKEND_CONFIG["memory_mb"],
    timeout_sec=BACKEND_CONFIG["timeout_sec"],
    # RDS config imported via CloudFormation exports (no stack dependency)
    env=env,
)

route53_stack = Route53Stack(
    app,
    "Route53Stack",
    domain_name="brightthread.design",
    cloudfront_distribution=cdn_stack.distribution,
    # API subdomain DNS is managed by BackendServiceStack (no dependency)
    env=env,
)

# CloudWatch Dashboard for RDS and DynamoDB monitoring
# RDS instance identifier is imported from CloudFormation exports
data_dashboard_stack = DataDashboardStack(
    app,
    "DataDashboardStack",
    conversations_table_name=DYNAMODB_CONFIG["conversations_table_name"],
    checkpoints_table_name=DYNAMODB_CONFIG["checkpoints_table_name"],
    env=env,
)

app.synth()
