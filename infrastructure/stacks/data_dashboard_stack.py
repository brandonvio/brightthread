"""CloudWatch Dashboard for RDS PostgreSQL and DynamoDB monitoring."""

import aws_cdk as cdk
from aws_cdk import (
    Duration,
    Fn,
    Stack,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct


class DataDashboardStack(Stack):
    """Stack for comprehensive RDS and DynamoDB monitoring dashboard.

    Creates a visually rich CloudWatch dashboard with:
    - RDS PostgreSQL metrics (CPU, connections, IOPS, storage, latency)
    - DynamoDB metrics for both tables (consumed capacity, throttling, latency)
    - Alarms for critical thresholds

    Imports RDS instance identifier and DynamoDB table names from CloudFormation
    exports to avoid hard-coded dependencies.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        conversations_table_name: str,
        checkpoints_table_name: str,
        db_instance_identifier: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize data dashboard stack.

        Args:
            scope: CDK scope
            construct_id: Stack identifier
            conversations_table_name: DynamoDB conversations table name
            checkpoints_table_name: DynamoDB checkpoints table name
            db_instance_identifier: RDS instance identifier (optional, imports from CFN if not provided)
        """
        super().__init__(scope, construct_id, **kwargs)

        # TEMP: Hardcoded value to allow RDSStack destruction
        # TODO: Restore Fn.import_value call after RDSStack is recreated
        if db_instance_identifier is None:
            db_instance_identifier = "placeholder-instance"

        dashboard = cloudwatch.Dashboard(
            self,
            "DataServicesDashboard",
            dashboard_name="brightthread-data-services",
            default_interval=Duration.hours(3),
        )

        # =====================================================================
        # Section Header: RDS PostgreSQL
        # =====================================================================
        dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="# 🐘 RDS PostgreSQL Database\n\nPerformance and health metrics for the BrightThread PostgreSQL instance",
                width=24,
                height=2,
            ),
        )

        # Row 1: RDS KPIs
        dashboard.add_widgets(
            cloudwatch.SingleValueWidget(
                title="CPU Utilization",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="CPUUtilization",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Database Connections",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="DatabaseConnections",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Free Storage (GB)",
                metrics=[
                    cloudwatch.MathExpression(
                        expression="storage / 1073741824",
                        using_metrics={
                            "storage": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="FreeStorageSpace",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="GB",
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Freeable Memory (MB)",
                metrics=[
                    cloudwatch.MathExpression(
                        expression="memory / 1048576",
                        using_metrics={
                            "memory": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="FreeableMemory",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="MB",
                    )
                ],
                width=6,
                height=4,
            ),
        )

        # Row 2: CPU and Memory Over Time
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="CPU Utilization %",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="CPUUtilization",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="CPU %",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="%", min=0, max=100),
            ),
            cloudwatch.GraphWidget(
                title="Memory & Storage",
                left=[
                    cloudwatch.MathExpression(
                        expression="memory / 1048576",
                        using_metrics={
                            "memory": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="FreeableMemory",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="Freeable Memory (MB)",
                        color="#2ca02c",
                    ),
                ],
                right=[
                    cloudwatch.MathExpression(
                        expression="storage / 1073741824",
                        using_metrics={
                            "storage": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="FreeStorageSpace",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="Free Storage (GB)",
                        color="#1f77b4",
                    ),
                ],
                width=12,
                height=6,
            ),
        )

        # Row 3: Database Connections and IOPS
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Database Connections",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="DatabaseConnections",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(1),
                        label="Connections",
                        color="#9467bd",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
            cloudwatch.GraphWidget(
                title="IOPS (Read/Write)",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="ReadIOPS",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Read IOPS",
                        color="#2ca02c",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="WriteIOPS",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Write IOPS",
                        color="#d62728",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="IOPS", min=0),
            ),
        )

        # Row 4: Latency and Throughput
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Read/Write Latency",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="ReadLatency",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Read Latency",
                        color="#1f77b4",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="WriteLatency",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Write Latency",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Seconds", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Network Throughput",
                left=[
                    cloudwatch.MathExpression(
                        expression="receive / 1048576",
                        using_metrics={
                            "receive": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="NetworkReceiveThroughput",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="Receive (MB/s)",
                        color="#2ca02c",
                    ),
                    cloudwatch.MathExpression(
                        expression="transmit / 1048576",
                        using_metrics={
                            "transmit": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="NetworkTransmitThroughput",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="Transmit (MB/s)",
                        color="#d62728",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="MB/s", min=0),
            ),
        )

        # Row 5: Transaction and Queue Metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Disk Queue Depth",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/RDS",
                        metric_name="DiskQueueDepth",
                        dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Queue Depth",
                        color="#e377c2",
                    ),
                ],
                width=12,
                height=5,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Swap Usage",
                left=[
                    cloudwatch.MathExpression(
                        expression="swap / 1048576",
                        using_metrics={
                            "swap": cloudwatch.Metric(
                                namespace="AWS/RDS",
                                metric_name="SwapUsage",
                                dimensions_map={
                                    "DBInstanceIdentifier": db_instance_identifier
                                },
                                statistic="Average",
                                period=Duration.minutes(5),
                            )
                        },
                        label="Swap (MB)",
                        color="#bcbd22",
                    ),
                ],
                width=12,
                height=5,
                left_y_axis=cloudwatch.YAxisProps(label="MB", min=0),
            ),
        )

        # =====================================================================
        # Section Header: DynamoDB
        # =====================================================================
        dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="# ⚡ DynamoDB Tables\n\nMetrics for Conversations and Checkpoints tables (on-demand billing)",
                width=24,
                height=2,
            ),
        )

        # Row 6: DynamoDB KPIs
        dashboard.add_widgets(
            cloudwatch.SingleValueWidget(
                title="Conversations - Read Units (5m)",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Conversations - Write Units (5m)",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedWriteCapacityUnits",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Checkpoints - Read Units (5m)",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
            cloudwatch.SingleValueWidget(
                title="Checkpoints - Write Units (5m)",
                metrics=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedWriteCapacityUnits",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                    )
                ],
                width=6,
                height=4,
            ),
        )

        # Row 7: DynamoDB Consumed Capacity Over Time
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Conversations Table - Consumed Capacity",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Read Units",
                        color="#1f77b4",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedWriteCapacityUnits",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Write Units",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Units", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Checkpoints Table - Consumed Capacity",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Read Units",
                        color="#1f77b4",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedWriteCapacityUnits",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Write Units",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Units", min=0),
            ),
        )

        # Row 8: DynamoDB Latency
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Conversations - Request Latency",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": conversations_table_name,
                            "Operation": "GetItem",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="GetItem",
                        color="#2ca02c",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": conversations_table_name,
                            "Operation": "PutItem",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="PutItem",
                        color="#d62728",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": conversations_table_name,
                            "Operation": "Query",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Query",
                        color="#9467bd",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="ms", min=0),
            ),
            cloudwatch.GraphWidget(
                title="Checkpoints - Request Latency",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": checkpoints_table_name,
                            "Operation": "GetItem",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="GetItem",
                        color="#2ca02c",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": checkpoints_table_name,
                            "Operation": "PutItem",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="PutItem",
                        color="#d62728",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SuccessfulRequestLatency",
                        dimensions_map={
                            "TableName": checkpoints_table_name,
                            "Operation": "Query",
                        },
                        statistic="Average",
                        period=Duration.minutes(5),
                        label="Query",
                        color="#9467bd",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="ms", min=0),
            ),
        )

        # Row 9: DynamoDB Throttling and Errors
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Throttled Requests (Both Tables)",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ThrottledRequests",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Conversations",
                        color="#d62728",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ThrottledRequests",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Checkpoints",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
            cloudwatch.GraphWidget(
                title="System Errors (Both Tables)",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SystemErrors",
                        dimensions_map={"TableName": conversations_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Conversations",
                        color="#d62728",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="SystemErrors",
                        dimensions_map={"TableName": checkpoints_table_name},
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="Checkpoints",
                        color="#ff7f0e",
                    ),
                ],
                width=12,
                height=6,
                left_y_axis=cloudwatch.YAxisProps(label="Count", min=0),
            ),
        )

        # Row 10: DynamoDB Item Count and GSI Metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Conversations GSI - Consumed Capacity",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={
                            "TableName": conversations_table_name,
                            "GlobalSecondaryIndexName": "order-id-index",
                        },
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="order-id-index Read",
                        color="#17becf",
                    ),
                    cloudwatch.Metric(
                        namespace="AWS/DynamoDB",
                        metric_name="ConsumedReadCapacityUnits",
                        dimensions_map={
                            "TableName": conversations_table_name,
                            "GlobalSecondaryIndexName": "user_id-updated_at-index",
                        },
                        statistic="Sum",
                        period=Duration.minutes(5),
                        label="user_id-updated_at-index Read",
                        color="#bcbd22",
                    ),
                ],
                width=24,
                height=5,
                left_y_axis=cloudwatch.YAxisProps(label="Units", min=0),
            ),
        )

        # =====================================================================
        # Alarms Section
        # =====================================================================
        dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown="# 🚨 Alarms\n\nCritical alerts for data services health",
                width=24,
                height=2,
            ),
        )

        # Create RDS Alarms
        cpu_alarm = cloudwatch.Metric(
            namespace="AWS/RDS",
            metric_name="CPUUtilization",
            dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
            statistic="Average",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "RDSCPUAlarm",
            alarm_name="brightthread-rds-cpu-high",
            threshold=80,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        storage_alarm = cloudwatch.Metric(
            namespace="AWS/RDS",
            metric_name="FreeStorageSpace",
            dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
            statistic="Average",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "RDSStorageAlarm",
            alarm_name="brightthread-rds-storage-low",
            threshold=2 * 1024 * 1024 * 1024,  # 2GB
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        connections_alarm = cloudwatch.Metric(
            namespace="AWS/RDS",
            metric_name="DatabaseConnections",
            dimensions_map={"DBInstanceIdentifier": db_instance_identifier},
            statistic="Average",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "RDSConnectionsAlarm",
            alarm_name="brightthread-rds-connections-high",
            threshold=80,  # db.t3.micro has ~87 max connections
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        # Create DynamoDB Alarms
        conversations_throttle_alarm = cloudwatch.Metric(
            namespace="AWS/DynamoDB",
            metric_name="ThrottledRequests",
            dimensions_map={"TableName": conversations_table_name},
            statistic="Sum",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "DynamoDBConversationsThrottleAlarm",
            alarm_name="brightthread-dynamodb-conversations-throttled",
            threshold=1,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        checkpoints_throttle_alarm = cloudwatch.Metric(
            namespace="AWS/DynamoDB",
            metric_name="ThrottledRequests",
            dimensions_map={"TableName": checkpoints_table_name},
            statistic="Sum",
            period=Duration.minutes(5),
        ).create_alarm(
            self,
            "DynamoDBCheckpointsThrottleAlarm",
            alarm_name="brightthread-dynamodb-checkpoints-throttled",
            threshold=1,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        # Alarm Status Widget
        dashboard.add_widgets(
            cloudwatch.AlarmStatusWidget(
                title="Data Services Alarm Status",
                alarms=[
                    cpu_alarm,
                    storage_alarm,
                    connections_alarm,
                    conversations_throttle_alarm,
                    checkpoints_throttle_alarm,
                ],
                width=24,
                height=4,
            ),
        )

        # Output dashboard URL
        cdk.CfnOutput(
            self,
            "DashboardURL",
            value=f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name=brightthread-data-services",
            description="Data Services CloudWatch Dashboard URL",
        )
