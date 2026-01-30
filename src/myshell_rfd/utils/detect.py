"""Binary and tool detection utility for MyShell_RFD.

Provides system scanning and tool detection capabilities.
Replaces check_binary() from utils.sh with enhanced functionality.
"""

import os
import platform
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from myshell_rfd.utils.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator


class ToolCategory(str, Enum):
    """Tool category enumeration."""

    SHELL = "shell"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    VCS = "vcs"
    EDITOR = "editor"
    BUILD = "build"
    LANGUAGE = "language"
    OTHER = "other"


@dataclass
class ToolInfo:
    """Information about a detected tool.

    Attributes:
        name: Tool name.
        command: Command to invoke the tool.
        path: Full path to the executable.
        version: Detected version string.
        category: Tool category.
        installed: Whether the tool is installed.
    """

    name: str
    command: str
    path: Path | None = None
    version: str | None = None
    category: ToolCategory = ToolCategory.OTHER
    installed: bool = False


@dataclass
class SystemInfo:
    """System information.

    Attributes:
        os_name: Operating system name.
        os_version: OS version string.
        arch: System architecture.
        shell: Current shell.
        home: User home directory.
        tools: Detected tools mapping.
    """

    os_name: str
    os_version: str
    arch: str
    shell: str
    home: Path
    tools: dict[str, ToolInfo] = field(default_factory=dict)


# Known tools and their detection info
KNOWN_TOOLS: dict[str, tuple[str, ToolCategory, list[str]]] = {
    # Shells
    "zsh": ("zsh", ToolCategory.SHELL, ["--version"]),
    # Containers
    "docker": ("docker", ToolCategory.CONTAINER, ["--version"]),
    "podman": ("podman", ToolCategory.CONTAINER, ["--version"]),
    # Kubernetes
    "kubectl": ("kubectl", ToolCategory.KUBERNETES, ["version", "--client", "--short"]),
    "helm": ("helm", ToolCategory.KUBERNETES, ["version", "--short"]),
    "minikube": ("minikube", ToolCategory.KUBERNETES, ["version", "--short"]),
    "k9s": ("k9s", ToolCategory.KUBERNETES, ["version", "--short"]),
    "eksctl": ("eksctl", ToolCategory.KUBERNETES, ["version"]),
    "oc": ("oc", ToolCategory.KUBERNETES, ["version", "--client"]),
    "rosa": ("rosa", ToolCategory.KUBERNETES, ["version"]),
    "tridentctl": ("tridentctl", ToolCategory.KUBERNETES, ["version"]),
    # Cloud
    "aws": ("aws", ToolCategory.CLOUD, ["--version"]),
    "gcloud": ("gcloud", ToolCategory.CLOUD, ["--version"]),
    "az": ("az", ToolCategory.CLOUD, ["--version"]),
    "terraform": ("terraform", ToolCategory.CLOUD, ["--version"]),
    "tofu": ("tofu", ToolCategory.CLOUD, ["--version"]),
    # VCS
    "git": ("git", ToolCategory.VCS, ["--version"]),
    "gh": ("gh", ToolCategory.VCS, ["--version"]),
    "glab": ("glab", ToolCategory.VCS, ["--version"]),
    # Tools
    "fzf": ("fzf", ToolCategory.OTHER, ["--version"]),
    "bat": ("bat", ToolCategory.OTHER, ["--version"]),
    "batcat": ("batcat", ToolCategory.OTHER, ["--version"]),
    "rg": ("rg", ToolCategory.OTHER, ["--version"]),
    "fd": ("fd", ToolCategory.OTHER, ["--version"]),
    "exa": ("exa", ToolCategory.OTHER, ["--version"]),
    "eza": ("eza", ToolCategory.OTHER, ["--version"]),
    # Languages
    "python3": ("python3", ToolCategory.LANGUAGE, ["--version"]),
    "node": ("node", ToolCategory.LANGUAGE, ["--version"]),
    "go": ("go", ToolCategory.LANGUAGE, ["version"]),
    "rust": ("rustc", ToolCategory.LANGUAGE, ["--version"]),
}


