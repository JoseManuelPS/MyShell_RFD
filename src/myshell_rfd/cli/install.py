"""Install-related CLI commands for MyShell_RFD.

Contains: install, uninstall, detect, clean commands.
"""

from typing import Annotated, Optional

import typer
from rich.table import Table

from myshell_rfd.cli import app, console


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
    from rich.prompt import Prompt

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
    init_registry()
    installer = get_installer()

    result = installer.uninstall_module(module)

    if result.success:
        logger.success(f"Uninstalled {module}")
    else:
        logger.error(result.message)
        raise typer.Exit(1)


@app.command()
def detect() -> None:
    """Auto-detect installed tools and configure matching modules."""
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.core.registry import init_registry
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()

    init_registry()
    installer = get_installer()

    logger.header("Auto-Detection")

    configured = installer.auto_detect_and_configure()

    if configured:
        logger.success(f"Configured {len(configured)} modules:")
        for name in configured:
            logger.print(f"  - {name}")


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
