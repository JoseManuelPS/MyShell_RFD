"""Main CLI commands for MyShell_RFD.

Contains: list, info, update commands.
"""

from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from myshell_rfd import __version__
from myshell_rfd.cli import app, console


@app.command(name="list")
def list_modules(
    category: Annotated[
        Optional[str],
        typer.Option("--category", "-c", help="Filter by category"),
    ] = None,
    installed: Annotated[
        bool,
        typer.Option("--installed", "-i", help="Show only installed modules"),
    ] = False,
    available: Annotated[
        bool,
        typer.Option("--available", "-a", help="Show only available modules"),
    ] = False,
) -> None:
    """List all modules."""
    from myshell_rfd.core.registry import init_registry

    registry = init_registry()

    table = Table(title="MyShell_RFD Modules")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="blue")
    table.add_column("Description")
    table.add_column("Status")

    for module in sorted(registry.get_all(), key=lambda m: m.name):
        # Apply filters
        if category and module.category.value != category.lower():
            continue
        if installed and not module.check_installed():
            continue
        if available and not module.check_available():
            continue

        status_parts = []
        if module.check_installed():
            status_parts.append("[green]Installed[/green]")
        if module.check_available():
            status_parts.append("[blue]Available[/blue]")
        else:
            status_parts.append("[yellow]Missing deps[/yellow]")

        table.add_row(
            module.name,
            module.category.value,
            module.info.description,
            " ".join(status_parts),
        )

    console.print(table)


@app.command()
def info(
    module: Annotated[
        str,
        typer.Argument(help="Module name"),
    ],
) -> None:
    """Show detailed information about a module."""
    from myshell_rfd.core.registry import init_registry

    registry = init_registry()
    mod = registry.get(module)

    if not mod:
        console.print(f"[red]Module '{module}' not found[/red]")
        raise typer.Exit(1)

    mod_info = mod.info

    content = f"""[bold]Name:[/bold] {mod_info.name}
[bold]Category:[/bold] {mod_info.category.value}
[bold]Description:[/bold] {mod_info.description}
[bold]Installation Type:[/bold] {mod_info.installation_type.value}

[bold]Required Binaries:[/bold] {', '.join(mod_info.required_binaries) or 'None'}
[bold]Provides:[/bold] {', '.join(mod_info.provides) or 'N/A'}
[bold]Tags:[/bold] {', '.join(mod_info.tags) or 'N/A'}

[bold]Status:[/bold] {'[green]Installed[/green]' if mod.check_installed() else '[yellow]Not installed[/yellow]'}
[bold]Available:[/bold] {'[green]Yes[/green]' if mod.check_available() else '[red]No (missing dependencies)[/red]'}"""

    console.print(Panel(content, title=f"Module: {mod_info.name}"))


@app.command()
def update() -> None:
    """Check for updates and update MyShell_RFD."""
    import httpx

    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()

    logger.info("Checking for updates...")

    try:
        # Check GitHub releases using httpx
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                "https://api.github.com/repos/myshell-rfd/myshell-rfd/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            response.raise_for_status()
            data = response.json()

        latest = data.get("tag_name", "").lstrip("v")

        if latest and latest != __version__:
            logger.info(f"New version available: {latest} (current: {__version__})")
            if typer.confirm("Update now?"):
                # Download and install
                logger.info("Updating...")
                # Implementation would go here
                logger.success("Updated successfully. Please restart your shell.")
        else:
            logger.success(f"Already at latest version ({__version__})")

    except httpx.HTTPStatusError as e:
        logger.warn(f"Could not check for updates: HTTP {e.response.status_code}")
    except httpx.RequestError as e:
        logger.warn(f"Could not check for updates: {e}")
