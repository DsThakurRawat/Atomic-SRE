"""AWS ECS deployment helpers.

This module is part of the Atomic-SRE infrastructure layer, strictly isolating cloud-specific
deployment and resource management logic from the core orchestrator. This separation of
concerns ensures that the AI engine remains agnostic to the underlying AWS environment.
"""

from atomic_sre.infrastructure.aws.cleanup import cleanup_resources
from atomic_sre.infrastructure.aws.ecr import ensure_repository
from atomic_sre.infrastructure.aws.ecs_tasks import (
    ensure_cluster,
    register_task_definition,
    run_task,
    wait_for_task_completion,
)
from atomic_sre.infrastructure.aws.iam import ensure_roles, ensure_service_linked_role
from atomic_sre.infrastructure.aws.images import ImageBuildConfig, build_and_push_images
from atomic_sre.infrastructure.aws.models import (
    EcsDeploymentConfig,
    NetworkSelection,
    SecurityGroupInfo,
)
from atomic_sre.infrastructure.aws.network import create_basic_vpc
from atomic_sre.infrastructure.aws.secrets import (
    SecretInfo,
    create_secret,
    get_secret_info,
    restore_secret,
)
from atomic_sre.infrastructure.aws.security_groups import create_security_group
from atomic_sre.infrastructure.aws.session import create_session, get_identity
from atomic_sre.infrastructure.aws.status import check_deployment

__all__ = [
    "EcsDeploymentConfig",
    "NetworkSelection",
    "ImageBuildConfig",
    "SecurityGroupInfo",
    "build_and_push_images",
    "cleanup_resources",
    "check_deployment",
    "create_basic_vpc",
    "create_security_group",
    "create_secret",
    "create_session",
    "ensure_cluster",
    "ensure_repository",
    "ensure_roles",
    "ensure_service_linked_role",
    "get_identity",
    "get_secret_info",
    "restore_secret",
    "register_task_definition",
    "run_task",
    "wait_for_task_completion",
    "SecretInfo",
]
