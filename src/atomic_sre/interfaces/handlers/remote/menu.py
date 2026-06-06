"""Remote deployment mode for the CLI.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""

import questionary

from atomic_sre.interfaces.console.banner import print_global_banner
from atomic_sre.interfaces.console.console import console
from atomic_sre.interfaces.handlers.remote.aws.ecs.menu import run_aws_ecs_mode


def run_remote_mode() -> None:
    """Run the remote deployment actions."""
    console.clear()
    print_global_banner(animated=False)

    target = questionary.select(
        "Remote Deployment:",
        choices=[
            "AWS ECS",
            "Back",
        ],
    ).ask()

    if target in (None, "Back"):
        return
    if target == "AWS ECS":
        run_aws_ecs_mode()
