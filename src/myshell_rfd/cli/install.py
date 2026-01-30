"""Install-related CLI commands for MyShell_RFD.

Contains: install, uninstall, detect, clean, doctor commands.
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
        if yes:
            # Install all automatically
            results = installer.install_all(auto_yes=True)
            success_count = sum(1 for r in results.values() if r.success)
            logger.info(f"Installed {success_count}/{len(results)} modules")
        else:
            # Interactive installation for all modules
            modules = list(registry.get_available())
            
            if not modules:
                logger.warn("No available modules found")
                raise typer.Exit(0)

            logger.info(f"Found {len(modules)} available modules")
            results = {}
            installed_count = 0
            
            for m in modules:
                if m.check_installed():
                    continue

                if typer.confirm(f"Install {m.name}?", default=True):
                    result = installer.install_module(m.name, auto_yes=True)
                    results[m.name] = result
                    if result.success:
                        installed_count += 1
                        logger.success(f"Installed {m.name}")
                    else:
                        logger.error(f"Failed to install {m.name}: {result.message}")
            
            if installed_count > 0:
                logger.info(f"Installed {installed_count} modules")
            else:
                logger.info("No modules installed")

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
def doctor(
    fix: Annotated[
        bool,
        typer.Option("--fix", "-f", help="Fix missing prerequisites"),
    ] = False,
    change_shell: Annotated[
        bool,
        typer.Option("--change-shell", help="Change default shell to ZSH if needed"),
    ] = False,
) -> None:
    """Check and fix system prerequisites.

    Verifies that zsh, git, curl are installed and optionally
    changes the default shell to ZSH.

    Examples:
        myshell doctor           # Check prerequisites status
        myshell doctor --fix     # Fix missing prerequisites
        myshell doctor --fix --change-shell  # Also change default shell
    """
    from myshell_rfd.core.installer import get_installer
    from myshell_rfd.utils.logger import get_logger

    logger = get_logger()
    installer = get_installer()
    status = installer.get_prerequisites_status()

    # Display status table
    table = Table(title="System Health Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status")

    def status_icon(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]✗[/red]"

    table.add_row("ZSH installed", status_icon(status.zsh_installed))
    table.add_row("ZSH is default shell", status_icon(status.zsh_default))
    table.add_row("Git installed", status_icon(status.git_installed))
    table.add_row("Curl installed", status_icon(status.curl_installed))
    table.add_row("Oh My Zsh installed", status_icon(status.omz_installed))
    table.add_row("Config sourced", status_icon(status.config_sourced))

    console.print(table)

    if status.all_ok and status.config_sourced:
        console.print("\n[green]All prerequisites met![/green]")
        return

    if not fix:
        console.print("\n[yellow]Run with --fix to install missing prerequisites[/yellow]")
        if status.zsh_installed and not status.zsh_default:
            console.print("[yellow]Add --change-shell to also set ZSH as default[/yellow]")
        raise typer.Exit(1)

    # Fix issues
    logger.info("Fixing prerequisites...")
    if installer.fix_prerequisites(change_shell=change_shell):
        console.print("\n[green]All issues fixed![/green]")
        console.print("[dim]Restart your shell for changes to take effect.[/dim]")
    else:
        console.print("\n[yellow]Some issues could not be fixed automatically.[/yellow]")
        raise typer.Exit(1)
