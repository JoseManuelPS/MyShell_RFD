"""Rollback system for MyShell_RFD (E4).

Provides snapshot-based configuration rollback with history tracking.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from myshell_rfd.utils.files import BACKUP_DIR, get_file_ops
from myshell_rfd.utils.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator


SNAPSHOTS_DIR = BACKUP_DIR / "snapshots"
SNAPSHOT_INDEX = SNAPSHOTS_DIR / "index.json"


@dataclass
class SnapshotFile:
    """A file included in a snapshot.

    Attributes:
        original_path: Original file path.
        backup_path: Path to backup copy.
        existed: Whether file existed before.
    """

    original_path: str
    backup_path: str
    existed: bool = True


@dataclass
class Snapshot:
    """A configuration snapshot for rollback.

    Attributes:
        id: Unique snapshot ID.
        created_at: Creation timestamp.
        description: Human-readable description.
        files: Files included in snapshot.
        modules: Modules that were modified.
    """

    id: str
    created_at: str
    description: str
    files: list[SnapshotFile] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, description: str, modules: list[str] | None = None) -> "Snapshot":
        """Create a new snapshot.

        Args:
            description: Snapshot description.
            modules: Modules being modified.

        Returns:
            New Snapshot instance.
        """
        return cls(
            id=str(uuid4())[:8],
            created_at=datetime.now().isoformat(),
            description=description,
            modules=modules or [],
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "description": self.description,
            "files": [asdict(f) for f in self.files],
            "modules": self.modules,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        """Create from dictionary."""
        files = [SnapshotFile(**f) for f in data.get("files", [])]
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            description=data["description"],
            files=files,
            modules=data.get("modules", []),
        )


class RollbackManager:
    """Manages configuration snapshots and rollback.

    Provides:
    - Automatic snapshot creation before modifications
    - Snapshot listing and inspection
    - Rollback to any snapshot
    - Cleanup of old snapshots
    """

    def __init__(self, max_snapshots: int = 20) -> None:
        """Initialize rollback manager.

        Args:
            max_snapshots: Maximum number of snapshots to keep.
        """
        self._max_snapshots = max_snapshots
        self._logger = get_logger()
        self._file_ops = get_file_ops()
        self._snapshots: list[Snapshot] = []
        self._ensure_dirs()
        self._load_index()

    def _ensure_dirs(self) -> None:
        """Ensure snapshot directories exist."""
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    def _load_index(self) -> None:
        """Load snapshot index from disk."""
        if not SNAPSHOT_INDEX.exists():
            self._snapshots = []
            return

        try:
            with open(SNAPSHOT_INDEX) as f:
                data = json.load(f)
            self._snapshots = [Snapshot.from_dict(s) for s in data]
        except (json.JSONDecodeError, KeyError) as e:
            self._logger.warn(f"Could not load snapshot index: {e}")
            self._snapshots = []

    def _save_index(self) -> None:
        """Save snapshot index to disk."""
        data = [s.to_dict() for s in self._snapshots]
        with open(SNAPSHOT_INDEX, "w") as f:
            json.dump(data, f, indent=2)

    def create_snapshot(
        self,
        description: str,
        files: list[Path],
        modules: list[str] | None = None,
    ) -> Snapshot:
        """Create a new snapshot.

        Args:
            description: Snapshot description.
            files: Files to include in snapshot.
            modules: Modules being modified.

        Returns:
            The created snapshot.
        """
        snapshot = Snapshot.create(description, modules)
        snapshot_dir = SNAPSHOTS_DIR / snapshot.id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Backup each file
        for file_path in files:
            if file_path.exists():
                backup_name = file_path.name
                backup_path = snapshot_dir / backup_name

                # Copy file to snapshot
                backup_path.write_bytes(file_path.read_bytes())

                snapshot.files.append(
                    SnapshotFile(
                        original_path=str(file_path),
                        backup_path=str(backup_path),
                        existed=True,
                    )
                )
            else:
                # File doesn't exist, mark for potential creation tracking
                snapshot.files.append(
                    SnapshotFile(
                        original_path=str(file_path),
                        backup_path="",
                        existed=False,
                    )
                )

        # Add to index
        self._snapshots.insert(0, snapshot)

        # Cleanup old snapshots
        self._cleanup_old()

        # Save index
        self._save_index()

        self._logger.debug(f"Created snapshot {snapshot.id}: {description}")
        return snapshot

    def list_snapshots(self) -> "Iterator[Snapshot]":
        """List all snapshots.

        Yields:
            Snapshots ordered by creation date (newest first).
        """
        yield from self._snapshots

    def get_snapshot(self, snapshot_id: str) -> Snapshot | None:
        """Get a snapshot by ID.

        Args:
            snapshot_id: Snapshot ID (or prefix).

        Returns:
            Snapshot or None if not found.
        """
        for snapshot in self._snapshots:
            if snapshot.id.startswith(snapshot_id):
                return snapshot
        return None

    def rollback(self, snapshot_id: str) -> bool:
        """Rollback to a snapshot.

        Args:
            snapshot_id: Snapshot ID to rollback to.

        Returns:
            True if rollback succeeded.
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            self._logger.error(f"Snapshot '{snapshot_id}' not found")
            return False

        self._logger.info(f"Rolling back to snapshot {snapshot.id}...")

        # Create a snapshot of current state first
        current_files = [Path(f.original_path) for f in snapshot.files]
        self.create_snapshot(
            f"Pre-rollback state (before {snapshot.id})",
            current_files,
        )

        # Restore files
        for file_info in snapshot.files:
            original = Path(file_info.original_path)

            if file_info.existed:
                # Restore from backup
                backup = Path(file_info.backup_path)
                if backup.exists():
                    original.parent.mkdir(parents=True, exist_ok=True)
                    original.write_bytes(backup.read_bytes())
                    self._logger.debug(f"Restored {original}")
            else:
                # File didn't exist, remove if it was created
                if original.exists():
                    original.unlink()
                    self._logger.debug(f"Removed {original}")

        self._logger.success(f"Rolled back to snapshot {snapshot.id}")
        return True

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot.

        Args:
            snapshot_id: Snapshot ID to delete.

        Returns:
            True if deleted.
        """
        import shutil

        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return False

        # Remove snapshot directory
        snapshot_dir = SNAPSHOTS_DIR / snapshot.id
        if snapshot_dir.exists():
            shutil.rmtree(snapshot_dir)

        # Remove from index
        self._snapshots = [s for s in self._snapshots if s.id != snapshot.id]
        self._save_index()

        self._logger.debug(f"Deleted snapshot {snapshot.id}")
        return True

    def _cleanup_old(self) -> None:
        """Remove old snapshots exceeding max count."""
        import shutil

        while len(self._snapshots) > self._max_snapshots:
            old = self._snapshots.pop()
            snapshot_dir = SNAPSHOTS_DIR / old.id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            self._logger.debug(f"Cleaned up old snapshot {old.id}")

    def clear_all(self) -> int:
        """Clear all snapshots.

        Returns:
            Number of snapshots deleted.
        """
        import shutil

        count = len(self._snapshots)

        for snapshot in self._snapshots:
            snapshot_dir = SNAPSHOTS_DIR / snapshot.id
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)

        self._snapshots = []
        self._save_index()

        self._logger.info(f"Cleared {count} snapshots")
        return count


# Global instance
_rollback_manager: RollbackManager | None = None


def get_rollback_manager() -> RollbackManager:
    """Get the global RollbackManager instance."""
    global _rollback_manager
    if _rollback_manager is None:
        _rollback_manager = RollbackManager()
    return _rollback_manager
