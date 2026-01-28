"""Installation service for MyShell_RFD.

Orchestrates module installation with rollback support,
offline caching (E5), and auto-detection (E3).
"""

from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.core.config import ModuleConfig, ModuleState, get_config, save_config
from myshell_rfd.core.registry import get_registry
from myshell_rfd.core.rollback import get_rollback_manager
from myshell_rfd.core.shell import get_shell_manager
from myshell_rfd.utils.detect import get_detector
from myshell_rfd.utils.files import CACHE_DIR, get_file_ops
from myshell_rfd.utils.logger import get_logger
from myshell_rfd.utils.process import get_runner

if TYPE_CHECKING:
    from myshell_rfd.core.module_base import BaseModule, InstallResult
    from myshell_rfd.core.rollback import Snapshot


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

    def auto_detect_and_configure(self) -> list[str]:
        """Auto-detect installed tools and configure matching modules (E3).

        Returns:
            List of modules that were configured.
        """
        configured = []

        self._logger.info("Scanning for installed tools...")

        for module in self._registry.get_all():
            if module.check_available() and not module.check_installed():
                self._logger.debug(f"Auto-configuring {module.name}")
                result = self.install_module(module.name, auto_yes=True)
                if result.success:
                    configured.append(module.name)

        if configured:
            self._logger.success(f"Auto-configured {len(configured)} modules")
        else:
            self._logger.info("No new modules to configure")

        return configured

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

        Returns:
            True if cleaned successfully.
        """
        zshrc = self._detector.get_shell_config_file()

        # Create snapshot first
        self._rollback.create_snapshot(
            "Before clean",
            [zshrc],
        )

        # Remove all module sections
        content = self._file_ops.read_file(zshrc)
        if not content:
            return True

        # Find and remove all MyShell_RFD sections
        import re

        pattern = r"\n?# >>> MyShell_RFD \[[^\]]+\].*?# <<< MyShell_RFD \[[^\]]+\]\n?"
        new_content = re.sub(pattern, "", content, flags=re.DOTALL)

        # Clean up extra blank lines
        while "\n\n\n" in new_content:
            new_content = new_content.replace("\n\n\n", "\n\n")

        self._file_ops.write_file(zshrc, new_content, backup=True)

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
