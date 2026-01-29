"""Version control system modules for MyShell_RFD.

Configures GitHub CLI and GitLab CLI.
"""

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    ModuleCategory,
    ModuleInfo,
)


class GitHubModule(ConfigOnlyModule):
    """GitHub CLI configuration module.

    Configures:
    - GitHub CLI (gh) autocompletion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="GitHub",
            description="GitHub CLI completion",
            category=ModuleCategory.VCS,
            required_binaries=["gh"],
            provides=["gh-completion"],
            tags=["github", "gh", "git", "vcs"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate GitHub CLI configuration."""
        return """# GitHub CLI completion
source <(gh completion -s zsh)
compdef _gh gh"""


class GitLabModule(ConfigOnlyModule):
    """GitLab CLI configuration module.

    Configures:
    - GitLab CLI (glab) autocompletion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="GitLab",
            description="GitLab CLI completion",
            category=ModuleCategory.VCS,
            required_binaries=["glab"],
            provides=["glab-completion"],
            tags=["gitlab", "glab", "git", "vcs"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate GitLab CLI configuration."""
        return """# GitLab CLI completion
source <(glab completion -s zsh)
compdef _glab glab"""
