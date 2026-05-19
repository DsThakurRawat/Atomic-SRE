"""CLI banner rendering."""

from importlib.metadata import PackageNotFoundError, version

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from atomic_sre.cli.presentation.ascii_art import get_ascii_art
from atomic_sre.cli.presentation.console import console

_COLOURS = ["bold green"]


def print_global_banner(animated: bool = True) -> None:
    """Print the main CLI banner.

    Args:
        animated: Unused, kept for backward compatibility.
    """
    console.print(_build_banner())


def _build_banner() -> Panel:
    """Build the banner panel with solid bold green styling.

    Returns:
        The styled Panel group.
    """
    ascii_art = get_ascii_art().strip("\n")
    # spellchecker:ignore-next-line
    banner_text = Text(justify="center")
    banner_text.append("\n")
    for line in ascii_art.splitlines():
        if not line.strip():
            banner_text.append("\n")
            continue
        banner_text.append(f"{line}\n", style="bold green")

    banner_text.append(
        "\n🤖 Autonomous Multi-Agent AI Orchestration for SRE\n",
        style="bright_white",
    )
    banner_text.append("Observe • Reason • Act • Heal\n", style="dim white")
    banner_text.append("\n")

    footer_text = Text(justify="right")
    footer_text.append(f"v{_get_version()}\n", style="bold green")
    footer_text.append("Made by DIVYANSH RAWAT", style="dim white")
    return Panel(
        Group(banner_text, footer_text),
        title="Welcome to Atomic SRE",
        border_style="bold green",
        expand=True,
    )


def _get_version() -> str:
    """Return the CLI version.

    Returns:
        The CLI version string.
    """
    try:
        return version("atomic-sre")
    except PackageNotFoundError:
        return "0.2.0"
