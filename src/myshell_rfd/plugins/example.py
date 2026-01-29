"""Example plugin for MyShell_RFD.

This file demonstrates how to create a custom module plugin.
Copy this to ~/.myshell_rfd/plugins/ and modify as needed.
"""

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    ModuleCategory,
    ModuleInfo,
)


class ExampleModule(ConfigOnlyModule):
    """Example custom module.

    This module demonstrates how to create a plugin that:
    - Checks for a binary dependency
    - Adds custom configuration to .zshrc
    - Provides aliases and functions
    """

    @property
    def info(self) -> ModuleInfo:
        """Module metadata."""
        return ModuleInfo(
            name="Example",
            description="Example custom module for demonstration",
            category=ModuleCategory.TOOLS,
            required_binaries=[],  # Add required binaries here
            optional_binaries=["example-cli"],
            provides=["example-aliases"],
            tags=["example", "demo", "custom"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate configuration content.

        Args:
            config: Module configuration with user settings.

        Returns:
            Configuration to add to .zshrc.
        """
        # Access user settings
        greeting = config.settings.get("greeting", "Hello")

        return f'''# Example Module Configuration
# Greeting: {greeting}

# Example aliases
alias example-hello='echo "{greeting} from MyShell_RFD!"'
alias example-time='date +"%H:%M:%S"'

# Example function
example_info() {{
    echo "Example plugin loaded"
    echo "Greeting: {greeting}"
    echo "User: $USER"
}}'''


# You can define multiple modules in one file
class AnotherExampleModule(ConfigOnlyModule):
    """Another example module."""

    @property
    def info(self) -> ModuleInfo:
        """Module metadata."""
        return ModuleInfo(
            name="AnotherExample",
            description="Another example module",
            category=ModuleCategory.OTHER,
            tags=["example"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate configuration."""
        return "# Another example module\nalias another-example='echo Another example'"
