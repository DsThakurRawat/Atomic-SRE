"""CLI entrypoint for the Atomic SRE.

This module manages the presentation, CLI, and user interaction boundaries for the Atomic-SRE
framework. It serves as the primary entrypoint for user commands and handles the translation
of human intent into orchestrator actions.
"""

import click

from atomic_sre.interfaces.console.styles import apply_questionary_style
from atomic_sre.interfaces.interactive_shell import start_interactive_shell


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Run the Atomic SRE CLI entrypoint.

    Args:
        ctx: Click context for the command invocation.
    """
    apply_questionary_style()
    if ctx.invoked_subcommand is None:
        start_interactive_shell()


def main() -> None:
    """Run the CLI."""
    cli()


if __name__ == "__main__":
    main()
