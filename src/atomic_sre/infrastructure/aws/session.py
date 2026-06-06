"""AWS session helpers.

This module is part of the Atomic-SRE infrastructure layer, strictly isolating cloud-specific
deployment and resource management logic from the core orchestrator. This separation of
concerns ensures that the AI engine remains agnostic to the underlying AWS environment.
"""

import boto3
from botocore.exceptions import ClientError

from atomic_sre.infrastructure.aws.models import EcsDeploymentConfig


def create_session(config: EcsDeploymentConfig) -> boto3.session.Session:
    """Create a boto3 session."""
    if config.aws_profile:
        return boto3.session.Session(
            profile_name=config.aws_profile,
            region_name=config.aws_region,
        )

    return boto3.session.Session(region_name=config.aws_region)


def get_identity(session: boto3.session.Session) -> dict[str, str]:
    """Fetch the current AWS identity."""
    client = session.client("sts")
    try:
        response = client.get_caller_identity()
    except ClientError as exc:
        raise RuntimeError(f"Failed to read AWS identity: {exc}") from exc

    return {
        "Account": str(response.get("Account", "")),
        "Arn": str(response.get("Arn", "")),
        "UserId": str(response.get("UserId", "")),
    }
