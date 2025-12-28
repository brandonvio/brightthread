"""Backend service stack for FastAPI Lambda and API Gateway."""

import os

import aws_cdk as cdk
from aws_cdk import (
    Annotations,
    Duration,
    Fn,
    Stack,
    aws_apigateway as apigateway,
    aws_certificatemanager as acm,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

# Hardcoded to avoid cross-stack dependencies
HOSTED_ZONE_ID = "Z09464061UA1TPI1KPH87"
DOMAIN_NAME = "brightthread.design"


class BackendServiceStack(Stack):
    """Stack for BrightThread Order Support Agent backend.

    Deploys:
    - Lambda function for FastAPI application
    - API Gateway with proxy integration
    - IAM execution role with CloudWatch logs access and RDS permissions
    - CloudWatch log group with retention policy

    Database configuration is imported from RDSStack CloudFormation exports.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        artifact_bucket_name: str,
        artifact_key: str,
        function_name: str = "brightthread-order-support-agent",
        memory_mb: int = 512,
        timeout_sec: int = 60,
        **kwargs,
    ) -> None:
        """Initialize backend service stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            artifact_bucket_name: S3 bucket containing Lambda code
            artifact_key: S3 key to Lambda deployment package
            function_name: Lambda function name
            memory_mb: Lambda memory allocation
            timeout_sec: Lambda timeout in seconds
        """
        super().__init__(scope, construct_id, **kwargs)

        # TEMP: Hardcoded values to allow RDSStack destruction
        # TODO: Restore Fn.import_value calls after RDSStack is recreated
        db_secret_arn = "arn:aws:secretsmanager:us-west-2:PLACEHOLDER:secret:placeholder"
        db_host = "placeholder.rds.amazonaws.com"
        db_port = "5432"
        db_name = "brightthread"

        bedrock_model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

        # Import DynamoDB table names from CloudFormation exports
        conversations_table_name = Fn.import_value("BrightThreadConversationsTableName")
        checkpoints_table_name = Fn.import_value("BrightThreadCheckpointsTableName")

        # Reference deployment artifact bucket
        artifact_bucket = s3.Bucket.from_bucket_name(
            self,
            "ArtifactBucket",
            artifact_bucket_name,
        )

        # Acknowledge S3 objectVersion warning at stack level
        Annotations.of(self).acknowledge_warning(
            "@aws-cdk/aws-lambda:codeFromBucketObjectVersionNotSpecified",
            "Artifact key includes git commit SHA for immutable versioning",
        )

        # CloudWatch log group for Lambda
        log_group = logs.LogGroup(
            self,
            "LambdaLogGroup",
            log_group_name=f"/aws/lambda/{function_name}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Import IAM role from IAMStack
        role_arn = Fn.import_value("BrightThreadLambdaRoleArn")
        execution_role = iam.Role.from_role_arn(
            self,
            "LambdaExecutionRole",
            role_arn=role_arn,
            mutable=True,
        )

        # Grant CloudWatch Logs write access
        log_group.grant_write(execution_role)

        # Acknowledge metadata warning at stack level
        Annotations.of(self).acknowledge_warning(
            "@aws-cdk/core:addMethodMetadataFailed",
            "Known CDK limitation with fromAwsManagedPolicyName",
        )

        # Grant Secrets Manager read access for DB credentials
        db_secret = secretsmanager.Secret.from_secret_complete_arn(
            self,
            "DBSecret",
            secret_complete_arn=db_secret_arn,
        )
        db_secret.grant_read(execution_role)

        # Build environment variables
        # Note: AWS_REGION is automatically set by Lambda runtime
        lambda_env: dict[str, str] = {
            "LOG_LEVEL": "INFO",
            "BEDROCK_MODEL_ID": bedrock_model_id,
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
            "DATABASE_URL": os.environ["DATABASE_URL"],
            "DB_SECRET_ARN": db_secret_arn,
            "DB_HOST": db_host,
            "DB_PORT": db_port,
            "DB_NAME": db_name,
            "CONVERSATIONS_TABLE_NAME": conversations_table_name,
            "CHECKPOINTS_TABLE_NAME": checkpoints_table_name,
            # LangSmith tracing configuration
            "LANGSMITH_TRACING": "true",
            "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com",
            "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY", ""),
            "LANGSMITH_PROJECT": "brightthread-aws",
        }

        # Lambda function from S3 artifact
        lambda_function = lambda_.Function(
            self,
            "FastAPIFunction",
            function_name=function_name,
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="main.lambda_handler",
            code=lambda_.Code.from_bucket(
                artifact_bucket,
                artifact_key,
            ),
            role=execution_role,
            memory_size=memory_mb,
            timeout=Duration.seconds(timeout_sec),
            environment=lambda_env,
            log_group=log_group,
            description="BrightThread Order Support Agent API",
        )

        # API Gateway REST API with Lambda proxy integration
        api = apigateway.RestApi(
            self,
            "OrderSupportAPI",
            rest_api_name="BrightThread Order Support API",
            description="Conversational order support system with policy evaluation",
            deploy=True,
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
        )

        # Integrate root resource with Lambda
        api.root.add_method(
            "ANY",
            apigateway.LambdaIntegration(
                lambda_function,
                proxy=True,
            ),
        )

        # Proxy all sub-paths to Lambda
        api.root.add_proxy(
            default_integration=apigateway.LambdaIntegration(
                lambda_function,
                proxy=True,
            ),
        )

        # Create custom domain name for API Gateway
        cert_arn = cdk.Fn.import_value("brightthread-certificate-arn-us-west-2")
        certificate = acm.Certificate.from_certificate_arn(
            self,
            "ApiCertificate",
            certificate_arn=cert_arn,
        )

        # Create custom domain
        custom_domain = apigateway.DomainName(
            self,
            "ApiCustomDomain",
            domain_name="api.brightthread.design",
            certificate=certificate,
            endpoint_type=apigateway.EndpointType.REGIONAL,
        )

        # Map the custom domain to the API stage
        custom_domain.add_base_path_mapping(
            api,
            base_path="",
            stage=api.deployment_stage,
        )

        # Create Route53 A record for api.brightthread.design
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id=HOSTED_ZONE_ID,
            zone_name=DOMAIN_NAME,
        )

        route53.ARecord(
            self,
            "ApiAliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayDomain(custom_domain)
            ),
            record_name=f"api.{DOMAIN_NAME}",
        )

        # Output API endpoint
        cdk.CfnOutput(
            self,
            "APIEndpoint",
            value=api.url,
            description="BrightThread Order Support API endpoint",
            export_name="BrightThreadAPIEndpoint",
        )

        # Output Lambda function name
        cdk.CfnOutput(
            self,
            "LambdaFunctionName",
            value=lambda_function.function_name,
            description="Lambda function name",
            export_name="BrightThreadLambdaFunctionName",
        )

        # Output Lambda function ARN
        cdk.CfnOutput(
            self,
            "LambdaFunctionArn",
            value=lambda_function.function_arn,
            description="Lambda function ARN",
            export_name="BrightThreadLambdaFunctionArn",
        )

        # Store references for cross-stack use
        self.api_gateway = api
        self.api_custom_domain = custom_domain
        self.lambda_function = lambda_function

        # Create comprehensive CloudWatch Dashboard
        self._create_dashboard(lambda_function, api, function_name)

    def _create_dashboard(
        self,
        lambda_function: lambda_.Function,
        api: apigateway.RestApi,
        function_name: str,
    ) -> cloudwatch.Dashboard:
        """Create a comprehensive CloudWatch dashboard for Lambda monitoring.

        Includes metrics for:
        - Invocations and errors
        - Duration and performance percentiles
        - Concurrent executions
        - Throttling
        - API Gateway integration metrics
        """
        dashboard = cloudwatch.Dashboard(
            self,
            "LambdaDashboard",
            dashboard_name=f"{function_name}-dashboard",
            default_interval=Duration.hours(3),
        )

        # Row 1: Key Performance Indicators (Single Value Widgets)
        dashboard.add_widgets(
            cloudwatch.SingleValueWidget(
                title="Total Invocations (24h)",
                metrics=[
                    lambda_function.metric_invocations(
                        statistic="Sum",
                        period=Duration.hours(24),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Error Rate (24h)",
                metrics=[
                    cloudwatch.MathExpression(
                        expression="(errors / invocations) * 100",
                        using_metrics={
                            "errors": lambda_function.metric_errors(
                                statistic="Sum",
                                period=Duration.hours(24),
                            ),
                            "invocations": lambda_function.metric_invocations(
                                statistic="Sum",
                                period=Duration.hours(24),
                            ),
                        },
                        label="Error %",
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Avg Duration (24h)",
                metrics=[
                    lambda_function.metric_duration(
                        statistic="Average",
                        period=Duration.hours(24),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Throttles (24h)",
                metrics=[
                    lambda_function.metric_throttles(
                        statistic="Sum",
                        period=Duration.hours(24),
                    )
                ],
                width=6,
                height=4,
            ),
        )

        # Row 2: Invocations and Errors Over Time
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Invocations & Errors",
                left=[
                    lambda_function.metric_invocations(
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Invocations",
                        color="#2ca02c",
                    ),
                ],
                right=[
                    lambda_function.metric_errors(
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Errors",
                        color="#d62728",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Invocations", min=0),
                right_y_axis=cloudwatch.YAxisProps(label="Errors", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Success Rate %",
                left=[
                    cloudwatch.MathExpression(
                        expression="100 - (errors / invocations) * 100",
                        using_metrics={
                            "errors": lambda_function.metric_errors(
                                statistic="Sum",
                                period=Duration.minutes(5),
                            ),
                            "invocations": lambda_function.metric_invocations(
                                statistic="Sum",
                                period=Duration.minutes(5),
                            ),
                        },
                        label="Success Rate",
                        color="#1f77b4",
                    )
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="%", min=0, max=100),
            ),
        )

        # Row 3: Duration Metrics (Performance)
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Duration Percentiles",
                left=[
                    lambda_function.metric_duration(
                        statistic="p50",
                        period=Duration.minutes(5),
                        label="p50",
                        color="#2ca02c",
                    ),
                    lambda_function.metric_duration(
                        statistic="p90",
                        period=Duration.minutes(5),
                        label="p90",
                        color="#ff7f0e",
                    ),
                    lambda_function.metric_duration(
                        statistic="p99",
                        period=Duration.minutes(5),
                        label="p99",
                        color="#d62728",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="ms", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Duration Statistics",
                left=[
                    lambda_function.metric_duration(
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Average",
                        color="#1f77b4",
                    ),
                    lambda_function.metric_duration(
                        statistic="Maximum",
                        period=Duration.minutes(5),
                        label="Maximum",
                        color="#d62728",
                    ),
                    lambda_function.metric_duration(
                        statistic="Minimum",
                        period=Duration.minutes(5),
                        label="Minimum",
                        color="#2ca02c",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="ms", min=0),
            ),
        )

        # Row 4: Concurrency and Throttling
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Concurrent Executions",
                left=[
                    lambda_function.metric(
                        metric_name="ConcurrentExecutions",
                        statistic="Maximum",
                        period=Duration.minutes(1),
                        label="Concurrent Executions",
                        color="#9467bd",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Throttles & Provisioned Concurrency",
                left=[
                    lambda_function.metric_throttles(
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Throttles",
                        color="#d62728",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
        )

        # Row 5: API Gateway Metrics
        api_name = api.rest_api_name
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Gateway Requests",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Count",
                        dimensions_map={
                            "ApiName": api_name,
                            "Stage": "prod",
                        },
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Request Count",
                        color="#1f77b4",
                    ),
                ],
                width=8,
                height=6,
            ),
            cloudwatch.GraphWidget(
                title="API Gateway Latency",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Latency",
                        dimensions_map={
                            "ApiName": api_name,
                            "Stage": "prod",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Avg Latency",
                        color="#ff7f0e",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Latency",
                        dimensions_map={
                            "ApiName": api_name,
                            "Stage": "prod",
                        },
                        statistic="p99",
                        period=Duration.minutes(5),
                        label="p99 Latency",
                        color="#d62728",
                    ),
                ],
                width=8,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="ms", min=0),
            ),
            cloudwatch.GraphWidget(
                title="API Gateway Errors",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="4XXError",
                        dimensions_map={
                            "ApiName": api_name,
                            "Stage": "prod",
                        },
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="4XX Errors",
                        color="#ff7f0e",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="5XXError",
                        dimensions_map={
                            "ApiName": api_name,
                            "Stage": "prod",
                        },
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="5XX Errors",
                        color="#d62728",
                    ),
                ],
                width=8,
                height=6,
            ),
        )

        # Row 6: Memory and Cold Starts (Log-based metrics approximation)
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Invocations Heatmap by Hour",
                left=[
                    lambda_function.metric_invocations(
                        statistic="Sum",
                        period=Duration.hours(1),
                        label="Hourly Invocations",
                        color="#17becf",
                    ),
                ],
                width=24,
                height=4,
                view=cloudwatch.GraphWidgetView.BAR,
            ),
        )

        # Row 7: Alarm Status Widget
        # Create alarms for the dashboard
        error_alarm = lambda_function.metric_errors(
            statistic="Sum",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "LambdaErrorAlarm",
            alarm_name=f"{function_name}-errors",
            threshold=5,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        throttle_alarm = lambda_function.metric_throttles(
            statistic="Sum",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "LambdaThrottleAlarm",
            alarm_name=f"{function_name}-throttles",
            threshold=1,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        duration_alarm = lambda_function.metric_duration(
            statistic="p99",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "LambdaDurationAlarm",
            alarm_name=f"{function_name}-duration-p99",
            threshold=50000,  # 50 seconds (Lambda timeout is 60s)
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        dashboard.add_widgets(
            cloudwatch.AlarmStatusWidget(
                title="Alarm Status",
                alarms=[error_alarm, throttle_alarm, duration_alarm],
                width=24,
                height=3,
            ),
        )

        # Output dashboard URL
        cdk.CfnOutput(
            self,
            "DashboardURL",
            value=f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={function_name}-dashboard",
            description="CloudWatch Dashboard URL",
        )

        return dashboard
