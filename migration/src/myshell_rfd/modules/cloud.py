"""Cloud infrastructure modules for MyShell_RFD.

Configures Terraform and OpenTofu.
"""

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    ModuleCategory,
    ModuleInfo,
)


class TerraformModule(ConfigOnlyModule):
    """Terraform configuration module.

    Configures:
    - Terraform autocompletion
    - Terraform aliases
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Terraform",
            description="Terraform IaC completion and aliases",
            category=ModuleCategory.CLOUD,
            required_binaries=["terraform"],
            provides=["terraform-completion", "terraform-aliases"],
            tags=["terraform", "iac", "hashicorp", "infrastructure"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Terraform configuration."""
        return """# Terraform completion
autoload -Uz bashcompinit && bashcompinit
complete -o nospace -C /usr/local/bin/terraform terraform

# Terraform aliases
alias tf='terraform'
alias tfi='terraform init'
alias tfp='terraform plan'
alias tfa='terraform apply'
alias tfd='terraform destroy'
alias tfo='terraform output'
alias tfs='terraform state'
alias tfv='terraform validate'
alias tff='terraform fmt'"""


class OpenTofuModule(ConfigOnlyModule):
    """OpenTofu configuration module.

    Configures:
    - OpenTofu autocompletion
    - OpenTofu aliases
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="OpenTofu",
            description="OpenTofu IaC completion and aliases",
            category=ModuleCategory.CLOUD,
            required_binaries=["tofu"],
            provides=["opentofu-completion", "opentofu-aliases"],
            tags=["opentofu", "tofu", "iac", "infrastructure", "terraform"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate OpenTofu configuration."""
        return """# OpenTofu completion
autoload -Uz bashcompinit && bashcompinit
complete -o nospace -C /usr/local/bin/tofu tofu

# OpenTofu aliases
alias tofu='tofu'
alias tfi='tofu init'
alias tfp='tofu plan'
alias tfa='tofu apply'
alias tfd='tofu destroy'
alias tfo='tofu output'
alias tfs='tofu state'
alias tfv='tofu validate'
alias tff='tofu fmt'"""
