"""Module registry for MyShell_RFD.

Manages module discovery, registration, and lifecycle.
Supports both built-in modules and external plugins (E1).
"""

import importlib
import importlib.metadata
from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.core.module_base import BaseModule, ModuleCategory, ModuleProtocol
from myshell_rfd.utils.detect import get_detector
from myshell_rfd.utils.files import PLUGINS_DIR, get_file_ops
from myshell_rfd.utils.logger import get_logger
from myshell_rfd.utils.process import get_runner

if TYPE_CHECKING:
    from collections.abc import Iterator

    from myshell_rfd.core.config import ModuleConfig
    from myshell_rfd.core.module_base import InstallResult, ModuleInfo


# Entry point group for external plugins
PLUGIN_ENTRY_POINT = "myshell_rfd.plugins"


class ModuleRegistry:
    """Registry for discovering and managing modules.

    Handles:
    - Built-in module discovery
    - External plugin loading (E1)
    - Module instantiation with dependencies
    - Category-based filtering
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self._modules: dict[str, type[BaseModule]] = {}
        self._instances: dict[str, BaseModule] = {}
        self._logger = get_logger()

    def register(self, module_class: type[BaseModule]) -> None:
        """Register a module class.

        Args:
            module_class: The module class to register.
        """
        # Create temporary instance to get info
        instance = self._create_instance(module_class)
        name = instance.info.name

        if name in self._modules:
            self._logger.warn(f"Module '{name}' already registered, overwriting")

        self._modules[name] = module_class
        self._instances[name] = instance
        self._logger.debug(f"Registered module: {name}")

    def _create_instance(self, module_class: type[BaseModule]) -> BaseModule:
        """Create a module instance with dependencies.

        Args:
            module_class: The module class to instantiate.

        Returns:
            Module instance.
        """
        return module_class(
            logger=get_logger(),
            file_ops=get_file_ops(),
            runner=get_runner(),
            detector=get_detector(),
        )

    def get(self, name: str) -> BaseModule | None:
        """Get a module instance by name.

        Args:
            name: Module name (case-insensitive).

        Returns:
            Module instance or None if not found.
        """
        # Case-insensitive lookup
        name_lower = name.lower()
        for registered_name, instance in self._instances.items():
            if registered_name.lower() == name_lower:
                return instance
        return None

    def get_all(self) -> "Iterator[BaseModule]":
        """Get all registered module instances.

        Yields:
            Module instances.
        """
        yield from self._instances.values()

    def get_by_category(self, category: ModuleCategory) -> "Iterator[BaseModule]":
        """Get modules by category.

        Args:
            category: Category to filter by.

        Yields:
            Matching module instances.
        """
        for instance in self._instances.values():
            if instance.category == category:
                yield instance

    def get_available(self) -> "Iterator[BaseModule]":
        """Get modules that can be installed (prerequisites met).

        Yields:
            Available module instances.
        """
        for instance in self._instances.values():
            if instance.check_available():
                yield instance

    def get_installed(self) -> "Iterator[BaseModule]":
        """Get modules that are already configured.

        Yields:
            Installed module instances.
        """
        for instance in self._instances.values():
            if instance.check_installed():
                yield instance

    def list_names(self) -> list[str]:
        """Get sorted list of module names.

        Returns:
            List of module names.
        """
        return sorted(self._modules.keys())

    def list_info(self) -> list["ModuleInfo"]:
        """Get list of module info objects.

        Returns:
            List of ModuleInfo sorted by name.
        """
        return sorted(
            [inst.info for inst in self._instances.values()],
            key=lambda i: i.name,
        )

    def install_module(self, name: str, config: "ModuleConfig") -> "InstallResult":
        """Install a module by name.

        Args:
            name: Module name.
            config: Module configuration.

        Returns:
            Installation result.
        """
        from myshell_rfd.core.module_base import InstallResult

        module = self.get(name)
        if module is None:
            return InstallResult(
                success=False,
                message=f"Module '{name}' not found",
            )

        return module.install(config)

    def uninstall_module(self, name: str) -> "InstallResult":
        """Uninstall a module by name.

        Args:
            name: Module name.

        Returns:
            Uninstallation result.
        """
        from myshell_rfd.core.module_base import InstallResult

        module = self.get(name)
        if module is None:
            return InstallResult(
                success=False,
                message=f"Module '{name}' not found",
            )

        return module.uninstall()

    def discover_builtin(self) -> int:
        """Discover and register built-in modules.

        Uses the explicit BUILTIN_MODULES list from modules/__init__.py
        instead of dynamic introspection with dir().

        Returns:
            Number of modules registered.
        """
        from myshell_rfd.modules import BUILTIN_MODULES

        count = 0
        for module_class in BUILTIN_MODULES:
            try:
                self.register(module_class)
                count += 1
            except TypeError:
                # Abstract class or instantiation error, skip
                self._logger.debug(f"Could not register {module_class.__name__}")

        self._logger.debug(f"Discovered {count} built-in modules")
        return count

    def discover_plugins(self) -> int:
        """Discover and load external plugins (E1).

        Loads plugins from:
        1. Entry points (installed packages)
        2. Plugin directory (~/.myshell_rfd/plugins/)

        Returns:
            Number of plugins loaded.
        """
        count = 0

        # Load from entry points
        count += self._load_entry_points()

        # Load from plugins directory
        count += self._load_plugin_directory()

        self._logger.debug(f"Discovered {count} plugins")
        return count

    def _load_entry_points(self) -> int:
        """Load plugins from entry points.

        Returns:
            Number of plugins loaded.
        """
        count = 0

        try:
            eps = importlib.metadata.entry_points(group=PLUGIN_ENTRY_POINT)
            for ep in eps:
                try:
                    plugin_class = ep.load()
                    if isinstance(plugin_class, type) and issubclass(plugin_class, BaseModule):
                        self.register(plugin_class)
                        count += 1
                        self._logger.debug(f"Loaded plugin from entry point: {ep.name}")
                except Exception as e:
                    self._logger.warn(f"Failed to load plugin {ep.name}: {e}")
        except Exception as e:
            self._logger.debug(f"Error loading entry points: {e}")

        return count

    def _load_plugin_directory(self) -> int:
        """Load plugins from plugin directory.

        Returns:
            Number of plugins loaded.
        """
        count = 0

        if not PLUGINS_DIR.exists():
            return count

        # Look for Python files in plugins directory
        for plugin_file in PLUGINS_DIR.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem,
                    plugin_file,
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find module classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseModule)
                            and attr is not BaseModule
                        ):
                            try:
                                self.register(attr)
                                count += 1
                                self._logger.debug(f"Loaded plugin: {attr_name}")
                            except TypeError:
                                pass

            except Exception as e:
                self._logger.warn(f"Failed to load plugin {plugin_file.name}: {e}")

        return count

    def discover_all(self) -> int:
        """Discover all modules (built-in and plugins).

        Returns:
            Total number of modules registered.
        """
        count = 0
        count += self.discover_builtin()
        count += self.discover_plugins()
        return count


# Global registry instance
_registry: ModuleRegistry | None = None


def get_registry() -> ModuleRegistry:
    """Get the global module registry.

    Returns:
        The module registry instance.
    """
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
    return _registry


def init_registry() -> ModuleRegistry:
    """Initialize and populate the module registry.

    Returns:
        The populated registry.
    """
    registry = get_registry()
    registry.discover_all()
    return registry
