"""DynamoDB tables for agent conversation history and LangGraph checkpoints."""

import aws_cdk as cdk
from aws_cdk import RemovalPolicy, Stack, aws_dynamodb as dynamodb
from constructs import Construct


class DynamoDBStack(Stack):
    """Stack for DynamoDB tables used by the order support agent.

    Deploys:
    - Conversations table with GSI on order_id
    - Checkpoints table for LangGraph state persistence
    - Both tables use on-demand billing and TTL
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        conversations_table_name: str,
        checkpoints_table_name: str,
        env: cdk.Environment,
    ) -> None:
        """Initialize DynamoDB stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            conversations_table_name: Name for conversations table
            checkpoints_table_name: Name for checkpoints table
            env: CDK environment (account and region)
        """
        super().__init__(scope, construct_id, env=env)

        # Conversations table - stores conversation metadata
        self.conversations_table = dynamodb.Table(
            self,
            "ConversationsTable",
            table_name=conversations_table_name,
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=False,
        )

        # Global Secondary Index for querying by order_id
        self.conversations_table.add_global_secondary_index(
            index_name="order-id-index",
            partition_key=dynamodb.Attribute(
                name="order_id",
                type=dynamodb.AttributeType.STRING,
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # Global Secondary Index for listing conversations by user, sorted by updated_at
        self.conversations_table.add_global_secondary_index(
            index_name="user_id-updated_at-index",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="updated_at",
                type=dynamodb.AttributeType.STRING,
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # Checkpoints table - stores LangGraph state checkpoints
        # Uses PK/SK schema required by langgraph-checkpoint-amazon-dynamodb package
        self.checkpoints_table = dynamodb.Table(
            self,
            "CheckpointsTable",
            table_name=checkpoints_table_name,
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="expireAt",
            removal_policy=RemovalPolicy.DESTROY,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            point_in_time_recovery=False,
        )

        # CloudFormation Outputs for cross-stack reference
        cdk.CfnOutput(
            self,
            "ConversationsTableName",
            value=self.conversations_table.table_name,
            description="DynamoDB Conversations table name",
            export_name="BrightThreadConversationsTableName",
        )

        cdk.CfnOutput(
            self,
            "ConversationsTableArn",
            value=self.conversations_table.table_arn,
            description="DynamoDB Conversations table ARN",
            export_name="BrightThreadConversationsTableArn",
        )

        cdk.CfnOutput(
            self,
            "CheckpointsTableName",
            value=self.checkpoints_table.table_name,
            description="DynamoDB Checkpoints table name",
            export_name="BrightThreadCheckpointsTableName",
        )

        cdk.CfnOutput(
            self,
            "CheckpointsTableArn",
            value=self.checkpoints_table.table_arn,
            description="DynamoDB Checkpoints table ARN",
            export_name="BrightThreadCheckpointsTableArn",
        )
