"""Plugin system for MyShell_RFD.

This package provides the plugin infrastructure for extending MyShell_RFD
with custom modules.

## Creating a Plugin

1. Create a Python package with your module class
2. Register via entry points in pyproject.toml
3. Or place .py files in ~/.myshell_rfd/plugins/

## Entry Point Registration

In your package's pyproject.toml:

```toml
[project.entry-points."myshell_rfd.plugins"]
my_module = "my_package.module:MyModule"
```

## Plugin Directory

Place Python files directly in ~/.myshell_rfd/plugins/:

```python
# ~/.myshell_rfd/plugins/my_module.py
from myshell_rfd.core.module_base import ConfigOnlyModule, ModuleInfo, ModuleCategory

class MyModule(ConfigOnlyModule):
    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="MyModule",
            description="My custom module",
            category=ModuleCategory.TOOLS,
        )

    def get_config_content(self, config):
        return "# My custom configuration"
```

The module will be automatically discovered and loaded.
"""

from myshell_rfd.plugins.loader import PluginLoader, discover_plugins

__all__ = ["PluginLoader", "discover_plugins"]
