"""Profile management CLI commands for MyShell_RFD.

Contains: profile list, switch, create, delete, export, import commands.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.table import Table

from myshell_rfd.cli import app, console

# Create profile sub-app
profile_app = typer.Typer(help="Manage configuration profiles")
app.add_typer(profile_app, name="profile")


@profile_app.command(name="list")
def profile_list() -> None:
    """List all profiles."""
    from myshell_rfd.core.config import get_config

    config = get_config()

    table = Table(title="Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Active", style="green")
    table.add_column("Modules")

    for name, profile in config.profiles.items():
        active = "[green]*[/green]" if name == config.active_profile else ""
        enabled = len(profile.get_enabled_modules())
        table.add_row(name, profile.description, active, str(enabled))

    console.print(table)


@profile_app.command()
def switch(
    name: Annotated[
        str,
        typer.Argument(help="Profile name to switch to"),
    ],
) -> None:
    """Switch to a different profile."""
    from myshell_rfd.core.config import get_config, save_config
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    config = get_config()

    try:
        config.switch_profile(name)
        save_config()
        logger.success(f"Switched to profile: {name}")
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)


@profile_app.command()
def create(
    name: Annotated[
        str,
        typer.Argument(help="New profile name"),
    ],
    description: Annotated[
        str,
        typer.Option("--desc", "-d", help="Profile description"),
    ] = "",
    copy_from: Annotated[
        Optional[str],
        typer.Option("--copy", "-c", help="Copy from existing profile"),
    ] = None,
) -> None:
    """Create a new profile."""
    from myshell_rfd.core.config import get_config, save_config
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    config = get_config()

    try:
        config.create_profile(name, description=description, copy_from=copy_from)
        save_config()
        logger.success(f"Created profile: {name}")
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)


@profile_app.command()
def delete(
    name: Annotated[
        str,
        typer.Argument(help="Profile name to delete"),
    ],
) -> None:
    """Delete a profile."""
    from myshell_rfd.core.config import get_config, save_config
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    config = get_config()

    try:
        if config.delete_profile(name):
            save_config()
            logger.success(f"Deleted profile: {name}")
        else:
            logger.warn(f"Profile not found: {name}")
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)


@profile_app.command(name="export")
def profile_export(
    name: Annotated[
        str,
        typer.Argument(help="Profile name to export"),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file path"),
    ] = Path("profile.toml"),
) -> None:
    """Export a profile to a file."""
    from myshell_rfd.core.config import get_config
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    config = get_config()

    try:
        config.export_profile(name, output)
        logger.success(f"Exported profile to: {output}")
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)


@profile_app.command(name="import")
def profile_import(
    path: Annotated[
        Path,
        typer.Argument(help="Profile file to import"),
    ],
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Override profile name"),
    ] = None,
) -> None:
    """Import a profile from a file."""
    from myshell_rfd.core.config import get_config, save_config
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    config = get_config()

    try:
        profile = config.import_profile(path, name)
        save_config()
        logger.success(f"Imported profile: {profile.name}")
    except (ValueError, FileNotFoundError) as e:
        logger.error(str(e))
        raise typer.Exit(1)
