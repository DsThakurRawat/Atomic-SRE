"""Security group management for ECS.

This module is part of the Atomic-SRE infrastructure layer, strictly isolating cloud-specific
deployment and resource management logic from the core orchestrator. This separation of
concerns ensures that the AI engine remains agnostic to the underlying AWS environment.
"""

from boto3.session import Session
from botocore.exceptions import ClientError

from atomic_sre.infrastructure.aws.models import SecurityGroupInfo


def create_security_group(
    session: Session,
    vpc_id: str,
    name: str,
    description: str,
) -> SecurityGroupInfo:
    """Create a security group with default outbound access."""
    ec2 = session.client("ec2")
    try:
        response = ec2.create_security_group(
            VpcId=vpc_id,
            GroupName=name,
            Description=description,
        )
    except ClientError as exc:
        raise RuntimeError(f"Failed to create security group: {exc}") from exc

    group_id = response["GroupId"]
    ec2.create_tags(Resources=[group_id], Tags=[{"Key": "Name", "Value": name}])

    return SecurityGroupInfo(
        group_id=group_id,
        name=name,
        description=description,
    )
