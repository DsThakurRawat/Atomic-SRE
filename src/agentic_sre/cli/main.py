"""CLI entrypoint for the Agentic SRE."""

import click

from agentic_sre.cli.interactive_shell import start_interactive_shell
from agentic_sre.cli.presentation.styles import apply_questionary_style


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Run the Agentic SRE CLI entrypoint.

    Args:
        ctx: Click context for the command invocation.
    """
    apply_questionary_style()
    if ctx.invoked_subcommand is None:
        start_interactive_shell()


def main() -> None:
    """Run the CLI."""
    cli()
