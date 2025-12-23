"""Infrastructure stack for core resources (RDS, S3, etc.)."""

from aws_cdk import (
    Annotations,
    Stack,
    aws_iam as iam,
)
from constructs import Construct


class InfrastructureStack(Stack):
    """Stack for application infrastructure resources.

    This stack contains core infrastructure components:
    - API Gateway CloudWatch Logs role
    - RDS database instances
    - S3 buckets
    - Other persistent storage and data services
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for API Gateway CloudWatch Logs
        api_gateway_logs_role = iam.Role(
            self,
            "APIGatewayCloudWatchLogsRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            description="Role for API Gateway to write CloudWatch Logs",
            role_name="APIGatewayCloudWatchRole",
        )

        # Attach CloudWatch Logs policy
        api_gateway_logs_role.attach_inline_policy(
            iam.Policy(
                self,
                "CloudWatchLogsPolicy",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:DescribeLogGroups",
                            "logs:DescribeLogStreams",
                            "logs:PutLogEvents",
                            "logs:GetLogEvents",
                            "logs:FilterLogEvents",
                        ],
                        resources=["arn:aws:logs:*:*:*"],
                    )
                ],
            )
        )

        # Create custom resource to set API Gateway account settings
        # This sets the CloudWatch role ARN at the account level
        from aws_cdk import custom_resources as cr

        api_gateway_settings = cr.AwsCustomResource(
            self,
            "APIGatewayAccountSettings",
            on_create=cr.AwsSdkCall(
                service="APIGateway",
                action="updateAccount",
                parameters={
                    "patchOperations": [
                        {
                            "op": "replace",
                            "path": "/cloudwatchRoleArn",
                            "value": api_gateway_logs_role.role_arn,
                        }
                    ]
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    "APIGatewayAccountSettings"
                ),
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=["apigateway:PATCH"],
                        resources=["arn:aws:apigateway:*::/account"],
                    ),
                    iam.PolicyStatement(
                        actions=["iam:PassRole"],
                        resources=[api_gateway_logs_role.role_arn],
                    ),
                ]
            ),
        )

        # Acknowledge metadata warning for custom resource service role
        # Access the internal service role and acknowledge on it
        service_role = api_gateway_settings.node.try_find_child("CustomResourcePolicy")
        if service_role:
            Annotations.of(service_role).acknowledge_warning(
                "@aws-cdk/core:addConstructMetadataFailed",
                "Known CDK limitation with fromAwsManagedPolicyName",
            )
        # Also acknowledge at the stack level
        Annotations.of(self).acknowledge_warning(
            "@aws-cdk/core:addConstructMetadataFailed",
            "Known CDK limitation with fromAwsManagedPolicyName in custom resources",
        )
