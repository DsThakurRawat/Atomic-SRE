"""Interactive shell for guided deployment.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""

import questionary

from atomic_sre.interfaces.console.banner import print_global_banner
from atomic_sre.interfaces.console.console import console
from atomic_sre.interfaces.handlers.local import run_local_mode
from atomic_sre.interfaces.handlers.remote.menu import run_remote_mode
from atomic_sre.interfaces.setup import ensure_required_config


def _refresh_screen(message: str = "") -> None:
    """Clear the screen and reprint the banner with an optional status message."""
    console.clear()
    print_global_banner(animated=False)
    if message:
        console.print(message)


def start_interactive_shell() -> None:
    """Start the interactive deployment shell."""
    print_global_banner()
    ensure_required_config()

    _refresh_screen()
    while True:
        choice = questionary.select(
            "Running Mode:",
            choices=[
                "Local",
                "Remote Deployment",
                "Exit",
            ],
        ).ask()

        if choice in (None, "Exit"):
            console.print("Goodbye.")
            return

        if choice == "Local":
            run_local_mode()
        elif choice == "Remote Deployment":
            run_remote_mode()

        _refresh_screen()
