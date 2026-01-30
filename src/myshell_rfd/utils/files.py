"""File operations utility for MyShell_RFD.

Provides safe file manipulation with backup and rollback support.
Replaces functionality from utils.sh (backup_file, add_to_config, etc.).
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from platformdirs import user_data_dir

if TYPE_CHECKING:
    from collections.abc import Iterator

# Application directories (lazy creation - don't create on import)
APP_NAME = "myshell_rfd"
CONFIG_DIR = Path.home() / ".myshell_rfd"
BACKUP_DIR = CONFIG_DIR / "backups"
CACHE_DIR = CONFIG_DIR / "cache"
PLUGINS_DIR = CONFIG_DIR / "plugins"
PROFILES_DIR = CONFIG_DIR / "profiles"
SHELL_CONFIG_FILE = CONFIG_DIR / "config"  # ZSH config managed by MyShell_RFD

CONFIG_HEADER = (
    "# ============================================================\n"
    "# MyShell_RFD Configuration\n"
    "# ============================================================\n"
    "# This file is managed by MyShell_RFD. Do not edit manually!\n"
    "# Your custom ZSH configuration should remain in ~/.zshrc\n"
    "#\n"
    "# To add/remove modules, use:\n"
    "#   myshell install <module>\n"
    "#   myshell uninstall <module>\n"
    "#\n"
    "# Or launch the TUI:\n"
    "#   myshell\n"
    "# ============================================================\n\n"
)


def get_app_dir() -> Path:
    """Get the application data directory, creating if needed."""
    return Path(user_data_dir(APP_NAME, appauthor=False, ensure_exists=True))


class FileOperations:
    """Safe file operations with backup support.

    Provides methods for reading, writing, and modifying files
    with automatic backup creation for rollback capability.
    """

    def __init__(self, backup_dir: Path | None = None) -> None:
        """Initialize file operations.

        Args:
            backup_dir: Custom backup directory. Defaults to ~/.myshell_rfd/backups.
        """
        self._backup_dir = backup_dir or BACKUP_DIR

    @property
    def backup_dir(self) -> Path:
        """Get the backup directory path."""
        return self._backup_dir

    def ensure_dirs(self) -> None:
        """Ensure all application directories exist."""
        for directory in [CONFIG_DIR, BACKUP_DIR, CACHE_DIR, PLUGINS_DIR, PROFILES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def backup_file(self, path: Path, *, suffix: str = "") -> Path | None:
        """Create a timestamped backup of a file.

        Args:
            path: The file to backup.
            suffix: Optional suffix for the backup name.

        Returns:
            The path to the backup file, or None if the source doesn't exist.
        """
        if not path.exists():
            return None

        self._backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.name}.{timestamp}"
        if suffix:
            backup_name = f"{backup_name}.{suffix}"

        backup_path = self._backup_dir / backup_name
        shutil.copy2(path, backup_path)

        return backup_path

    def read_file(self, path: Path) -> str | None:
        """Read file contents.

        Args:
            path: The file to read.

        Returns:
            The file contents, or None if the file doesn't exist.
        """
        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")

    def write_file(
        self,
        path: Path,
        content: str,
        *,
        backup: bool = True,
        create_parents: bool = True,
    ) -> Path | None:
        """Write content to a file with optional backup.

        Args:
            path: The file to write.
            content: The content to write.
            backup: Create a backup before writing.
            create_parents: Create parent directories if needed.

        Returns:
            The backup path if created, otherwise None.
        """
        backup_path = None

        if backup and path.exists():
            backup_path = self.backup_file(path)

        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return backup_path

    def append_file(
        self,
        path: Path,
        content: str,
        *,
        backup: bool = True,
        newline: bool = True,
    ) -> Path | None:
        """Append content to a file.

        Args:
            path: The file to append to.
            content: The content to append.
            backup: Create a backup before appending.
            newline: Add a newline before the content if needed.

        Returns:
            The backup path if created, otherwise None.
        """
        backup_path = None

        if backup and path.exists():
            backup_path = self.backup_file(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        existing = ""
        if path.exists():
            existing = path.read_text(encoding="utf-8")

        # Ensure newline separation
        if newline and existing and not existing.endswith("\n"):
            content = "\n" + content

        with path.open("a", encoding="utf-8") as f:
            f.write(content)

        return backup_path

    def add_to_config(
        self,
        path: Path,
        section_name: str,
        content: str,
        *,
        backup: bool = True,
    ) -> bool:
        """Add a configuration section if not already present.

        Implements idempotent configuration addition.
        Uses markers to identify sections and prevent duplicates.

        Args:
            path: The configuration file path.
            section_name: The section identifier (used in markers).
            content: The content to add.
            backup: Create a backup before modifying.

        Returns:
            True if content was added, False if already present.
        """
        # Clean marker format
        start_marker = f"##### {section_name} #####"

        # Check if file exists and has content
        existing = self.read_file(path)
        
        # If file is empty or missing, start with the header
        is_new = not existing or not existing.strip()
        if is_new:
            from myshell_rfd.utils.files import CONFIG_HEADER
            existing = CONFIG_HEADER
            self.write_file(path, existing, backup=backup)
        
        # Check if section already exists
        if start_marker in existing:
            return False

        # Build the new section (no end marker needed)
        section = f"\n{start_marker}\n{content.strip()}\n"

        self.append_file(path, section, backup=False, newline=True)

        return True

    def remove_from_config(
        self,
        path: Path,
        section_name: str,
        *,
        backup: bool = True,
    ) -> bool:
        """Remove a configuration section.

        Args:
            path: The configuration file path.
            section_name: The section identifier.
            backup: Create a backup before modifying.

        Returns:
            True if section was removed, False if not found.
        """
        import re

        content = self.read_file(path)
        if content is None:
            return False

        # Target marker
        new_start = f"##### {section_name} #####"

        if new_start not in content:
            return False

        lines = content.splitlines(keepends=True)
        new_lines: list[str] = []
        skip_line = False

        # Regex to detect start of ANY section
        section_start_re = re.compile(r"^#  \[.+\]\s*$")

        for line in lines:
            # Check for start of the target section
            if new_start in line:
                skip_line = True
                continue

            # Check for end of deletion block
            if skip_line:
                # If we hit the start of ANOTHER section, stop skipping
                if section_start_re.match(line):
                    skip_line = False
                    new_lines.append(line)
                    continue

                # Otherwise, stay in deletion mode
                continue

            # Not in a deletion block, keep the line
            new_lines.append(line)

        new_content = "".join(new_lines)

        # Remove extra blank lines
        while "\n\n\n" in new_content:
            new_content = new_content.replace("\n\n\n", "\n\n")

        self.write_file(path, new_content, backup=backup)

        return True

    def list_backups(self, pattern: str = "*") -> "Iterator[Path]":
        """List backup files matching a pattern.

        Args:
            pattern: Glob pattern for filtering backups.

        Yields:
            Paths to matching backup files.
        """
        if not self._backup_dir.exists():
            return

        yield from sorted(self._backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """Restore a file from backup.

        Args:
            backup_path: The backup file to restore.
            target_path: The target path to restore to.

        Returns:
            True if restored successfully.
        """
        if not backup_path.exists():
            return False

        # Backup current state before restoring
        if target_path.exists():
            self.backup_file(target_path, suffix="pre-restore")

        shutil.copy2(backup_path, target_path)
        return True

    def clean_old_backups(self, max_age_days: int = 30, max_count: int = 50) -> int:
        """Remove old backups exceeding age or count limits.

        Args:
            max_age_days: Maximum age in days for backups.
            max_count: Maximum number of backups to keep.

        Returns:
            Number of backups removed.
        """
        if not self._backup_dir.exists():
            return 0

        backups = list(self.list_backups())
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        removed = 0

        # Remove by age
        for backup in backups:
            if backup.stat().st_mtime < cutoff:
                backup.unlink()
                removed += 1

        # Remove by count (keep newest)
        remaining = list(self.list_backups())
        if len(remaining) > max_count:
            for backup in remaining[max_count:]:
                backup.unlink()
                removed += 1

        return removed


# Default instance
_file_ops: FileOperations | None = None


def get_file_ops() -> FileOperations:
    """Get the default FileOperations instance."""
    global _file_ops
    if _file_ops is None:
        _file_ops = FileOperations()
    return _file_ops
