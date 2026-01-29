"""MyShell_RFD modules.

This package contains all built-in modules for tool configuration.
Each module is a class that extends BaseModule or one of its variants.
"""

# Import all modules to trigger registration
from myshell_rfd.modules.aws import AWSModule
from myshell_rfd.modules.cloud import OpenTofuModule, TerraformModule
from myshell_rfd.modules.containers import DockerModule, PodmanModule
from myshell_rfd.modules.kubernetes import (
    EksctlModule,
    HelmModule,
    KubectlModule,
    MinikubeModule,
    OCModule,
    RosaModule,
    TridentctlModule,
)
from myshell_rfd.modules.myshell import MyShellModule
from myshell_rfd.modules.shell_plugins import (
    ZshAutocompletionsModule,
    ZshAutosuggestionsModule,
    ZshSyntaxHighlightingModule,
)
from myshell_rfd.modules.themes import PowerLevel10KModule
from myshell_rfd.modules.tools import (
    BatcatModule,
    FZFModule,
    KPluginModule,
    NVMModule,
    PLSModule,
    PythonVenvModule,
)
from myshell_rfd.modules.vcs import GitHubModule, GitLabModule

# Explicit list of all built-in module classes for registration.
# This list is used by the registry to discover modules without dynamic introspection.
# When adding a new module, add it here AND import it above.
BUILTIN_MODULES = [
    # MyShell (self-configuration)
    MyShellModule,
    # AWS
    AWSModule,
    # Containers
    DockerModule,
    PodmanModule,
    # Kubernetes
    KubectlModule,
    HelmModule,
    MinikubeModule,
    EksctlModule,
    OCModule,
    RosaModule,
    TridentctlModule,
    # Cloud
    TerraformModule,
    OpenTofuModule,
    # Tools
    FZFModule,
    BatcatModule,
    PLSModule,
    PythonVenvModule,
    NVMModule,
    KPluginModule,
    # VCS
    GitHubModule,
    GitLabModule,
    # Shell plugins
    ZshAutosuggestionsModule,
    ZshAutocompletionsModule,
    ZshSyntaxHighlightingModule,
    # Themes
    PowerLevel10KModule,
]

__all__ = [
    # Module list
    "BUILTIN_MODULES",
    # MyShell (self-configuration)
    "MyShellModule",
    # AWS
    "AWSModule",
    # Containers
    "DockerModule",
    "PodmanModule",
    # Kubernetes
    "KubectlModule",
    "HelmModule",
    "MinikubeModule",
    "EksctlModule",
    "OCModule",
    "RosaModule",
    "TridentctlModule",
    # Cloud
    "TerraformModule",
    "OpenTofuModule",
    # Tools
    "FZFModule",
    "BatcatModule",
    "PLSModule",
    "PythonVenvModule",
    "NVMModule",
    "KPluginModule",
    # VCS
    "GitHubModule",
    "GitLabModule",
    # Shell plugins
    "ZshAutosuggestionsModule",
    "ZshAutocompletionsModule",
    "ZshSyntaxHighlightingModule",
    # Themes
    "PowerLevel10KModule",
]
