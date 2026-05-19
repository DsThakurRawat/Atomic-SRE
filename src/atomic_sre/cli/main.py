"""CLI entrypoint for the Atomic SRE."""

import click

from atomic_sre.cli.interactive_shell import start_interactive_shell
from atomic_sre.cli.presentation.styles import apply_questionary_style


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
