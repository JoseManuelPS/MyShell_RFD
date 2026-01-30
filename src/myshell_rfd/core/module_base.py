"""Module protocol and base class for MyShell_RFD.

Defines the interface that all modules must implement and provides
a base class with common functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from myshell_rfd.core.config import ModuleConfig
    from myshell_rfd.utils.detect import BinaryDetector
    from myshell_rfd.utils.files import FileOperations
    from myshell_rfd.utils.logger import Logger
    from myshell_rfd.utils.process import ProcessRunner


class ModuleCategory(str, Enum):
    """Module category for organization."""

    SHELL = "shell"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    VCS = "vcs"
    TOOLS = "tools"
    THEME = "theme"


class InstallationType(str, Enum):
    """Type of installation the module performs."""

    CONFIG_ONLY = "config_only"  # Only adds configuration
    GIT_CLONE = "git_clone"  # Clones a git repository
    BINARY = "binary"  # Downloads/installs a binary
    PACKAGE = "package"  # Uses package manager


@dataclass
class ModuleInfo:
    """Metadata about a module.

    Attributes:
        name: Module display name.
        description: Short description.
        category: Module category.
        installation_type: How the module installs.
        required_binaries: Binaries that must exist.
        optional_binaries: Binaries that enhance functionality.
        provides: What this module provides/configures.
        dependencies: Other modules this depends on.
        tags: Searchable tags.
    """

    name: str
    description: str
    category: ModuleCategory
    installation_type: InstallationType = InstallationType.CONFIG_ONLY
    required_binaries: list[str] = field(default_factory=list)
    optional_binaries: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class InstallResult:
    """Result of a module installation.

    Attributes:
        success: Whether installation succeeded.
        message: Status message.
        config_added: Configuration content that was added.
        files_created: Files that were created.
        files_modified: Files that were modified.
        requires_restart: Whether shell restart is needed.
    """

    success: bool
    message: str = ""
    config_added: str = ""
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    requires_restart: bool = True


@runtime_checkable
class ModuleProtocol(Protocol):
    """Protocol that all modules must implement.

    This defines the interface for module discovery and execution.
    Use this for type checking when working with modules.
    """

    @property
    def info(self) -> ModuleInfo:
        """Get module metadata."""
        ...

    def check_available(self) -> bool:
        """Check if the module can be installed.

        Returns:
            True if prerequisites are met.
        """
        ...

    def check_installed(self) -> bool:
        """Check if the module is already configured.

        Returns:
            True if already installed/configured.
        """
        ...

    def install(self, config: "ModuleConfig") -> InstallResult:
        """Install/configure the module.

        Args:
            config: Module configuration with settings.

        Returns:
            Installation result.
        """
        ...

    def uninstall(self) -> InstallResult:
        """Remove module configuration.

        Returns:
            Uninstallation result.
        """
        ...


class BaseModule(ABC):
    """Base class for all modules.

    Provides common functionality and utility access.
    Subclasses must implement the abstract methods.
    """

    def __init__(
        self,
        logger: "Logger",
        file_ops: "FileOperations",
        runner: "ProcessRunner",
        detector: "BinaryDetector",
    ) -> None:
        """Initialize the module with utilities.

        Args:
            logger: Logger instance.
            file_ops: File operations instance.
            runner: Process runner instance.
            detector: Binary detector instance.
        """
        self._logger = logger
        self._file_ops = file_ops
        self._runner = runner
        self._detector = detector

    @property
    @abstractmethod
    def info(self) -> ModuleInfo:
        """Get module metadata.

        Returns:
            ModuleInfo with module details.
        """
        ...

    @property
    def name(self) -> str:
        """Get module name."""
        return self.info.name

    @property
    def category(self) -> ModuleCategory:
        """Get module category."""
        return self.info.category

    def check_available(self) -> bool:
        """Check if the module can be installed.

        Default implementation checks required binaries.

        Returns:
            True if all required binaries exist.
        """
        for binary in self.info.required_binaries:
            if not self._detector.check_binary(binary):
                self._logger.debug(f"{self.name}: Missing required binary '{binary}'")
                return False
        return True

    def check_installed(self) -> bool:
        """Check if the module is already configured.

        Default implementation checks if config section exists.

        Returns:
            True if already configured.
        """
        zshrc = self._detector.get_shell_config_file()
        content = self._file_ops.read_file(zshrc)

        if content is None:
            return False

        legacy_marker = f"# >>> MyShell_RFD [{self.name}]"
        new_marker = f"#  [{self.name}]"
        
        return new_marker in content or legacy_marker in content

    @abstractmethod
    def install(self, config: "ModuleConfig") -> InstallResult:
        """Install/configure the module.

        Args:
            config: Module configuration.

        Returns:
            Installation result.
        """
        ...

    def uninstall(self) -> InstallResult:
        """Remove module configuration.

        Default implementation removes config section from .zshrc.

        Returns:
            Uninstallation result.
        """
        zshrc = self._detector.get_shell_config_file()

        if self._file_ops.remove_from_config(zshrc, self.name):
            return InstallResult(
                success=True,
                message=f"{self.name} configuration removed",
                files_modified=[str(zshrc)],
            )

        return InstallResult(
            success=True,
            message=f"{self.name} was not configured",
        )

    def _add_config(self, content: str) -> bool:
        """Add configuration to .zshrc.

        Args:
            content: Configuration content to add.

        Returns:
            True if added, False if already present.
        """
        zshrc = self._detector.get_shell_config_file()
        return self._file_ops.add_to_config(zshrc, self.name, content)

    def _get_zsh_custom(self) -> "Any":
        """Get ZSH_CUSTOM directory path.

        Returns:
            Path to ZSH custom directory.
        """
        return self._detector.get_zsh_custom_dir()

    def _get_omz_dir(self) -> "Any":
        """Get Oh My Zsh directory path.

        Returns:
            Path to Oh My Zsh, or None if not installed.
        """
        return self._detector.get_oh_my_zsh_dir()


class ConfigOnlyModule(BaseModule):
    """Base class for modules that only add configuration.

    These modules configure existing tools (add aliases, completions, etc.)
    without installing new software.
    """

    @abstractmethod
    def get_config_content(self, config: "ModuleConfig") -> str:
        """Generate configuration content.

        Args:
            config: Module configuration with settings.

        Returns:
            Configuration string to add to .zshrc.
        """
        ...

    def install(self, config: "ModuleConfig") -> InstallResult:
        """Install by adding configuration.

        Args:
            config: Module configuration.

        Returns:
            Installation result.
        """
        if not self.check_available():
            return InstallResult(
                success=False,
                message=f"{self.name}: Required binaries not found",
            )

        if self.check_installed():
            return InstallResult(
                success=True,
                message=f"{self.name} is already configured",
            )

        content = self.get_config_content(config)

        if self._add_config(content):
            self._logger.success(f"{self.name} configured successfully")
            return InstallResult(
                success=True,
                message=f"{self.name} configured",
                config_added=content,
                files_modified=[str(self._detector.get_shell_config_file())],
            )

        return InstallResult(
            success=False,
            message=f"Failed to configure {self.name}",
        )


class GitCloneModule(BaseModule):
    """Base class for modules that clone git repositories.

    These modules install by cloning repositories (typically ZSH plugins).
    """

    @property
    @abstractmethod
    def repo_url(self) -> str:
        """Git repository URL to clone."""
        ...

    @property
    @abstractmethod
    def target_dir(self) -> "Any":
        """Target directory for the clone."""
        ...

    def get_config_content(self, config: "ModuleConfig") -> str:
        """Generate configuration content after cloning.

        Args:
            config: Module configuration.

        Returns:
            Configuration string. Override in subclass.
        """
        return ""

    def check_installed(self) -> bool:
        """Check if repository is already cloned."""
        from pathlib import Path

        target = Path(self.target_dir)
        return target.exists() and target.is_dir()

    def install(self, config: "ModuleConfig") -> InstallResult:
        """Install by cloning repository.

        Args:
            config: Module configuration.

        Returns:
            Installation result.
        """
        from pathlib import Path

        if self.check_installed():
            self._logger.info(f"{self.name} is already installed")
            return InstallResult(
                success=True,
                message=f"{self.name} already installed",
            )

        target = Path(self.target_dir)
        target.parent.mkdir(parents=True, exist_ok=True)

        self._logger.info(f"Cloning {self.name}...")

        result = self._runner.git_clone(self.repo_url, target)

        if not result.success:
            self._logger.error(f"Failed to clone {self.name}: {result.stderr}")
            return InstallResult(
                success=False,
                message=f"Clone failed: {result.stderr}",
            )

        # Add configuration if any
        content = self.get_config_content(config)
        if content:
            self._add_config(content)

        self._logger.success(f"{self.name} installed successfully")

        return InstallResult(
            success=True,
            message=f"{self.name} installed",
            files_created=[str(target)],
            config_added=content,
        )

    def uninstall(self) -> InstallResult:
        """Remove cloned repository and configuration."""
        import shutil
        from pathlib import Path

        # Remove repository
        target = Path(self.target_dir)
        if target.exists():
            shutil.rmtree(target)

        # Remove configuration
        super().uninstall()

        return InstallResult(
            success=True,
            message=f"{self.name} removed",
            files_modified=[str(target)],
        )
