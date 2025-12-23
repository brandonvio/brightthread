"""Route53 stack for DNS records."""

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
    aws_route53_targets as targets,
)
from constructs import Construct


class Route53Stack(Stack):
    """Stack for Route53 DNS records.

    Creates DNS records for:
    - Website apex → CloudFront distribution

    Note: API subdomain record is managed by BackendServiceStack.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain_name: str = "brightthread.design",
        cloudfront_distribution: cloudfront.IDistribution = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Route53 hosted zone
        hosted_zone = route53.HostedZone(
            self,
            "HostedZone",
            zone_name=domain_name,
        )

        CfnOutput(
            self,
            "HostedZoneId",
            value=hosted_zone.hosted_zone_id,
            description="Route53 Hosted Zone ID",
            export_name="hosted-zone-id",
        )

        CfnOutput(
            self,
            "NameServersInfo",
            value="Check Route53 console for nameservers for this hosted zone",
            description="To use this domain, update your registrar with the nameservers shown in Route53 console",
            export_name="nameservers-info",
        )

        # Create website subdomain record (apex → CloudFront)
        if cloudfront_distribution:
            route53.ARecord(
                self,
                "WebsiteAliasRecord",
                zone=hosted_zone,
                target=route53.RecordTarget.from_alias(
                    targets.CloudFrontTarget(cloudfront_distribution)
                ),
                record_name=domain_name,  # apex
            )

            CfnOutput(
                self,
                "WebsiteUrl",
                value=f"https://{domain_name}",
                description="Website URL",
                export_name="website-url",
            )

        self.hosted_zone = hosted_zone
