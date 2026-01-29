"""Kubernetes tools modules for MyShell_RFD.

Configures kubectl, helm, minikube, eksctl, oc, rosa, and tridentctl.
"""

from pathlib import Path

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    BaseModule,
    ConfigOnlyModule,
    InstallResult,
    ModuleCategory,
    ModuleInfo,
)


class KubectlModule(ConfigOnlyModule):
    """Kubectl configuration module.

    Configures:
    - Kubectl autocompletion
    - Kubectl aliases (k, kgp, kgs, etc.)
    - Optional Krew installation
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Kubectl",
            description="Kubernetes CLI with aliases and completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["kubectl"],
            provides=["kubectl-completion", "kubectl-aliases"],
            tags=["kubernetes", "k8s", "kubectl", "devops"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate kubectl configuration."""
        content = """# Kubectl completion and aliases
source <(kubectl completion zsh)
compdef _kubectl kubectl

# Kubectl aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgn='kubectl get nodes'
alias kgd='kubectl get deployments'
alias kga='kubectl get all'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kdp='kubectl describe pod'
alias kds='kubectl describe svc'
alias kdd='kubectl describe deployment'
alias kl='kubectl logs -f'
alias kex='kubectl exec -it'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'

# Kubectl completion for alias
compdef k='kubectl'"""

        # Add Krew path if installed
        if config.settings.get("krew", False):
            content += """

# Krew
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH\""""

        return content

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install kubectl with optional Krew."""
        result = super().install(config)

        if result.success and config.settings.get("install_krew", False):
            self._install_krew()

        return result

    def _install_krew(self) -> bool:
        """Install Krew kubectl plugin manager."""
        import os
        import tempfile

        self._logger.info("Installing Krew...")

        # Detect OS and arch
        os_name = os.uname().sysname.lower()
        arch = os.uname().machine
        if arch == "x86_64":
            arch = "amd64"
        elif arch == "aarch64":
            arch = "arm64"

        krew_name = f"krew-{os_name}_{arch}"

        with tempfile.TemporaryDirectory() as tmpdir:
            # Download Krew
            url = f"https://github.com/kubernetes-sigs/krew/releases/latest/download/{krew_name}.tar.gz"
            tar_path = Path(tmpdir) / f"{krew_name}.tar.gz"

            result = self._runner.download(url, tar_path, timeout=120.0)

            if not result.success:
                self._logger.error(f"Failed to download Krew: {result.stderr}")
                return False

            # Extract
            self._runner.run(["tar", "-xzf", str(tar_path), "-C", tmpdir])

            # Install
            krew_bin = f"{tmpdir}/{krew_name}"
            result = self._runner.run([krew_bin, "install", "krew"])

            if result.success:
                self._logger.success("Krew installed")
                return True

            self._logger.error(f"Failed to install Krew: {result.stderr}")
            return False


class HelmModule(ConfigOnlyModule):
    """Helm configuration module.

    Configures:
    - Helm autocompletion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Helm",
            description="Helm package manager completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["helm"],
            provides=["helm-completion"],
            tags=["helm", "kubernetes", "k8s", "charts"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Helm configuration."""
        return """# Helm completion
source <(helm completion zsh)
compdef _helm helm"""


class MinikubeModule(ConfigOnlyModule):
    """Minikube configuration module.

    Configures:
    - Minikube autocompletion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Minikube",
            description="Minikube local Kubernetes completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["minikube"],
            provides=["minikube-completion"],
            tags=["minikube", "kubernetes", "k8s", "local"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Minikube configuration."""
        return """# Minikube completion
source <(minikube completion zsh)
compdef _minikube minikube"""


class EksctlModule(ConfigOnlyModule):
    """Eksctl configuration module.

    Configures:
    - Eksctl autocompletion for AWS EKS
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Eksctl",
            description="AWS EKS CLI completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["eksctl"],
            provides=["eksctl-completion"],
            tags=["eksctl", "aws", "eks", "kubernetes"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Eksctl configuration."""
        return """# Eksctl completion
source <(eksctl completion zsh)
compdef _eksctl eksctl"""


class OCModule(ConfigOnlyModule):
    """OpenShift CLI configuration module.

    Configures:
    - OC autocompletion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="OC",
            description="OpenShift CLI completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["oc"],
            provides=["oc-completion"],
            tags=["openshift", "oc", "redhat", "kubernetes"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate OC configuration."""
        return """# OpenShift CLI completion
source <(oc completion zsh)
compdef _oc oc"""


class RosaModule(ConfigOnlyModule):
    """ROSA CLI configuration module.

    Configures:
    - ROSA autocompletion for Red Hat OpenShift on AWS
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Rosa",
            description="Red Hat OpenShift on AWS CLI completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["rosa"],
            provides=["rosa-completion"],
            tags=["rosa", "openshift", "aws", "redhat"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate ROSA configuration."""
        return """# ROSA CLI completion
source <(rosa completion zsh)
compdef _rosa rosa"""


class TridentctlModule(ConfigOnlyModule):
    """Tridentctl configuration module.

    Configures:
    - Tridentctl autocompletion
    - Astra alias
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Tridentctl",
            description="NetApp Trident CLI completion",
            category=ModuleCategory.KUBERNETES,
            required_binaries=["tridentctl"],
            provides=["tridentctl-completion"],
            tags=["trident", "netapp", "storage", "kubernetes"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Tridentctl configuration."""
        return """# Tridentctl completion
source <(tridentctl completion zsh)
compdef _tridentctl tridentctl

# Astra alias
alias astra='tridentctl'"""
