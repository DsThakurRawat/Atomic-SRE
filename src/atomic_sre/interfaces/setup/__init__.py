"""CLI configuration wizard package.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""

from atomic_sre.interfaces.setup.models import CliConfig
from atomic_sre.interfaces.setup.store import ConfigError, load_config, save_config
from atomic_sre.interfaces.setup.wizard import ensure_required_config

__all__ = [
    "CliConfig",
    "ConfigError",
    "ensure_required_config",
    "load_config",
    "save_config",
]
