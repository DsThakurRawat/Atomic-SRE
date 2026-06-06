"""Path helpers for the CLI.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""

from pathlib import Path


def project_root() -> Path:
    """Return the repository root directory.

    Returns:
        The repository root directory path.
    """
    return Path(__file__).resolve().parents[4]