class BinaryDetector:
    """Detects installed binaries and system configuration.

    Provides methods to check for binary existence, get version info,
    and scan the system for known tools.
    """

    def __init__(self) -> None:
        """Initialize the detector."""
        self._logger = get_logger()
        self._cache: dict[str, ToolInfo] = {}

    def check_binary(self, name: str) -> bool:
        """Check if a binary exists in PATH.

        Equivalent to check_binary() in utils.sh.

        Args:
            name: The binary name to check.

        Returns:
            True if the binary exists, False otherwise.
        """
        return shutil.which(name) is not None

    def get_binary_path(self, name: str) -> Path | None:
        """Get the full path to a binary.

        Args:
            name: The binary name.

        Returns:
            The full path, or None if not found.
        """
        path = shutil.which(name)
        return Path(path) if path else None

    def get_version(self, name: str, version_args: list[str] | None = None) -> str | None:
        """Get the version string of a binary.

        Args:
            name: The binary name.
            version_args: Arguments to get version (default: ["--version"]).

        Returns:
            The version string, or None if unable to determine.
        """
        import subprocess

        args = version_args or ["--version"]
        path = self.get_binary_path(name)

        if not path:
            return None

        try:
            result = subprocess.run(
                [str(path), *args],
                capture_output=True,
                timeout=5.0,
            )
            # Handle potential encoding issues
            try:
                output = result.stdout.decode("utf-8", errors="replace")
            except Exception:
                output = ""
            if not output:
                try:
                    output = result.stderr.decode("utf-8", errors="replace")
                except Exception:
                    output = ""
            # Extract first line, often contains version
            if output:
                return output.strip().split("\n")[0]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            pass

        return None

    def get_tool_info(self, name: str) -> ToolInfo:
        """Get detailed information about a tool.

        Args:
            name: The tool name.

        Returns:
            ToolInfo with detection results.
        """
        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Get known tool config or create default
        if name in KNOWN_TOOLS:
            command, category, version_args = KNOWN_TOOLS[name]
        else:
            command = name
            category = ToolCategory.OTHER
            version_args = ["--version"]

        path = self.get_binary_path(command)
        installed = path is not None

        version = None
        if installed:
            version = self.get_version(command, version_args)

        info = ToolInfo(
            name=name,
            command=command,
            path=path,
            version=version,
            category=category,
            installed=installed,
        )

        self._cache[name] = info
        return info

    def scan_known_tools(self) -> dict[str, ToolInfo]:
        """Scan for all known tools.

        Returns:
            Dictionary mapping tool names to their info.
        """
        self._logger.debug("Scanning for known tools...")

        result: dict[str, ToolInfo] = {}
        for name in KNOWN_TOOLS:
            info = self.get_tool_info(name)
            result[name] = info
            if info.installed:
                self._logger.debug(f"Found {name}: {info.version or 'version unknown'}")

        return result

    def get_installed_tools(self) -> "Iterator[ToolInfo]":
        """Yield only installed tools.

        Yields:
            ToolInfo for each installed tool.
        """
        for info in self.scan_known_tools().values():
            if info.installed:
                yield info

    def get_tools_by_category(self, category: ToolCategory) -> "Iterator[ToolInfo]":
        """Yield tools matching a category.

        Args:
            category: The category to filter by.

        Yields:
            ToolInfo for matching tools.
        """
        for info in self.scan_known_tools().values():
            if info.category == category:
                yield info

    def get_system_info(self) -> SystemInfo:
        """Get comprehensive system information.

        Returns:
            SystemInfo with OS details and detected tools.
        """
        # Detect current shell
        shell = os.environ.get("SHELL", "/bin/sh")
        shell_name = Path(shell).name

        info = SystemInfo(
            os_name=platform.system(),
            os_version=platform.release(),
            arch=platform.machine(),
            shell=shell_name,
            home=Path.home(),
            tools=self.scan_known_tools(),
        )

        return info

    def get_shell_config_file(self) -> Path:
        """Get the ZSH configuration file path.

        Returns the MyShell_RFD managed config file path.
        Modules should write their configuration here instead of .zshrc.

        Returns:
            Path to ~/.myshell_rfd/config.
        """
        from myshell_rfd.utils.files import SHELL_CONFIG_FILE

        return SHELL_CONFIG_FILE

    def get_zshrc_path(self) -> Path:
        """Get the path to .zshrc.

        Use this when you need to access .zshrc directly (e.g., for source lines).

        Returns:
            Path to user's .zshrc file.
        """
        return Path.home() / ".zshrc"

    def get_oh_my_zsh_dir(self) -> Path | None:
        """Get the Oh My Zsh directory if installed.

        Returns:
            Path to Oh My Zsh, or None if not installed.
        """
        # Check standard locations
        omz_dir = Path.home() / ".oh-my-zsh"
        if omz_dir.is_dir():
            return omz_dir

        # Check ZSH env variable
        zsh = os.environ.get("ZSH")
        if zsh:
            zsh_path = Path(zsh)
            if zsh_path.is_dir():
                return zsh_path

        return None

    def get_zsh_custom_dir(self) -> Path:
        """Get the ZSH custom directory.

        Returns:
            Path to ZSH_CUSTOM directory.
        """
        # Check environment variable first
        custom = os.environ.get("ZSH_CUSTOM")
        if custom:
            return Path(custom)

        # Default location
        omz = self.get_oh_my_zsh_dir()
        if omz:
            return omz / "custom"

        return Path.home() / ".oh-my-zsh" / "custom"

    def clear_cache(self) -> None:
        """Clear the detection cache."""
        self._cache.clear()


# Default instance
_detector: BinaryDetector | None = None


def get_detector() -> BinaryDetector:
    """Get the default BinaryDetector instance."""
    global _detector
    if _detector is None:
        _detector = BinaryDetector()
    return _detector
