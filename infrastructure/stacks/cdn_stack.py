"""CDN stack for S3 website bucket and CloudFront distribution."""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct


class CDNStack(Stack):
    """Stack for website S3 bucket and CloudFront distribution.

    This stack creates:
    - S3 bucket for static website hosting
    - CloudFront distribution for global content delivery
    - Configured for single-page application (SPA) routing
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket_name: str = "brightthread-web-233569452394",
        cloudfront_certificate_arn: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for website
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
        )

        # Enable static website hosting with public read access
        website_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[website_bucket.arn_for_objects("*")],
            )
        )

        # Import certificate from us-east-1 (required for CloudFront)
        # Note: Must be passed as parameter since cross-region CloudFormation exports aren't supported
        if not cloudfront_certificate_arn:
            raise ValueError(
                "cloudfront_certificate_arn is required for CDNStack. "
                "This should be the ARN of the ACM certificate from us-east-1."
            )
        certificate = acm.Certificate.from_certificate_arn(
            self,
            "CloudFrontCertificate",
            certificate_arn=cloudfront_certificate_arn,
        )

        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            certificate=certificate,
            domain_names=["brightthread.design", "*.brightthread.design"],
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            # Custom error responses for SPA routing
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
            ],
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        )

        # Outputs
        CfnOutput(
            self,
            "BucketName",
            value=website_bucket.bucket_name,
            description="S3 bucket name for website",
            export_name="website-bucket-name",
        )

        CfnOutput(
            self,
            "BucketArn",
            value=website_bucket.bucket_arn,
            description="S3 bucket ARN",
            export_name="website-bucket-arn",
        )

        CfnOutput(
            self,
            "DistributionDomainName",
            value=distribution.domain_name,
            description="CloudFront distribution domain name",
            export_name="website-distribution-domain",
        )

        CfnOutput(
            self,
            "DistributionId",
            value=distribution.distribution_id,
            description="CloudFront distribution ID",
            export_name="website-distribution-id",
        )

        self.bucket = website_bucket
        self.distribution = distribution
