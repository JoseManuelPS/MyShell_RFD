"""Core business logic for MyShell_RFD."""

from myshell_rfd.core.config import (
    AppConfig,
    ModuleConfig,
    ProfileConfig,
    get_config,
    load_config,
    save_config,
)
from myshell_rfd.core.installer import InstallerService, get_installer
from myshell_rfd.core.module_base import (
    BaseModule,
    ConfigOnlyModule,
    GitCloneModule,
    InstallResult,
    ModuleCategory,
    ModuleInfo,
    ModuleProtocol,
)
from myshell_rfd.core.registry import ModuleRegistry, get_registry, init_registry
from myshell_rfd.core.rollback import RollbackManager, Snapshot, get_rollback_manager
from myshell_rfd.core.shell import ShellManager, get_shell_manager

__all__ = [
    # Config
    "AppConfig",
    "ModuleConfig",
    "ProfileConfig",
    "get_config",
    "load_config",
    "save_config",
    # Module base
    "BaseModule",
    "ConfigOnlyModule",
    "GitCloneModule",
    "InstallResult",
    "ModuleCategory",
    "ModuleInfo",
    "ModuleProtocol",
    # Registry
    "ModuleRegistry",
    "get_registry",
    "init_registry",
    # Shell
    "ShellManager",
    "get_shell_manager",
    # Rollback
    "RollbackManager",
    "Snapshot",
    "get_rollback_manager",
    # Installer
    "InstallerService",
    "get_installer",
]
