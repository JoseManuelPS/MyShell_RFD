"""Shell management for MyShell_RFD.

Handles ZSH-specific operations including Oh My Zsh integration,
plugin management, and configuration.
"""

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.utils.detect import get_detector
from myshell_rfd.utils.files import get_file_ops
from myshell_rfd.utils.logger import get_logger
from myshell_rfd.utils.process import get_runner

if TYPE_CHECKING:
    from myshell_rfd.utils.detect import BinaryDetector
    from myshell_rfd.utils.files import FileOperations
    from myshell_rfd.utils.logger import Logger
    from myshell_rfd.utils.process import ProcessRunner


class ShellManager:
    """Manages ZSH shell configuration.

    Handles:
    - Oh My Zsh installation and plugin management
    - .zshrc modifications
    - Shell configuration sourcing
    """

    def __init__(
        self,
        logger: "Logger | None" = None,
        file_ops: "FileOperations | None" = None,
        runner: "ProcessRunner | None" = None,
        detector: "BinaryDetector | None" = None,
    ) -> None:
        """Initialize shell manager.

        Args:
            logger: Logger instance.
            file_ops: File operations instance.
            runner: Process runner instance.
            detector: Binary detector instance.
        """
        self._logger = logger or get_logger()
        self._file_ops = file_ops or get_file_ops()
        self._runner = runner or get_runner()
        self._detector = detector or get_detector()

    @property
    def zshrc_path(self) -> Path:
        """Get path to .zshrc."""
        return Path.home() / ".zshrc"

    @property
    def omz_dir(self) -> Path | None:
        """Get Oh My Zsh directory if installed."""
        return self._detector.get_oh_my_zsh_dir()

    @property
    def zsh_custom(self) -> Path:
        """Get ZSH_CUSTOM directory."""
        return self._detector.get_zsh_custom_dir()

    def is_zsh_installed(self) -> bool:
        """Check if ZSH is installed."""
        return self._detector.check_binary("zsh")

    def is_omz_installed(self) -> bool:
        """Check if Oh My Zsh is installed."""
        return self.omz_dir is not None

    def is_zsh_default(self) -> bool:
        """Check if ZSH is the default shell."""
        shell = os.environ.get("SHELL", "")
        return shell.endswith("zsh")

    def install_omz(self) -> bool:
        """Install Oh My Zsh.

        Returns:
            True if installed successfully.
        """
        if self.is_omz_installed():
            self._logger.info("Oh My Zsh is already installed")
            return True

        self._logger.info("Installing Oh My Zsh...")

        # Download and run installer
        result = self._runner.run(
            'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended',
            shell=True,
            timeout=120.0,
        )

        if result.success:
            self._logger.success("Oh My Zsh installed successfully")
            return True

        self._logger.error(f"Failed to install Oh My Zsh: {result.stderr}")
        return False

    def get_enabled_plugins(self) -> list[str]:
        """Get list of enabled Oh My Zsh plugins.

        Returns:
            List of plugin names.
        """
        content = self._file_ops.read_file(self.zshrc_path)
        if not content:
            return []

        # Match plugins=(...) pattern
        match = re.search(r"plugins=\(([^)]*)\)", content, re.MULTILINE | re.DOTALL)
        if not match:
            return []

        plugins_str = match.group(1)
        # Split on whitespace and newlines
        plugins = re.split(r"[\s\n]+", plugins_str)
        return [p.strip() for p in plugins if p.strip()]

    def enable_omz_plugin(self, plugin: str) -> bool:
        """Enable an Oh My Zsh plugin.

        Args:
            plugin: Plugin name to enable.

        Returns:
            True if plugin was enabled.
        """
        current_plugins = self.get_enabled_plugins()

        if plugin in current_plugins:
            self._logger.debug(f"Plugin '{plugin}' is already enabled")
            return True

        content = self._file_ops.read_file(self.zshrc_path)
        if not content:
            self._logger.error(".zshrc not found")
            return False

        # Find and update plugins line
        pattern = r"(plugins=\()([^)]*)\)"

        def replace_plugins(match: re.Match[str]) -> str:
            prefix = match.group(1)
            existing = match.group(2).strip()
            if existing:
                return f"{prefix}{existing} {plugin})"
            return f"{prefix}{plugin})"

        new_content, count = re.subn(pattern, replace_plugins, content)

        if count == 0:
            self._logger.error("Could not find plugins line in .zshrc")
            return False

        self._file_ops.write_file(self.zshrc_path, new_content, backup=True)
        self._logger.success(f"Enabled Oh My Zsh plugin: {plugin}")
        return True

    def disable_omz_plugin(self, plugin: str) -> bool:
        """Disable an Oh My Zsh plugin.

        Args:
            plugin: Plugin name to disable.

        Returns:
            True if plugin was disabled.
        """
        current_plugins = self.get_enabled_plugins()

        if plugin not in current_plugins:
            self._logger.debug(f"Plugin '{plugin}' is not enabled")
            return True

        content = self._file_ops.read_file(self.zshrc_path)
        if not content:
            return False

        # Remove plugin from list
        current_plugins.remove(plugin)

        # Rebuild plugins line
        plugins_str = " ".join(current_plugins)
        pattern = r"plugins=\([^)]*\)"
        new_content = re.sub(pattern, f"plugins=({plugins_str})", content)

        self._file_ops.write_file(self.zshrc_path, new_content, backup=True)
        self._logger.success(f"Disabled Oh My Zsh plugin: {plugin}")
        return True

    def set_theme(self, theme: str) -> bool:
        """Set the ZSH theme in .zshrc.

        Args:
            theme: Theme name.

        Returns:
            True if theme was set.
        """
        content = self._file_ops.read_file(self.zshrc_path)
        if not content:
            return False

        # Replace ZSH_THEME line
        pattern = r'ZSH_THEME="[^"]*"'
        new_content = re.sub(pattern, f'ZSH_THEME="{theme}"', content)

        if new_content == content:
            # Theme line not found, add it
            new_content = f'ZSH_THEME="{theme}"\n' + content

        self._file_ops.write_file(self.zshrc_path, new_content, backup=True)
        self._logger.success(f"Set ZSH theme: {theme}")
        return True

    def get_theme(self) -> str:
        """Get the current ZSH theme.

        Returns:
            Theme name or empty string.
        """
        content = self._file_ops.read_file(self.zshrc_path)
        if not content:
            return ""

        match = re.search(r'ZSH_THEME="([^"]*)"', content)
        return match.group(1) if match else ""

    def ensure_source_line(self, config_file: Path) -> bool:
        """Ensure .zshrc sources the MyShell config file.

        Args:
            config_file: Path to config file to source.

        Returns:
            True if source line exists or was added.
        """
        zshrc = self._detector.get_zshrc_path()
        content = self._file_ops.read_file(zshrc)
        if not content:
            content = ""

        source_line = f'[[ -f "{config_file}" ]] && source "{config_file}"'

        if str(config_file) in content:
            return True

        # Add source line at the end
        self._file_ops.append_file(
            zshrc,
            f"\n# MyShell_RFD Configuration\n{source_line}\n",
            backup=True,
        )

        self._logger.success("Added MyShell_RFD source line to .zshrc")
        return True

    def ensure_config_sourced(self) -> bool:
        """Ensure .zshrc sources the MyShell_RFD config file.

        Creates the config file if needed and adds source line to .zshrc.

        Returns:
            True if setup is complete.
        """
        from myshell_rfd.utils.files import CONFIG_DIR, SHELL_CONFIG_FILE

        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Create config file if it doesn't exist
        if not SHELL_CONFIG_FILE.exists():
            header = (
                "# ============================================================\n"
                "# MyShell_RFD Configuration\n"
                "# ============================================================\n"
                "# This file is managed by MyShell_RFD. Do not edit manually!\n"
                "# Your custom ZSH configuration should remain in ~/.zshrc\n"
                "#\n"
                "# To add/remove modules, use:\n"
                "#   myshell install <module>\n"
                "#   myshell uninstall <module>\n"
                "#\n"
                "# Or launch the TUI:\n"
                "#   myshell\n"
                "# ============================================================\n\n"
            )
            SHELL_CONFIG_FILE.write_text(header, encoding="utf-8")

        # Add source line to .zshrc
        return self.ensure_source_line(SHELL_CONFIG_FILE)

    def set_default_shell(self) -> bool:
        """Set ZSH as the default shell.

        Uses chsh command which requires user password.

        Returns:
            True if shell was changed successfully.
        """
        if self.is_zsh_default():
            self._logger.info("ZSH is already the default shell")
            return True

        zsh_path = self._detector.get_binary_path("zsh")
        if not zsh_path:
            self._logger.error("ZSH not found in PATH")
            return False

        self._logger.info(f"Changing default shell to ZSH ({zsh_path})...")
        # Run interactively to allow password entry
        result = self._runner.run(f"chsh -s {zsh_path}", shell=True, capture=False)

        if result.success:
            self._logger.success("Default shell changed to ZSH. Restart your terminal.")
            return True

        self._logger.error(f"Failed to change shell: {result.stderr}")
        return False

    def install_zsh_plugin(
        self,
        name: str,
        repo_url: str,
        *,
        as_theme: bool = False,
    ) -> bool:
        """Install a ZSH plugin by cloning repository.

        Args:
            name: Plugin/theme name.
            repo_url: Git repository URL.
            as_theme: Install as theme instead of plugin.

        Returns:
            True if installed successfully.
        """
        if as_theme:
            target_dir = self.zsh_custom / "themes" / name
        else:
            target_dir = self.zsh_custom / "plugins" / name

        if target_dir.exists():
            self._logger.info(f"{'Theme' if as_theme else 'Plugin'} '{name}' already installed")
            return True

        target_dir.parent.mkdir(parents=True, exist_ok=True)

        self._logger.info(f"Installing {name}...")
        result = self._runner.git_clone(repo_url, target_dir)

        if result.success:
            self._logger.success(f"Installed {name}")
            return True

        self._logger.error(f"Failed to install {name}: {result.stderr}")
        return False

    def uninstall_zsh_plugin(self, name: str, *, as_theme: bool = False) -> bool:
        """Uninstall a ZSH plugin.

        Args:
            name: Plugin/theme name.
            as_theme: Is this a theme.

        Returns:
            True if uninstalled.
        """
        import shutil

        if as_theme:
            target_dir = self.zsh_custom / "themes" / name
        else:
            target_dir = self.zsh_custom / "plugins" / name

        if not target_dir.exists():
            return True

        shutil.rmtree(target_dir)
        self._logger.success(f"Uninstalled {name}")

        # Also disable if it's a plugin
        if not as_theme:
            self.disable_omz_plugin(name)

        return True


# Global instance
_shell_manager: ShellManager | None = None


def get_shell_manager() -> ShellManager:
    """Get the global ShellManager instance."""
    global _shell_manager
    if _shell_manager is None:
        _shell_manager = ShellManager()
    return _shell_manager
