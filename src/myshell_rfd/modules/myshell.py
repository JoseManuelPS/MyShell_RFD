"""MyShell_RFD self-configuration module.

Configures MyShell_RFD's own shell integration, including:
- Shell completion for the myshell command
- Aliases and helper functions
"""

from pathlib import Path

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    BaseModule,
    InstallResult,
    InstallationType,
    ModuleCategory,
    ModuleInfo,
)


# ZSH completion script for myshell command
MYSHELL_COMPLETION_SCRIPT = '''#compdef myshell

_myshell() {
    local -a commands
    local -a global_opts

    commands=(
        'list:List all available modules'
        'info:Show detailed information about a module'
        'install:Install and configure modules'
        'uninstall:Uninstall a module and remove its configuration'
        'clean:Remove all MyShell_RFD configuration'
        'update:Check for updates and update MyShell_RFD'
        'profile:Manage configuration profiles'
        'rollback:Manage configuration snapshots'
        'completion:Shell completion management'
    )

    global_opts=(
        '(-v --version)'{-v,--version}'[Show version and exit]'
        '(-d --debug)'{-d,--debug}'[Enable debug output]'
        '(-q --quiet)'{-q,--quiet}'[Suppress non-essential output]'
        '--offline[Enable offline mode]'
        '(-p --profile)'{-p,--profile}'[Use specific profile]:profile:'
        '(-h --help)'{-h,--help}'[Show help message]'
    )

    _arguments -C \\
        $global_opts \\
        '1:command:->command' \\
        '*::arg:->args'

    case "$state" in
        command)
            _describe -t commands 'myshell commands' commands
            ;;
        args)
            case $words[1] in
                install|uninstall|info)
                    # Complete with module names
                    local -a modules
                    modules=(${(f)"$(myshell list --quiet 2>/dev/null | tail -n +3 | awk '{print $1}' 2>/dev/null)"})
                    if [[ -n "$modules" ]]; then
                        _describe -t modules 'modules' modules
                    fi
                    ;;
                profile)
                    local -a profile_commands
                    profile_commands=(
                        'list:List all profiles'
                        'switch:Switch to a different profile'
                        'create:Create a new profile'
                        'delete:Delete a profile'
                        'export:Export a profile to a file'
                        'import:Import a profile from a file'
                    )
                    _describe -t profile-commands 'profile commands' profile_commands
                    ;;
                rollback)
                    local -a rollback_commands
                    rollback_commands=(
                        'list:List available snapshots'
                        'apply:Rollback to a specific snapshot'
                        'clear:Clear all snapshots'
                    )
                    _describe -t rollback-commands 'rollback commands' rollback_commands
                    ;;
                completion)
                    local -a completion_commands
                    completion_commands=(
                        'install:Install shell completion'
                        'show:Show completion script'
                        'uninstall:Remove shell completion'
                    )
                    _describe -t completion-commands 'completion commands' completion_commands
                    ;;
            esac
            ;;
    esac
}

compdef _myshell myshell
'''


class MyShellModule(BaseModule):
    """MyShell_RFD self-configuration module.

    Installs shell completion and configuration for the myshell command itself.
    This allows myshell to be configured just like any other tool.
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="MyShell",
            description="MyShell_RFD shell completion and aliases",
            category=ModuleCategory.TOOLS,
            installation_type=InstallationType.CONFIG_ONLY,
            provides=["myshell-completion", "myshell-aliases"],
            tags=["myshell", "completion", "zsh", "shell"],
        )

    def check_available(self) -> bool:
        """MyShell is always available (we're running it)."""
        return True

    def check_installed(self) -> bool:
        """Check if myshell completion is installed."""
        completion_paths = self._get_completion_paths()
        return any(p.exists() for p in completion_paths)

    def _get_completion_paths(self) -> list[Path]:
        """Get possible completion file paths."""
        home = Path.home()
        return [
            home / ".oh-my-zsh/custom/plugins/myshell/_myshell",
            home / ".zsh/completions/_myshell",
        ]

    def _get_install_path(self) -> Path:
        """Determine the best path to install completion."""
        home = Path.home()

        # Prefer Oh My Zsh if installed
        omz_dir = home / ".oh-my-zsh"
        if omz_dir.exists():
            return home / ".oh-my-zsh/custom/plugins/myshell/_myshell"

        # Fallback to standard zsh completions
        return home / ".zsh/completions/_myshell"

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate myshell shell configuration."""
        return """# MyShell_RFD aliases
alias msrfd='myshell'
alias msrfdl='myshell list'
alias msrfdi='myshell install'"""

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install myshell completion and configuration."""
        # Determine installation path
        install_path = self._get_install_path()

        # Create parent directory
        install_path.parent.mkdir(parents=True, exist_ok=True)

        # Write completion script
        install_path.write_text(MYSHELL_COMPLETION_SCRIPT)
        self._logger.debug(f"Installed completion to: {install_path}")

        # Add shell configuration (aliases)
        self._add_config(self.get_config_content(config))

        # If using Oh My Zsh plugin directory, create plugin init file
        if ".oh-my-zsh" in str(install_path):
            init_file = install_path.parent / "myshell.plugin.zsh"
            init_content = """# MyShell_RFD Oh-My-Zsh plugin
# This file enables the myshell zsh completion

# Completion is auto-loaded from _myshell file
"""
            init_file.write_text(init_content)

            # Enable the plugin
            from myshell_rfd.core.shell import get_shell_manager

            shell = get_shell_manager()
            shell.enable_omz_plugin("myshell")

        self._logger.success("MyShell completion installed")

        return InstallResult(
            success=True,
            message="MyShell_RFD shell completion and aliases installed",
            files_created=[str(install_path)],
        )

    def uninstall(self, config: ModuleConfig | None = None) -> InstallResult:
        """Uninstall myshell completion."""
        removed_files = []

        for path in self._get_completion_paths():
            if path.exists():
                path.unlink()
                removed_files.append(str(path))

                # Remove parent dir if empty (for oh-my-zsh plugin dir)
                if path.parent.name == "myshell":
                    # Also remove plugin init file if present
                    init_file = path.parent / "myshell.plugin.zsh"
                    if init_file.exists():
                        init_file.unlink()

                    if not any(path.parent.iterdir()):
                        path.parent.rmdir()

        # Remove config from .zshrc
        self._remove_config()

        if removed_files:
            return InstallResult(
                success=True,
                message="MyShell_RFD shell completion removed",
                files_removed=removed_files,
            )

        return InstallResult(
            success=True,
            message="MyShell_RFD was not installed",
        )
