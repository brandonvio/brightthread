"""RDS PostgreSQL stack - Free tier eligible."""

import aws_cdk as cdk
from aws_cdk import (
    Annotations,
    Duration,
    RemovalPolicy,
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
)
from constructs import Construct


class RDSStack(Stack):
    """Stack for PostgreSQL RDS instance (free tier eligible).

    Deploys:
    - PostgreSQL RDS instance (db.t3.micro, 20GB gp2)
    - Secrets Manager secret for database credentials
    - Security group for database access
    - Uses default VPC for simplicity
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        db_name: str = "brightthread",
        allowed_ips: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Initialize RDS stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            db_name: Database name to create
            allowed_ips: List of CIDR blocks allowed to access RDS (e.g., ["1.2.3.4/32"])
        """
        super().__init__(scope, construct_id, **kwargs)

        # Use default VPC
        vpc = ec2.Vpc.from_lookup(
            self,
            "DefaultVPC",
            is_default=True,
        )

        # Security group for RDS - allows inbound PostgreSQL from Lambda
        self.db_security_group = ec2.SecurityGroup(
            self,
            "RDSSecurityGroup",
            vpc=vpc,
            description="Security group for BrightThread RDS PostgreSQL",
            allow_all_outbound=True,
        )

        # Security group for Lambda to access RDS
        self.lambda_security_group = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=vpc,
            description="Security group for Lambda to access RDS",
            allow_all_outbound=True,
        )

        # Allow Lambda security group to connect to RDS on PostgreSQL port
        # (Used if Lambda is deployed in VPC)
        self.db_security_group.add_ingress_rule(
            peer=self.lambda_security_group,
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from Lambda in VPC",
        )

        # Allow public access for Lambda outside VPC (demo only - protected by password)
        self.db_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from Lambda (outside VPC)",
        )

        # Allow specified IPs to connect to RDS (for development access)
        for ip_cidr in allowed_ips or []:
            self.db_security_group.add_ingress_rule(
                peer=ec2.Peer.ipv4(ip_cidr),
                connection=ec2.Port.tcp(5432),
                description=f"Allow PostgreSQL access from {ip_cidr}",
            )

        # Database credentials stored in Secrets Manager
        self.db_credentials = rds.DatabaseSecret(
            self,
            "DBCredentials",
            username="brightthread_admin",
            secret_name="brightthread/rds/credentials",
        )

        # PostgreSQL RDS instance - Free tier eligible
        # Free tier: db.t3.micro, 20GB storage, single-AZ
        self.db_instance = rds.DatabaseInstance(
            self,
            "PostgresInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_6,
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO,
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC,
            ),
            credentials=rds.Credentials.from_secret(self.db_credentials),
            database_name=db_name,
            # Free tier: 20GB gp2 storage
            allocated_storage=20,
            storage_type=rds.StorageType.GP2,
            # Single-AZ for free tier
            multi_az=False,
            # Allow public access for development (Lambda in same VPC will use internal)
            publicly_accessible=True,
            security_groups=[self.db_security_group],
            # Backup and maintenance
            backup_retention=Duration.days(7),
            delete_automated_backups=True,
            preferred_backup_window="03:00-04:00",
            preferred_maintenance_window="Mon:04:00-Mon:05:00",
            # Performance Insights disabled for free tier
            enable_performance_insights=False,
            # Auto minor version upgrades
            auto_minor_version_upgrade=True,
            # Remove on stack deletion (for development)
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
            # CloudWatch logs
            cloudwatch_logs_exports=["postgresql"],
            cloudwatch_logs_retention=cdk.aws_logs.RetentionDays.ONE_WEEK,
        )

        # Acknowledge metadata warning for log retention custom resource at stack level
        Annotations.of(self).acknowledge_warning(
            "@aws-cdk/core:addConstructMetadataFailed",
            "Known CDK limitation with fromAwsManagedPolicyName in log retention",
        )

        # Store VPC reference for cross-stack use
        self.vpc = vpc

        # Outputs
        cdk.CfnOutput(
            self,
            "DBEndpoint",
            value=self.db_instance.db_instance_endpoint_address,
            description="RDS PostgreSQL endpoint",
            export_name="BrightThreadDBEndpoint",
        )

        cdk.CfnOutput(
            self,
            "DBPort",
            value=self.db_instance.db_instance_endpoint_port,
            description="RDS PostgreSQL port",
            export_name="BrightThreadDBPort",
        )

        cdk.CfnOutput(
            self,
            "DBSecretArn",
            value=self.db_credentials.secret_arn,
            description="Secrets Manager ARN for DB credentials",
            export_name="BrightThreadDBSecretArn",
        )

        cdk.CfnOutput(
            self,
            "DBSecurityGroupId",
            value=self.db_security_group.security_group_id,
            description="RDS security group ID",
            export_name="BrightThreadDBSecurityGroupId",
        )

        cdk.CfnOutput(
            self,
            "LambdaSecurityGroupId",
            value=self.lambda_security_group.security_group_id,
            description="Lambda security group ID for RDS access",
            export_name="BrightThreadLambdaSecurityGroupId",
        )

        cdk.CfnOutput(
            self,
            "DBName",
            value=db_name,
            description="Database name",
            export_name="BrightThreadDBName",
        )

        cdk.CfnOutput(
            self,
            "DBInstanceIdentifier",
            value=self.db_instance.instance_identifier,
            description="RDS instance identifier for CloudWatch metrics",
            export_name="BrightThreadDBInstanceIdentifier",
        )
