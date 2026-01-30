"""Theme modules for MyShell_RFD.

Configures PowerLevel10K and other ZSH themes.
"""

import base64
from pathlib import Path

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    GitCloneModule,
    InstallResult,
    InstallationType,
    ModuleCategory,
    ModuleInfo,
)


class PowerLevel10KModule(GitCloneModule):
    """PowerLevel10K theme module.

    Installs and configures:
    - PowerLevel10K ZSH theme
    - Default p10k configuration
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="PowerLevel10K",
            description="Modern ZSH theme with instant prompt",
            category=ModuleCategory.THEME,
            installation_type=InstallationType.GIT_CLONE,
            provides=["powerlevel10k", "p10k"],
            tags=["theme", "powerlevel10k", "p10k", "prompt"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/romkatv/powerlevel10k.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return self._get_zsh_custom() / "themes" / "powerlevel10k"

    def check_available(self) -> bool:
        """Can always be installed."""
        return True

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install PowerLevel10K theme."""
        result = super().install(config)

        if not result.success:
            return result

        # Set theme in .zshrc
        from myshell_rfd.core.shell import get_shell_manager

        shell = get_shell_manager()
        shell.set_theme("powerlevel10k/powerlevel10k")

        # Install default p10k configuration
        self._install_p10k_config(config)

        self._logger.success("PowerLevel10K theme installed")

        return InstallResult(
            success=True,
            message="PowerLevel10K installed and configured",
            files_created=[str(self.target_dir)],
            files_modified=[str(Path.home() / ".zshrc"), str(Path.home() / ".p10k.zsh")],
        )

    def _install_p10k_config(self, config: ModuleConfig) -> bool:
        """Install the default p10k configuration file."""
        p10k_dest = Path.home() / ".p10k.zsh"

        # Check if user wants to keep existing config
        if p10k_dest.exists() and not config.settings.get("overwrite_config", False):
            self._logger.info("Keeping existing .p10k.zsh configuration")
            return True

        # Try to load bundled p10k config
        try:
            from importlib.resources import files

            assets = files("myshell_rfd.assets")
            p10k_content = (assets / "p10k.zsh").read_text()
            p10k_dest.write_text(p10k_content)
            self._logger.debug("Installed bundled p10k configuration")
            return True
        except Exception as e:
            self._logger.debug(f"Could not load bundled config: {e}")

        # Fallback: check if file exists in assets directory (REMOVED LEGACY FALLBACK)
        # The importlib.resources method above should be sufficient.

        self._logger.warn("No bundled p10k config found. Run 'p10k configure' to set up.")
        return False

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate P10K configuration."""
        return """# PowerLevel10K instant prompt
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
    source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Load p10k configuration
[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh"""

    def uninstall(self) -> InstallResult:
        """Uninstall PowerLevel10K."""
        # Reset theme to default
        from myshell_rfd.core.shell import get_shell_manager

        shell = get_shell_manager()
        shell.set_theme("robbyrussell")

        # Remove p10k.zsh
        p10k_config = Path.home() / ".p10k.zsh"
        if p10k_config.exists():
            self._file_ops.backup_file(p10k_config)
            p10k_config.unlink()

        # Remove theme directory
        return super().uninstall()
