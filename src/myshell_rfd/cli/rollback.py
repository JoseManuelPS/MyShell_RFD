"""Rollback management CLI commands for MyShell_RFD.

Contains: rollback list, apply, clear commands.
"""

from typing import Annotated

import typer
from rich.table import Table

from myshell_rfd.cli import app, console

# Create rollback sub-app
rollback_app = typer.Typer(help="Manage configuration snapshots")
app.add_typer(rollback_app, name="rollback")


@rollback_app.command(name="list")
def rollback_list(
    limit: Annotated[
        int,
        typer.Option("--limit", "-n", help="Number of snapshots to show"),
    ] = 10,
) -> None:
    """List available snapshots."""
    from myshell_rfd.core.rollback import get_rollback_manager

    manager = get_rollback_manager()

    table = Table(title="Configuration Snapshots")
    table.add_column("ID", style="cyan")
    table.add_column("Created", style="blue")
    table.add_column("Description")
    table.add_column("Files")

    for i, snapshot in enumerate(manager.list_snapshots()):
        if i >= limit:
            break
        table.add_row(
            snapshot.id,
            snapshot.created_at[:19],
            snapshot.description,
            str(len(snapshot.files)),
        )

    console.print(table)


@rollback_app.command()
def apply(
    snapshot_id: Annotated[
        str,
        typer.Argument(help="Snapshot ID to rollback to"),
    ],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation"),
    ] = False,
) -> None:
    """Rollback to a specific snapshot."""
    from myshell_rfd.core.rollback import get_rollback_manager
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    manager = get_rollback_manager()

    snapshot = manager.get_snapshot(snapshot_id)
    if not snapshot:
        logger.error(f"Snapshot not found: {snapshot_id}")
        raise typer.Exit(1)

    console.print(f"[bold]Snapshot:[/bold] {snapshot.id}")
    console.print(f"[bold]Created:[/bold] {snapshot.created_at}")
    console.print(f"[bold]Description:[/bold] {snapshot.description}")
    console.print(f"[bold]Files:[/bold] {len(snapshot.files)}")

    if not yes:
        if not typer.confirm("Apply this rollback?"):
            raise typer.Abort()

    if manager.rollback(snapshot_id):
        logger.success("Rollback applied successfully")
    else:
        logger.error("Rollback failed")
        raise typer.Exit(1)


@rollback_app.command()
def clear(
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation"),
    ] = False,
) -> None:
    """Clear all snapshots."""
    from myshell_rfd.core.rollback import get_rollback_manager
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()

    if not yes:
        if not typer.confirm("Delete all snapshots?"):
            raise typer.Abort()

    manager = get_rollback_manager()
    count = manager.clear_all()
    logger.success(f"Cleared {count} snapshots")
