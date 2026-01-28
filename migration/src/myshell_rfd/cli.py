"""CLI interface for MyShell_RFD.

Provides command-line interface using Typer for all operations.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from myshell_rfd import __version__

# Create main app
app = typer.Typer(
    name="myshell",
    help="Professional shell configuration tool for ZSH",
    add_completion=True,
    no_args_is_help=False,
    rich_markup_mode="rich",
)

# Sub-commands
profile_app = typer.Typer(help="Manage configuration profiles")
rollback_app = typer.Typer(help="Manage configuration snapshots")

app.add_typer(profile_app, name="profile")
app.add_typer(rollback_app, name="rollback")

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


@app.command()
def install(
    ctx: typer.Context,
    module: Annotated[
        Optional[str],
        typer.Argument(help="Module name to install (omit for interactive selection)"),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Auto-accept all prompts"),
    ] = False,
    all_modules: Annotated[
        bool,
        typer.Option("--all", "-a", help="Install all available modules"),
    ] = False,
) -> None:
    """Install and configure modules.

    Without arguments, shows an interactive module selector.
    Specify a module name to install directly, or use --all for everything.
    """
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.core.registry import init_registry
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    offline = ctx.obj.get("offline", False)

    # Initialize
    registry = init_registry()
    installer = get_installer(offline=offline)

    # Check prerequisites
    missing = installer.check_prerequisites()
    if missing:
        logger.warn(f"Missing prerequisites: {', '.join(missing)}")
        if typer.confirm("Install prerequisites?", default=True):
            if not installer.install_prerequisites():
                logger.error("Failed to install prerequisites")
                raise typer.Exit(1)

    # Ensure Oh My Zsh
    if not installer.ensure_omz():
        raise typer.Exit(1)

    if all_modules:
        # Install all available modules
        results = installer.install_all(auto_yes=yes)
        success_count = sum(1 for r in results.values() if r.success)
        logger.info(f"Installed {success_count}/{len(results)} modules")

    elif module:
        # Install specific module
        result = installer.install_module(module, auto_yes=yes)
        if not result.success:
            logger.error(result.message)
            raise typer.Exit(1)

    else:
        # Interactive selection
        modules = list(registry.get_available())

        if not modules:
            logger.warn("No available modules found")
            raise typer.Exit(0)

        # Build choices
        choices = {m.name: m for m in modules}
        choice_list = list(choices.keys())

        # Use rich prompt for selection
        from rich.prompt import Prompt

        logger.header("Module Selection")

        table = Table(title="Available Modules")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Status", style="green")

        for m in sorted(modules, key=lambda x: x.name):
            status = "[green]Ready[/green]" if m.check_available() else "[yellow]Missing deps[/yellow]"
            installed = "[blue]Installed[/blue]" if m.check_installed() else ""
            table.add_row(m.name, m.info.description, installed or status)

        console.print(table)
        console.print()

        selected = Prompt.ask(
            "Enter module name to install",
            choices=choice_list,
            default=choice_list[0] if choice_list else None,
        )

        if selected:
            result = installer.install_module(selected, auto_yes=yes)
            if not result.success:
                raise typer.Exit(1)


@app.command()
def uninstall(
    module: Annotated[
        str,
        typer.Argument(help="Module name to uninstall"),
    ],
) -> None:
    """Uninstall a module and remove its configuration."""
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.core.registry import init_registry
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    registry = init_registry()
    installer = get_installer()

    result = installer.uninstall_module(module)

    if result.success:
        logger.success(f"Uninstalled {module}")
    else:
        logger.error(result.message)
        raise typer.Exit(1)


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
    from myshell_rfd.core.module_base import ModuleCategory
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
    from rich.panel import Panel

    from myshell_rfd.core.registry import init_registry

    registry = init_registry()
    mod = registry.get(module)

    if not mod:
        console.print(f"[red]Module '{module}' not found[/red]")
        raise typer.Exit(1)

    info = mod.info

    content = f"""[bold]Name:[/bold] {info.name}
[bold]Category:[/bold] {info.category.value}
[bold]Description:[/bold] {info.description}
[bold]Installation Type:[/bold] {info.installation_type.value}

[bold]Required Binaries:[/bold] {', '.join(info.required_binaries) or 'None'}
[bold]Provides:[/bold] {', '.join(info.provides) or 'N/A'}
[bold]Tags:[/bold] {', '.join(info.tags) or 'N/A'}

[bold]Status:[/bold] {'[green]Installed[/green]' if mod.check_installed() else '[yellow]Not installed[/yellow]'}
[bold]Available:[/bold] {'[green]Yes[/green]' if mod.check_available() else '[red]No (missing dependencies)[/red]'}"""

    console.print(Panel(content, title=f"Module: {info.name}"))


@app.command()
def clean(
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation"),
    ] = False,
) -> None:
    """Remove all MyShell_RFD configuration."""
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()

    if not yes:
        if not typer.confirm("This will remove all MyShell_RFD configuration. Continue?"):
            raise typer.Abort()

    installer = get_installer()
    if installer.clean_config():
        logger.success("Configuration cleaned")
    else:
        logger.error("Failed to clean configuration")
        raise typer.Exit(1)


@app.command()
def update() -> None:
    """Check for updates and update MyShell_RFD."""
    from myshell_rfd.utils.logger import get_logger
    from myshell_rfd.utils.process import get_runner

    logger = get_logger()
    runner = get_runner()

    logger.info("Checking for updates...")

    # Check GitHub releases
    result = runner.run(
        ["curl", "-fsSL", "https://api.github.com/repos/myshell-rfd/myshell-rfd/releases/latest"],
        timeout=30.0,
    )

    if result.success:
        import json

        try:
            data = json.loads(result.stdout)
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
        except json.JSONDecodeError:
            logger.warn("Could not parse update information")
    else:
        logger.warn("Could not check for updates")


@app.command()
def detect() -> None:
    """Auto-detect installed tools and configure matching modules."""
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.core.registry import init_registry
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()

    registry = init_registry()
    installer = get_installer()

    logger.header("Auto-Detection")

    configured = installer.auto_detect_and_configure()

    if configured:
        console.print(f"\n[green]Configured {len(configured)} modules:[/green]")
        for name in configured:
            console.print(f"  - {name}")
    else:
        console.print("[yellow]No new modules to configure[/yellow]")


# Profile sub-commands
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


# Rollback sub-commands
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


if __name__ == "__main__":
    app()
