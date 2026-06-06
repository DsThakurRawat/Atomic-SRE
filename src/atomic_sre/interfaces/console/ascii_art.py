"""ASCII art for the CLI.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""


def get_ascii_art() -> str:
    """Return the Atomic SRE ASCII art.

    Returns:
        The ASCII art string.
    """
    return r"""
 █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗  ███████╗██████╗ ███████╗
██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝  ██╔════╝██╔══██╗██╔════╝
███████║   ██║   ██║   ██║██╔████╔██║██║██║       ███████╗██████╔╝█████╗
██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║       ╚════██║██╔══██╗██╔══╝
██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗  ███████║██║  ██║███████╗
╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝  ╚══════╝╚═╝  ╚═╝╚══════╝
"""
