"""OpenSearch stack - Free tier eligible single-node cluster with vector search."""

import aws_cdk as cdk
from aws_cdk import (
    Annotations,
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
)
from constructs import Construct


class OpenSearchStack(Stack):
    """Stack for OpenSearch single-node cluster (free tier eligible).

    Deploys:
    - OpenSearch domain with t3.small.search instance (free tier)
    - Single node, no replicas
    - Public endpoint (no VPC) with IP-based access policy
    - Fine-grained access control with master user
    - k-NN (vector search) enabled by default in OpenSearch 2.x
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain_name: str = "brightthread",
        allowed_ips: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Initialize OpenSearch stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            domain_name: OpenSearch domain name
            allowed_ips: List of CIDR blocks allowed to access OpenSearch
        """
        super().__init__(scope, construct_id, **kwargs)

        # Import Lambda role ARN from IAMStack for access policy
        lambda_role_arn = cdk.Fn.import_value("BrightThreadLambdaRoleArn")

        # Build IP-based access policy conditions
        ip_conditions = []
        for ip_cidr in allowed_ips or []:
            ip_conditions.append(ip_cidr)

        # OpenSearch domain - Free tier eligible
        # Free tier: t3.small.search, 10GB EBS storage (first 12 months)
        # Deployed WITHOUT VPC for public access (protected by fine-grained access control)
        self.domain = opensearch.Domain(
            self,
            "OpenSearchDomain",
            domain_name=domain_name,
            # OpenSearch 2.x supports k-NN (vector search) by default
            version=opensearch.EngineVersion.OPENSEARCH_2_11,
            # Free tier: t3.small.search instance
            capacity=opensearch.CapacityConfig(
                data_node_instance_type="t3.small.search",
                data_nodes=1,
                # No dedicated master nodes for single-node cluster
                master_nodes=0,
                # Multi-AZ with standby disabled (required for t3 instances)
                multi_az_with_standby_enabled=False,
            ),
            # EBS storage - 10GB free tier
            ebs=opensearch.EbsOptions(
                enabled=True,
                volume_size=10,
            ),
            # NO VPC - public endpoint for dev accessibility
            # Security is handled by:
            # 1. Fine-grained access control (username/password)
            # 2. IP-based access policy
            # 3. HTTPS enforcement
            # Zone awareness disabled for single-node
            zone_awareness=opensearch.ZoneAwarenessConfig(
                enabled=False,
            ),
            # Enable fine-grained access control (master user)
            fine_grained_access_control=opensearch.AdvancedSecurityOptions(
                master_user_name="brightthread_admin",
            ),
            # Node-to-node encryption
            node_to_node_encryption=True,
            # Encryption at rest
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True,
            ),
            # Enforce HTTPS
            enforce_https=True,
            # Removal policy for development
            removal_policy=RemovalPolicy.DESTROY,
            # Enable logging
            logging=opensearch.LoggingOptions(
                slow_search_log_enabled=True,
                slow_index_log_enabled=True,
                app_log_enabled=True,
            ),
        )

        # Access policy - allow Lambda role and specified IPs
        # With fine-grained access control, this policy allows access
        # but authentication is still required
        self.domain.add_access_policies(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[
                    iam.ArnPrincipal(lambda_role_arn),
                    iam.AnyPrincipal(),  # Allow any principal (auth enforced by fine-grained access)
                ],
                actions=["es:*"],
                resources=[f"{self.domain.domain_arn}/*"],
                conditions={
                    "IpAddress": {
                        "aws:SourceIp": ip_conditions,
                    }
                } if ip_conditions else None,
            )
        )

        # Acknowledge metadata warnings
        Annotations.of(self).acknowledge_warning(
            "@aws-cdk/core:addConstructMetadataFailed",
            "Known CDK limitation with OpenSearch domain",
        )

        # Outputs
        cdk.CfnOutput(
            self,
            "OpenSearchEndpoint",
            value=self.domain.domain_endpoint,
            description="OpenSearch domain endpoint",
            export_name="BrightThreadOpenSearchEndpoint",
        )

        cdk.CfnOutput(
            self,
            "OpenSearchDomainArn",
            value=self.domain.domain_arn,
            description="OpenSearch domain ARN",
            export_name="BrightThreadOpenSearchDomainArn",
        )
