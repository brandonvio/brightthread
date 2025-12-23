"""OIDC stack for GitHub Actions integration."""

from aws_cdk import (
    Stack,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct


class OidcStack(Stack):
    """Stack that sets up OIDC provider and IAM role for GitHub Actions deployment."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        github_repo_owner: str,
        github_repo_name: str,
        role_name: str = "brightthread-github-actions-role",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create OIDC provider for GitHub
        github_oidc_provider = iam.OpenIdConnectProvider(
            self,
            "GitHubOidcProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
        )

        # Create IAM role for GitHub Actions
        github_role = iam.Role(
            self,
            "GitHubActionsRole",
            role_name=role_name,
            assumed_by=iam.OpenIdConnectPrincipal(
                github_oidc_provider,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_repo_owner}/{github_repo_name}:*",
                    },
                },
            ),
        )

        # Add CDK deployment permissions
        github_role.attach_inline_policy(
            iam.Policy(
                self,
                "GitHubActionsPolicy",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["*"],
                        resources=["*"],
                    )
                ],
            )
        )

        # Output the role ARN for GitHub Actions workflow configuration
        CfnOutput(
            self,
            "GitHubActionsRoleArn",
            value=github_role.role_arn,
            description="ARN of the IAM role for GitHub Actions to assume",
            export_name="github-actions-role-arn",
        )

        CfnOutput(
            self,
            "OidcProviderArn",
            value=github_oidc_provider.open_id_connect_provider_arn,
            description="ARN of the GitHub OIDC provider",
            export_name="github-oidc-provider-arn",
        )

        self.role = github_role
        self.oidc_provider = github_oidc_provider
