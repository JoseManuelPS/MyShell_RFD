"""Container tools modules for MyShell_RFD.

Configures Docker and Podman integration.
"""

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    InstallResult,
    ModuleCategory,
    ModuleInfo,
)


class DockerModule(ConfigOnlyModule):
    """Docker configuration module.

    Configures:
    - Docker Oh My Zsh plugin
    - Docker aliases
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Docker",
            description="Docker CLI integration and aliases",
            category=ModuleCategory.CONTAINER,
            required_binaries=["docker"],
            provides=["docker-completion", "docker-aliases"],
            tags=["docker", "container", "devops"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Docker configuration."""
        return """# Docker aliases
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlog='docker logs -f'
alias dprune='docker system prune -af'"""

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install Docker module with OMZ plugin."""
        # Enable Oh My Zsh docker plugin
        from myshell_rfd.core.shell import get_shell_manager

        shell = get_shell_manager()
        shell.enable_omz_plugin("docker")

        # Add custom config
        return super().install(config)


class PodmanModule(ConfigOnlyModule):
    """Podman configuration module.

    Configures:
    - Podman autocompletion
    - Podman aliases
    - Docker compatibility alias
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Podman",
            description="Podman CLI integration and aliases",
            category=ModuleCategory.CONTAINER,
            required_binaries=["podman"],
            provides=["podman-completion", "podman-aliases"],
            tags=["podman", "container", "devops", "rootless"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Podman configuration."""
        use_docker_alias = config.settings.get("docker_alias", True)

        content = """# Podman completion
source <(podman completion zsh)
compdef _podman podman

# Podman aliases
alias pps='podman ps'
alias ppsa='podman ps -a'
alias pi='podman images'
alias pex='podman exec -it'
alias plog='podman logs -f'"""

        if use_docker_alias:
            content += """

# Docker compatibility
alias docker='podman'"""

        return content
