"""Installation service for MyShell_RFD.

Orchestrates module installation with rollback support,
offline caching (E5), and auto-detection (E3).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.core.config import ModuleConfig, ModuleState, get_config, save_config
from myshell_rfd.core.registry import get_registry
from myshell_rfd.core.rollback import get_rollback_manager
from myshell_rfd.core.shell import get_shell_manager
from myshell_rfd.utils.detect import get_detector
from myshell_rfd.utils.files import CACHE_DIR, SHELL_CONFIG_FILE, get_file_ops
from myshell_rfd.utils.logger import get_logger
from myshell_rfd.utils.process import get_runner

if TYPE_CHECKING:
    from myshell_rfd.core.module_base import BaseModule, InstallResult
    from myshell_rfd.core.rollback import Snapshot


@dataclass
class PrerequisiteStatus:
    """Status of system prerequisites.

    Attributes:
        zsh_installed: Whether ZSH is installed.
        zsh_default: Whether ZSH is the default shell.
        git_installed: Whether git is installed.
        curl_installed: Whether curl is installed.
        omz_installed: Whether Oh My Zsh is installed.
        config_sourced: Whether .zshrc sources MyShell config.
    """

    zsh_installed: bool
    zsh_default: bool
    git_installed: bool
    curl_installed: bool
    omz_installed: bool
    config_sourced: bool

    @property
    def all_ok(self) -> bool:
        """Check if all prerequisites are met."""
        return all([
            self.zsh_installed,
            self.zsh_default,
            self.git_installed,
            self.curl_installed,
        ])

    @property
    def missing(self) -> list[str]:
        """Get list of missing prerequisites."""
        issues = []
        if not self.zsh_installed:
            issues.append("zsh")
        if not self.git_installed:
            issues.append("git")
        if not self.curl_installed:
            issues.append("curl")
        if self.zsh_installed and not self.zsh_default:
            issues.append("zsh not default shell")
        return issues


class InstallerService:
    """Orchestrates module installation and configuration.

    Features:
    - Rollback-safe installation (E4)
    - Offline caching support (E5)
    - Automatic tool detection (E3)
    - Profile-aware installation (E2)
    """

    def __init__(self, *, offline: bool = False) -> None:
        """Initialize installer service.

        Args:
            offline: Enable offline mode.
        """
        self._offline = offline
        self._logger = get_logger()
        self._file_ops = get_file_ops()
        self._runner = get_runner()
        self._detector = get_detector()
        self._registry = get_registry()
        self._shell = get_shell_manager()
        self._rollback = get_rollback_manager()

    def check_prerequisites(self) -> list[str]:
        """Check installation prerequisites.

        Returns:
            List of missing prerequisites.
        """
        missing = []

        if not self._shell.is_zsh_installed():
            missing.append("zsh")

        if not self._detector.check_binary("git"):
            missing.append("git")

        if not self._detector.check_binary("curl"):
            missing.append("curl")

        return missing

    def install_prerequisites(self) -> bool:
        """Install missing prerequisites.

        Returns:
            True if all prerequisites are installed.
        """
        missing = self.check_prerequisites()

        if not missing:
            return True

        self._logger.info(f"Installing prerequisites: {', '.join(missing)}")

        # Detect package manager
        pkg_mgr = None
        for mgr, cmd in [("apt", "apt-get"), ("dnf", "dnf"), ("apk", "apk")]:
            if self._detector.check_binary(cmd):
                pkg_mgr = cmd
                break

        if not pkg_mgr:
            self._logger.error("No supported package manager found")
            return False

        # Install packages
        packages = " ".join(missing)

        if pkg_mgr == "apt-get":
            cmd = f"sudo apt-get update && sudo apt-get install -y {packages}"
        elif pkg_mgr == "dnf":
            cmd = f"sudo dnf install -y {packages}"
        elif pkg_mgr == "apk":
            cmd = f"sudo apk add {packages}"
        else:
            return False

        result = self._runner.run(cmd, shell=True)

        if result.success:
            self._logger.success("Prerequisites installed")
            return True

        self._logger.error(f"Failed to install prerequisites: {result.stderr}")
        return False

    def get_prerequisites_status(self) -> PrerequisiteStatus:
        """Get detailed prerequisites status.

        Returns:
            PrerequisiteStatus with all checks.
        """
        zshrc = self._detector.get_zshrc_path()
        zshrc_content = self._file_ops.read_file(zshrc) or ""
        config_sourced = str(SHELL_CONFIG_FILE) in zshrc_content

        return PrerequisiteStatus(
            zsh_installed=self._shell.is_zsh_installed(),
            zsh_default=self._shell.is_zsh_default(),
            git_installed=self._detector.check_binary("git"),
            curl_installed=self._detector.check_binary("curl"),
            omz_installed=self._shell.is_omz_installed(),
            config_sourced=config_sourced,
        )

    def fix_prerequisites(self, *, change_shell: bool = False) -> bool:
        """Install missing prerequisites and optionally change default shell.

        Args:
            change_shell: Also change default shell to ZSH if needed.

        Returns:
            True if all issues were fixed.
        """
        all_fixed = True

        # Install missing packages
        missing = self.check_prerequisites()
        if missing:
            if not self.install_prerequisites():
                all_fixed = False

        # Change default shell if requested
        if change_shell and not self._shell.is_zsh_default():
            if not self._shell.set_default_shell():
                all_fixed = False

        # Ensure config is sourced
        self._shell.ensure_config_sourced()

        return all_fixed

    def ensure_omz(self) -> bool:
        """Ensure Oh My Zsh is installed.

        Returns:
            True if Oh My Zsh is available.
        """
        if self._shell.is_omz_installed():
            return True

        if self._offline:
            self._logger.error("Oh My Zsh not installed and offline mode is enabled")
            return False

        return self._shell.install_omz()

    def install_module(
        self,
        name: str,
        *,
        auto_yes: bool = False,
        settings: dict | None = None,
    ) -> "InstallResult":
        """Install a single module.

        Args:
            name: Module name.
            auto_yes: Skip confirmation prompts.
            settings: Module-specific settings.

        Returns:
            Installation result.
        """
        from myshell_rfd.core.module_base import InstallResult

        module = self._registry.get(name)
        if not module:
            return InstallResult(
                success=False,
                message=f"Module '{name}' not found",
            )

        # Check availability
        if not module.check_available():
            return InstallResult(
                success=False,
                message=f"Module '{name}' prerequisites not met",
            )

        # Create snapshot before installation
        zshrc = self._detector.get_shell_config_file()
        snapshot = self._rollback.create_snapshot(
            f"Before installing {name}",
            [zshrc],
            modules=[name],
        )

        # Get or create module config
        config = get_config()
        profile = config.current_profile

        if name not in profile.modules:
            profile.modules[name] = ModuleConfig()

        module_config = profile.modules[name]
        if settings:
            module_config.settings.update(settings)

        # Install
        self._logger.info(f"Installing {name}...")
        result = module.install(module_config)

        if result.success:
            # Update config
            module_config.enabled = True
            module_config.state = ModuleState.CONFIGURED
            from datetime import datetime

            module_config.installed_at = datetime.now()
            save_config()

            self._logger.success(f"{name} installed successfully")
        else:
            self._logger.error(f"Failed to install {name}: {result.message}")

        return result

    def uninstall_module(self, name: str) -> "InstallResult":
        """Uninstall a module.

        Args:
            name: Module name.

        Returns:
            Uninstallation result.
        """
        from myshell_rfd.core.module_base import InstallResult

        module = self._registry.get(name)
        if not module:
            return InstallResult(
                success=False,
                message=f"Module '{name}' not found",
            )

        # Create snapshot before uninstallation
        zshrc = self._detector.get_shell_config_file()
        self._rollback.create_snapshot(
            f"Before uninstalling {name}",
            [zshrc],
            modules=[name],
        )

        # Uninstall
        result = module.uninstall()

        if result.success:
            # Update config
            config = get_config()
            profile = config.current_profile

            if name in profile.modules:
                profile.modules[name].enabled = False
                profile.modules[name].state = ModuleState.NOT_INSTALLED

            save_config()
            self._logger.success(f"{name} uninstalled")

        return result

    def install_all(
        self,
        *,
        auto_yes: bool = False,
        skip_unavailable: bool = True,
    ) -> dict[str, "InstallResult"]:
        """Install all available modules.

        Args:
            auto_yes: Skip confirmation prompts.
            skip_unavailable: Skip modules with missing prerequisites.

        Returns:
            Dictionary mapping module names to results.
        """
        results: dict[str, "InstallResult"] = {}

        for module in self._registry.get_available():
            result = self.install_module(module.name, auto_yes=auto_yes)
            results[module.name] = result

        return results



    def rollback(self, snapshot_id: str) -> bool:
        """Rollback to a snapshot.

        Args:
            snapshot_id: Snapshot ID.

        Returns:
            True if rollback succeeded.
        """
        return self._rollback.rollback(snapshot_id)

    def list_snapshots(self) -> list["Snapshot"]:
        """List available snapshots.

        Returns:
            List of snapshots.
        """
        return list(self._rollback.list_snapshots())

    def clean_config(self) -> bool:
        """Remove all MyShell_RFD configuration.

        Cleans both the MyShell config file and the source line in .zshrc.

        Returns:
            True if cleaned successfully.
        """
        import re

        config_file = SHELL_CONFIG_FILE
        zshrc = self._detector.get_zshrc_path()

        # Create snapshot first (backup both files)
        self._rollback.create_snapshot(
            "Before clean",
            [config_file, zshrc],
        )

        # Clean the MyShell config file (remove all module sections)
        content = self._file_ops.read_file(config_file)
        if content:
            # Find and remove all MyShell_RFD sections
            # Matches legacy: # >>> ... # <<< ...
            # Matches new: #  [...] ... (until next marker or EOF)
            
            # Since we don't have end markers for new sections, we can't easily use a simple regex for everything without risk.
            # However, we can use the file_ops.remove_from_config logic if we iterate over installed modules.
            # But clean_config should remove EVERYTHING even unknown modules.
            
            # For robust cleaning of the new format without end markers, we might just look for the start lines.
            lines = content.splitlines(keepends=True)
            new_lines = []
            
            # Keep header
            header_end_marker = "# ============================================================\n"
            in_header = True
            
            for line in lines:
                if in_header:
                    new_lines.append(line)
                    if line == header_end_marker and len(new_lines) > 5: # simple heaurestic to identify our header
                         # The header ends with a blank line usually, but let's just stop "header protection" after the separator
                         pass
                    # Actually, the header is constant. We can just keep it.
                    continue
                
                # If we encounter a section start, skip it and subsequent lines until we find something that isn't a section content?
                # Actually, simply wiping the file content after the header is safer and cleaner for "clean_config".
                # The header is approximately the first 15 lines.
                pass

            # Simpler approach: If we want to nuke all config, and we control the file, 
            # and the file is ONLY for myshell config (as we moved it to ~/.myshell_rfd/config),
            # we can just truncate it to the header!
            
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
            
            self._file_ops.write_file(config_file, header, backup=False)

        # Remove the source line from .zshrc
        zshrc_content = self._file_ops.read_file(zshrc)
        if zshrc_content and str(config_file) in zshrc_content:
            # Remove the MyShell_RFD source section
            pattern = r"\n?# MyShell_RFD Configuration\n\[\[.*?myshell_rfd.*?\]\].*?\n?"
            new_zshrc = re.sub(pattern, "", zshrc_content, flags=re.DOTALL)

            # Clean up extra blank lines
            while "\n\n\n" in new_zshrc:
                new_zshrc = new_zshrc.replace("\n\n\n", "\n\n")

            self._file_ops.write_file(zshrc, new_zshrc, backup=False)

        # Reset config
        config = get_config()
        for module_config in config.current_profile.modules.values():
            module_config.enabled = False
            module_config.state = ModuleState.NOT_INSTALLED

        save_config()

        self._logger.success("Configuration cleaned")
        return True

    def get_cache_dir(self, name: str) -> Path:
        """Get cache directory for a module (E5).

        Args:
            name: Module name.

        Returns:
            Path to cache directory.
        """
        cache_dir = CACHE_DIR / name
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir


# Global instance
_installer: InstallerService | None = None


def get_installer(*, offline: bool = False) -> InstallerService:
    """Get the installer service instance.

    Args:
        offline: Enable offline mode.

    Returns:
        InstallerService instance.
    """
    global _installer
    if _installer is None or _installer._offline != offline:
        _installer = InstallerService(offline=offline)
    return _installer
