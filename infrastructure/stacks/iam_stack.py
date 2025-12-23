"""IAM roles and policies for Lambda functions."""

import aws_cdk as cdk
from aws_cdk import Fn, Stack, aws_iam as iam
from constructs import Construct


class IAMStack(Stack):
    """Stack for IAM roles and policies.

    Deploys:
    - Lambda execution role with DynamoDB permissions
    - Imports DynamoDB table ARNs from DynamoDBStack via CloudFormation exports
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_role_name: str,
        env: cdk.Environment,
    ) -> None:
        """Initialize IAM stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            lambda_role_name: Name for Lambda execution role
            env: CDK environment (account and region)
        """
        super().__init__(scope, construct_id, env=env)

        # Import DynamoDB table ARNs from CloudFormation exports
        conversations_table_arn = Fn.import_value("BrightThreadConversationsTableArn")
        checkpoints_table_arn = Fn.import_value("BrightThreadCheckpointsTableArn")

        # Lambda execution role
        self.lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            role_name=lambda_role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for BrightThread backend Lambda functions",
        )

        # DynamoDB access policy
        dynamodb_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeTable",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
            ],
            resources=[
                conversations_table_arn,
                checkpoints_table_arn,
                f"{conversations_table_arn}/index/*",
            ],
        )

        self.lambda_role.add_to_policy(dynamodb_policy)

        # Bedrock access policy for AI model invocation
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
            ],
            resources=["*"],
        )

        self.lambda_role.add_to_policy(bedrock_policy)

        # OpenSearch access policy for vector search
        opensearch_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "es:ESHttpGet",
                "es:ESHttpPost",
                "es:ESHttpPut",
                "es:ESHttpDelete",
                "es:ESHttpHead",
            ],
            resources=[
                f"arn:aws:es:{env.region}:{env.account}:domain/brightthread/*",
            ],
        )

        self.lambda_role.add_to_policy(opensearch_policy)

        # CloudFormation Outputs for cross-stack reference
        cdk.CfnOutput(
            self,
            "LambdaRoleArn",
            value=self.lambda_role.role_arn,
            description="Lambda execution role ARN",
            export_name="BrightThreadLambdaRoleArn",
        )

        cdk.CfnOutput(
            self,
            "LambdaRoleName",
            value=self.lambda_role.role_name,
            description="Lambda execution role name",
            export_name="BrightThreadLambdaRoleName",
        )
