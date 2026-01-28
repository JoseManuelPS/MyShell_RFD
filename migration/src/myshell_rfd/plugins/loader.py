"""Plugin loader for MyShell_RFD.

Handles discovery and loading of external plugins from:
1. Entry points (installed packages)
2. Plugin directory (~/.myshell_rfd/plugins/)
"""

import importlib
import importlib.metadata
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.core.module_base import BaseModule
from myshell_rfd.utils.files import PLUGINS_DIR
from myshell_rfd.utils.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

# Entry point group name
ENTRY_POINT_GROUP = "myshell_rfd.plugins"


@dataclass
class PluginInfo:
    """Information about a loaded plugin.

    Attributes:
        name: Plugin name.
        module_class: The module class.
        source: Where the plugin was loaded from.
        version: Plugin version if available.
    """

    name: str
    module_class: type[BaseModule]
    source: str
    version: str = ""


class PluginLoader:
    """Loads and manages external plugins.

    Discovers plugins from entry points and plugin directory,
    validates them, and provides access to loaded modules.
    """

    def __init__(self) -> None:
        """Initialize the plugin loader."""
        self._logger = get_logger()
        self._plugins: dict[str, PluginInfo] = {}

    @property
    def plugins(self) -> dict[str, PluginInfo]:
        """Get loaded plugins."""
        return self._plugins

    def discover_all(self) -> int:
        """Discover all plugins.

        Returns:
            Number of plugins loaded.
        """
        count = 0
        count += self._load_entry_points()
        count += self._load_directory_plugins()
        return count

    def _load_entry_points(self) -> int:
        """Load plugins from entry points.

        Returns:
            Number of plugins loaded.
        """
        count = 0

        try:
            eps = importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)

            for ep in eps:
                try:
                    module_class = ep.load()

                    if not self._validate_plugin(module_class, ep.name):
                        continue

                    # Get version from package if available
                    version = ""
                    try:
                        dist = ep.dist
                        if dist:
                            version = dist.version
                    except Exception:
                        pass

                    self._plugins[ep.name] = PluginInfo(
                        name=ep.name,
                        module_class=module_class,
                        source=f"entry_point:{ep.value}",
                        version=version,
                    )

                    self._logger.debug(f"Loaded plugin from entry point: {ep.name}")
                    count += 1

                except Exception as e:
                    self._logger.warn(f"Failed to load plugin {ep.name}: {e}")

        except Exception as e:
            self._logger.debug(f"Error loading entry points: {e}")

        return count

    def _load_directory_plugins(self) -> int:
        """Load plugins from plugin directory.

        Returns:
            Number of plugins loaded.
        """
        count = 0

        if not PLUGINS_DIR.exists():
            PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
            return count

        for plugin_file in PLUGINS_DIR.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue

            try:
                module_name = f"myshell_rfd_plugin_{plugin_file.stem}"

                # Load the module
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    plugin_file,
                )

                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find module classes
                for attr_name in dir(module):
                    if attr_name.startswith("_"):
                        continue

                    attr = getattr(module, attr_name)

                    if not self._is_module_class(attr):
                        continue

                    if not self._validate_plugin(attr, attr_name):
                        continue

                    plugin_name = f"{plugin_file.stem}.{attr_name}"

                    self._plugins[plugin_name] = PluginInfo(
                        name=attr_name,
                        module_class=attr,
                        source=f"file:{plugin_file}",
                    )

                    self._logger.debug(f"Loaded plugin from file: {plugin_name}")
                    count += 1

            except Exception as e:
                self._logger.warn(f"Failed to load plugin {plugin_file.name}: {e}")

        return count

    def _is_module_class(self, obj: object) -> bool:
        """Check if object is a module class.

        Args:
            obj: Object to check.

        Returns:
            True if it's a valid module class.
        """
        if not isinstance(obj, type):
            return False

        if not issubclass(obj, BaseModule):
            return False

        if obj is BaseModule:
            return False

        # Check if it's from our own package (skip built-ins)
        module = getattr(obj, "__module__", "")
        if module.startswith("myshell_rfd.modules"):
            return False

        return True

    def _validate_plugin(self, module_class: type, name: str) -> bool:
        """Validate a plugin class.

        Args:
            module_class: The class to validate.
            name: Plugin name for logging.

        Returns:
            True if valid.
        """
        if not isinstance(module_class, type):
            self._logger.warn(f"Plugin {name}: Not a class")
            return False

        if not issubclass(module_class, BaseModule):
            self._logger.warn(f"Plugin {name}: Must extend BaseModule")
            return False

        # Try to instantiate (will fail if abstract)
        try:
            from myshell_rfd.utils.detect import get_detector
            from myshell_rfd.utils.files import get_file_ops
            from myshell_rfd.utils.process import get_runner

            instance = module_class(
                logger=get_logger(),
                file_ops=get_file_ops(),
                runner=get_runner(),
                detector=get_detector(),
            )

            # Check required property
            _ = instance.info

        except TypeError as e:
            self._logger.debug(f"Plugin {name}: Abstract class, skipping ({e})")
            return False
        except Exception as e:
            self._logger.warn(f"Plugin {name}: Validation failed ({e})")
            return False

        return True

    def get_module_classes(self) -> "Iterator[type[BaseModule]]":
        """Get all loaded module classes.

        Yields:
            Module classes from loaded plugins.
        """
        for plugin in self._plugins.values():
            yield plugin.module_class

    def get_plugin_info(self, name: str) -> PluginInfo | None:
        """Get info about a specific plugin.

        Args:
            name: Plugin name.

        Returns:
            PluginInfo or None if not found.
        """
        return self._plugins.get(name)

    def reload_plugins(self) -> int:
        """Reload all plugins.

        Returns:
            Number of plugins loaded.
        """
        self._plugins.clear()
        return self.discover_all()


# Global loader instance
_loader: PluginLoader | None = None


def get_plugin_loader() -> PluginLoader:
    """Get the global plugin loader."""
    global _loader
    if _loader is None:
        _loader = PluginLoader()
    return _loader


def discover_plugins() -> int:
    """Discover all plugins.

    Returns:
        Number of plugins discovered.
    """
    loader = get_plugin_loader()
    return loader.discover_all()
