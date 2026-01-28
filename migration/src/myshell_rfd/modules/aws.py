"""AWS CLI module for MyShell_RFD.

Configures AWS CLI autocompletion for ZSH.
"""

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    InstallResult,
    ModuleCategory,
    ModuleInfo,
)


class AWSModule(ConfigOnlyModule):
    """AWS CLI configuration module.

    Configures:
    - AWS CLI autocompletion
    - AWS completer integration with ZSH
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="AWS",
            description="AWS CLI autocompletion",
            category=ModuleCategory.CLOUD,
            required_binaries=["aws"],
            provides=["aws-completion"],
            tags=["aws", "cloud", "amazon", "cli"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate AWS configuration."""
        return """# AWS CLI Completion
autoload -Uz bashcompinit && bashcompinit
complete -C '/usr/local/bin/aws_completer' aws"""
