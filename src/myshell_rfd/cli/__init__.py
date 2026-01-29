"""CLI interface for MyShell_RFD.

Provides command-line interface using Typer for all operations.
This package splits the CLI into logical modules for maintainability.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from myshell_rfd import __version__

# Create main app
app = typer.Typer(
    name="myshell",
    help="Professional shell configuration tool for ZSH",
    add_completion=True,
    no_args_is_help=False,
    rich_markup_mode="rich",
)

# Shared console instance
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"MyShell_RFD v{__version__}")
        raise typer.Exit()


def setup_logging(debug: bool, quiet: bool) -> None:
    """Configure logging based on flags."""
    from myshell_rfd.utils.logger import Logger, set_logger

    logger = Logger(debug_mode=debug, quiet=quiet)
    set_logger(logger)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version", "-v",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Enable debug output"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress non-essential output"),
    ] = False,
    offline: Annotated[
        bool,
        typer.Option("--offline", help="Enable offline mode (use cached resources)"),
    ] = False,
    profile_name: Annotated[
        str,
        typer.Option("--profile", "-p", help="Use specific profile"),
    ] = "default",
) -> None:
    """MyShell_RFD - Professional ZSH configuration tool.

    Run without arguments to start interactive TUI mode.
    """
    # Store context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["quiet"] = quiet
    ctx.obj["offline"] = offline
    ctx.obj["profile"] = profile_name

    setup_logging(debug, quiet)

    # If no sub-command, launch TUI
    if ctx.invoked_subcommand is None:
        from myshell_rfd.tui.app import run

        run()


# Import and register sub-commands
# These imports must come after app is defined to avoid circular imports
from myshell_rfd.cli import commands  # noqa: E402, F401
from myshell_rfd.cli import install  # noqa: E402, F401
from myshell_rfd.cli import profile  # noqa: E402, F401
from myshell_rfd.cli import rollback  # noqa: E402, F401
