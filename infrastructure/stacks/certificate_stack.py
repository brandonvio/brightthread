"""ACM Certificate stack for SSL/TLS certificates."""

from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    CfnOutput,
)
from constructs import Construct


class CertificateStack(Stack):
    """Stack for creating ACM SSL/TLS certificates.

    Creates certificates for:
    - brightthread.design
    - *.brightthread.design

    Uses DNS validation with Route53 for automatic validation.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain_name: str = "brightthread.design",
        hosted_zone_id: str = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference the hosted zone created by Route53Stack
        # For cross-region deployments, hosted_zone_id must be passed explicitly
        if hosted_zone_id:
            hosted_zone = route53.HostedZone.from_hosted_zone_id(
                self,
                "HostedZone",
                hosted_zone_id=hosted_zone_id,
            )
        else:
            # Fallback: try to look up by domain name (only works in same region)
            hosted_zone = route53.HostedZone.from_lookup(
                self,
                "HostedZone",
                domain_name=domain_name,
            )

        # Create certificate for domain and wildcard
        certificate = acm.Certificate(
            self,
            "DomainCertificate",
            domain_name=domain_name,
            subject_alternative_names=[f"*.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hosted_zone),
            certificate_name=f"brightthread-{self.region}",
        )

        # Outputs
        CfnOutput(
            self,
            "CertificateArn",
            value=certificate.certificate_arn,
            description=f"ACM Certificate ARN for {domain_name} in {self.region}",
            export_name=f"brightthread-certificate-arn-{self.region}",
        )

        CfnOutput(
            self,
            "CertificateDomains",
            value=f"{domain_name}, *.{domain_name}",
            description="Domains covered by this certificate",
            export_name=f"brightthread-certificate-domains-{self.region}",
        )

        self.certificate = certificate
