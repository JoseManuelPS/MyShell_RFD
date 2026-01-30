"""Tool and system detection utilities.

Provides functionality to:
- Check for installed binaries
- Get tool versions (legacy logic removed)
- Detect system information (legacy logic removed)
"""

import shutil
from pathlib import Path

from myshell_rfd.utils.logger import get_logger


class BinaryDetector:
    """Detects installed binaries and system paths.
    
    Provides core functionality for checking if tools are installed
    and resolving standard configuration paths.
    """

    def __init__(self) -> None:
        """Initialize detector."""
        self._logger = get_logger()

    def check_binary(self, name: str) -> bool:
        """Check if a binary exists in PATH.

        Args:
            name: Binary name to check.

        Returns:
            True if binary exists.
        """
        return shutil.which(name) is not None

    def get_binary_path(self, name: str) -> str | None:
        """Get the full path to a binary.

        Args:
            name: Binary name.

        Returns:
            Full path or None if not found.
        """
        return shutil.which(name)

    def get_zshrc_path(self) -> Path:
        """Get path to .zshrc.

        Returns:
            Path to .zshrc file.
        """
        return Path.home() / ".zshrc"

    def get_shell_config_file(self) -> Path:
        """Get path to the MyShell_RFD config file.
        
        Returns:
            Path to config file.
        """
        from myshell_rfd.utils.files import SHELL_CONFIG_FILE
        return SHELL_CONFIG_FILE

    def get_oh_my_zsh_dir(self) -> Path | None:
        """Get Oh My Zsh installation directory.

        Returns:
            Path if installed, None otherwise.
        """
        # Common locations
        candidates = [
            Path.home() / ".oh-my-zsh",
            Path.home() / ".oh-my-zsh-custom",
        ]
        
        # Check environment variable
        import os
        if "ZSH" in os.environ:
            candidates.insert(0, Path(os.environ["ZSH"]))

        for path in candidates:
            if path.exists() and (path / "oh-my-zsh.sh").exists():
                return path

        return None

    def get_zsh_custom_dir(self) -> Path:
        """Get ZSH_CUSTOM directory.

        Returns:
            Path to ZSH custom directory.
        """
        omz_dir = self.get_oh_my_zsh_dir()
        if omz_dir:
            import os
            custom = os.environ.get("ZSH_CUSTOM")
            if custom:
                return Path(custom)
            return omz_dir / "custom"
        
        # Fallback for non-OMZ setups (though we mostly target OMZ)
        return Path.home() / ".zsh"


# Global instance
_detector: BinaryDetector | None = None


def get_detector() -> BinaryDetector:
    """Get the global BinaryDetector instance."""
    global _detector
    if _detector is None:
        _detector = BinaryDetector()
    return _detector
