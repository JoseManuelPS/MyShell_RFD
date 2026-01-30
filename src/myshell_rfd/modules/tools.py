"""Developer tools modules for MyShell_RFD.

Configures FZF, Bat, PLS, Python venv, NVM, and K plugin.
"""

from pathlib import Path

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    ConfigOnlyModule,
    GitCloneModule,
    InstallResult,
    InstallationType,
    ModuleCategory,
    ModuleInfo,
)


class FZFModule(GitCloneModule):
    """FZF fuzzy finder module.

    Installs and configures:
    - FZF fuzzy finder
    - FZF key bindings
    - FZF completion
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="FZF",
            description="Fuzzy finder for shell",
            category=ModuleCategory.TOOLS,
            installation_type=InstallationType.GIT_CLONE,
            provides=["fzf", "fzf-completion", "fzf-keybindings"],
            tags=["fzf", "fuzzy", "search", "finder"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/junegunn/fzf.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return Path.home() / ".fzf"

    def check_available(self) -> bool:
        """FZF can always be installed."""
        return True

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate FZF configuration."""
        return """# FZF configuration
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# FZF options
export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'"""

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install FZF with installer script."""
        # Clone if not present
        if not self.check_installed():
            result = super().install(config)
            if not result.success:
                return result

        # Run FZF installer
        install_script = self.target_dir / "install"
        if install_script.exists():
            self._logger.info("Running FZF installer...")
            # Use --all but we will cleanup .zshrc afterwards
            result = self._runner.run(
                [str(install_script), "--all", "--no-bash", "--no-fish"],
            )
            if not result.success:
                self._logger.warn(f"FZF installer warning: {result.stderr}")

            # Cleanup .zshrc: the installer adds a source line that we already
            # handle in ~/.myshell_rfd/config
            self._cleanup_zshrc()

        # Add config
        self._add_config(self.get_config_content(config))

        return InstallResult(
            success=True,
            message="FZF installed and configured",
            files_created=[str(self.target_dir)],
        )

    def _cleanup_zshrc(self) -> None:
        """Remove FZF source line from .zshrc if present."""
        zshrc = Path.home() / ".zshrc"
        if not zshrc.exists():
            return

        content = self._file_ops.read_file(zshrc)
        if not content:
            return

        # The line added by FZF installer
        fzf_line = "[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh"
        
        if fzf_line in content:
            self._logger.debug("Removing FZF source line from .zshrc")
            # Replace the line and any surrounding whitespace/newlines it might have added
            new_content = content.replace(fzf_line, "")
            
            # Clean up potential double or triple newlines left behind
            import re
            new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
            
            self._file_ops.write_file(zshrc, new_content.strip() + "\n", backup=True)


class BatcatModule(ConfigOnlyModule):
    """Bat/Batcat configuration module.

    Configures:
    - Bat aliases for syntax-highlighted cat
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Batcat",
            description="Syntax-highlighted cat alternative",
            category=ModuleCategory.TOOLS,
            optional_binaries=["bat", "batcat"],
            provides=["bat-aliases"],
            tags=["bat", "batcat", "cat", "syntax"],
        )

    def check_available(self) -> bool:
        """Check if bat or batcat is available."""
        return (
            self._detector.check_binary("bat")
            or self._detector.check_binary("batcat")
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Bat configuration."""
        # Detect which binary is available
        if self._detector.check_binary("bat"):
            cmd = "bat"
        else:
            cmd = "batcat"

        return f"""# Bat/Batcat aliases
alias cat='{cmd}'
alias bat='{cmd}'
alias catp='{cmd} --plain'"""


class PLSModule(ConfigOnlyModule):
    """PLS (please sudo) configuration module.

    Configures:
    - pls alias for sudo with last command
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="PLS",
            description="Please sudo alias",
            category=ModuleCategory.TOOLS,
            required_binaries=["sudo"],
            provides=["pls-alias"],
            tags=["sudo", "pls", "please", "alias"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate PLS configuration."""
        return """# PLS - Please sudo
alias pls='sudo $(fc -ln -1)'
alias please='sudo $(fc -ln -1)'"""


class PythonVenvModule(ConfigOnlyModule):
    """Python virtual environment module.

    Configures:
    - Python venv auto-activation
    - Venv aliases
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="Python",
            description="Python venv integration",
            category=ModuleCategory.TOOLS,
            required_binaries=["python3"],
            provides=["python-venv"],
            tags=["python", "venv", "virtualenv"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate Python venv configuration."""
        return """# Python venv helpers
alias venv='python3 -m venv .venv'
alias activate='source .venv/bin/activate'

# Auto-activate venv if present
auto_activate_venv() {
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
}
chpwd_functions+=(auto_activate_venv)"""


class NVMModule(ConfigOnlyModule):
    """NVM (Node Version Manager) configuration module.

    Configures:
    - NVM lazy loading for faster shell startup
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="NVM",
            description="Node Version Manager lazy loading",
            category=ModuleCategory.TOOLS,
            provides=["nvm-config"],
            tags=["nvm", "node", "nodejs", "npm"],
        )

    def check_available(self) -> bool:
        """Check if NVM is installed."""
        nvm_dir = Path.home() / ".nvm"
        return nvm_dir.is_dir()

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate NVM configuration with lazy loading."""
        return """# NVM - Node Version Manager (lazy loading)
export NVM_DIR="$HOME/.nvm"

# Lazy load NVM for faster shell startup
nvm() {
    unset -f nvm node npm npx
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && source "$NVM_DIR/bash_completion"
    nvm "$@"
}

node() {
    unset -f nvm node npm npx
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    node "$@"
}

npm() {
    unset -f nvm node npm npx
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    npm "$@"
}

npx() {
    unset -f nvm node npm npx
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    npx "$@"
}"""


class KPluginModule(GitCloneModule):
    """K plugin module (directory listing).

    Installs and configures:
    - K plugin for enhanced directory listing
    - Mapped to 'z' command
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        return ModuleInfo(
            name="K_Plugin",
            description="Enhanced directory listing (z command)",
            category=ModuleCategory.TOOLS,
            installation_type=InstallationType.GIT_CLONE,
            provides=["k-plugin", "z-command"],
            tags=["k", "ls", "directory", "listing"],
        )

    @property
    def repo_url(self) -> str:
        """Git repository URL."""
        return "https://github.com/supercrabtree/k.git"

    @property
    def target_dir(self) -> Path:
        """Target directory for clone."""
        return self._get_zsh_custom() / "plugins" / "k"

    def check_available(self) -> bool:
        """K plugin can always be installed."""
        return True

    def get_config_content(self, config: ModuleConfig) -> str:
        """Generate K plugin configuration."""
        return """# K plugin (enhanced ls as 'z' command)
alias z='k'"""

    def install(self, config: ModuleConfig) -> InstallResult:
        """Install K plugin and patch for 'z' command."""
        result = super().install(config)

        if result.success:
            # Patch k.sh to respond to 'z' as well
            k_script = self.target_dir / "k.sh"
            if k_script.exists():
                content = k_script.read_text()
                if "alias z=k" not in content:
                    content += "\nalias z=k\n"
                    k_script.write_text(content)

            # Enable the plugin
            from myshell_rfd.core.shell import get_shell_manager

            shell = get_shell_manager()
            shell.enable_omz_plugin("k")

        return result
