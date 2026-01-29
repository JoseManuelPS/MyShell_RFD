"""ZSH plugin modules for MyShell_RFD.

Configures zsh-autosuggestions, zsh-completions, and zsh-syntax-highlighting.
"""

from pathlib import Path

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    GitCloneModule,
    InstallResult,
    InstallationType,
    ModuleCategory,
    ModuleInfo,
)


class ZshAutosuggestionsModule(GitCloneModule):
    """ZSH Autosuggestions plugin module.

    Installs:
    - Fish-like autosuggestions for ZSH
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="ZSH-Autosuggestions",
            description="Fish-like autosuggestions for ZSH",
            category=ModuleCategory.SHELL,
            installation_type=InstallationType.GIT_CLONE,
            provides=["zsh-autosuggestions"],
            tags=["zsh", "autosuggestions", "plugin"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/zsh-users/zsh-autosuggestions.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return self._get_zsh_custom() / "plugins" / "zsh-autosuggestions"

    def check_available(self) -> bool:
        """Can always be installed."""
        return True

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install and enable the plugin."""
        result = super().install(config)

        if result.success:
            from myshell_rfd.core.shell import get_shell_manager

            shell = get_shell_manager()
            shell.enable_omz_plugin("zsh-autosuggestions")

        return result


class ZshAutocompletionsModule(GitCloneModule):
    """ZSH Completions plugin module.

    Installs:
    - Additional ZSH completions
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="ZSH-Completions",
            description="Additional ZSH completions",
            category=ModuleCategory.SHELL,
            installation_type=InstallationType.GIT_CLONE,
            provides=["zsh-completions"],
            tags=["zsh", "completions", "plugin"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/zsh-users/zsh-completions.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return self._get_zsh_custom() / "plugins" / "zsh-completions"

    def check_available(self) -> bool:
        """Can always be installed."""
        return True

    def get_config_content(self, config: ModuleConfig) -> str:
        """Add completions to fpath."""
        return f"""# ZSH Completions
fpath+={self.target_dir}/src"""

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install and enable the plugin."""
        result = super().install(config)

        if result.success:
            from myshell_rfd.core.shell import get_shell_manager

            shell = get_shell_manager()
            shell.enable_omz_plugin("zsh-completions")

            # Add fpath config
            self._add_config(self.get_config_content(config))

        return result


class ZshSyntaxHighlightingModule(GitCloneModule):
    """ZSH Syntax Highlighting plugin module.

    Installs:
    - Fish-like syntax highlighting for ZSH
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="ZSH-Syntax-Highlighting",
            description="Fish-like syntax highlighting for ZSH",
            category=ModuleCategory.SHELL,
            installation_type=InstallationType.GIT_CLONE,
            provides=["zsh-syntax-highlighting"],
            tags=["zsh", "syntax", "highlighting", "plugin"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/zsh-users/zsh-syntax-highlighting.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return self._get_zsh_custom() / "plugins" / "zsh-syntax-highlighting"

    def check_available(self) -> bool:
        """Can always be installed."""
        return True

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install and enable the plugin."""
        result = super().install(config)

        if result.success:
            from myshell_rfd.core.shell import get_shell_manager

            shell = get_shell_manager()
            shell.enable_omz_plugin("zsh-syntax-highlighting")

        return result
