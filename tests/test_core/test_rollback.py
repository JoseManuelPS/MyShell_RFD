"""Tests for rollback system."""

import tempfile
from pathlib import Path

import pytest

from myshell_rfd.core.rollback import RollbackManager, Snapshot


class TestSnapshot:
    """Tests for Snapshot class."""

    def test_create_snapshot(self):
        """Test creating a snapshot."""
        snapshot = Snapshot.create("Test snapshot", modules=["module1"])

        assert snapshot.id is not None
        assert len(snapshot.id) == 8
        assert snapshot.description == "Test snapshot"
        assert "module1" in snapshot.modules
        assert snapshot.created_at is not None

    def test_to_dict_from_dict(self):
        """Test snapshot serialization."""
        original = Snapshot.create("Test", modules=["m1", "m2"])

        data = original.to_dict()
        restored = Snapshot.from_dict(data)

        assert restored.id == original.id
        assert restored.description == original.description
        assert restored.modules == original.modules


class TestRollbackManager:
    """Tests for RollbackManager class."""

    @pytest.fixture
    def manager(self, temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> RollbackManager:
        """Create a rollback manager with temp directory."""
        # Patch the backup directory
        import myshell_rfd.core.rollback as rollback_module

        snapshots_dir = temp_dir / "snapshots"
        monkeypatch.setattr(rollback_module, "SNAPSHOTS_DIR", snapshots_dir)
        monkeypatch.setattr(rollback_module, "SNAPSHOT_INDEX", snapshots_dir / "index.json")

        return RollbackManager(max_snapshots=5)

    def test_create_snapshot(self, manager: RollbackManager, temp_dir: Path):
        """Test creating a snapshot."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("original content")

        snapshot = manager.create_snapshot(
            "Test snapshot",
            [test_file],
            modules=["TestModule"],
        )

        assert snapshot is not None
        assert snapshot.description == "Test snapshot"
        assert len(snapshot.files) == 1
        assert snapshot.files[0].existed is True

    def test_list_snapshots(self, manager: RollbackManager, temp_dir: Path):
        """Test listing snapshots."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        manager.create_snapshot("Snapshot 1", [test_file])
        manager.create_snapshot("Snapshot 2", [test_file])

        snapshots = list(manager.list_snapshots())

        assert len(snapshots) == 2
        # Newest first
        assert snapshots[0].description == "Snapshot 2"

    def test_get_snapshot(self, manager: RollbackManager, temp_dir: Path):
        """Test getting snapshot by ID."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        created = manager.create_snapshot("Test", [test_file])

        found = manager.get_snapshot(created.id)

        assert found is not None
        assert found.id == created.id

    def test_get_snapshot_by_prefix(self, manager: RollbackManager, temp_dir: Path):
        """Test getting snapshot by ID prefix."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        created = manager.create_snapshot("Test", [test_file])
        prefix = created.id[:4]

        found = manager.get_snapshot(prefix)

        assert found is not None
        assert found.id == created.id

    def test_rollback(self, manager: RollbackManager, temp_dir: Path):
        """Test rolling back to a snapshot."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("original")

        snapshot = manager.create_snapshot("Before change", [test_file])

        # Modify file
        test_file.write_text("modified")
        assert test_file.read_text() == "modified"

        # Rollback
        result = manager.rollback(snapshot.id)

        assert result is True
        assert test_file.read_text() == "original"

    def test_rollback_nonexistent(self, manager: RollbackManager):
        """Test rolling back to nonexistent snapshot."""
        result = manager.rollback("nonexistent")

        assert result is False

    def test_delete_snapshot(self, manager: RollbackManager, temp_dir: Path):
        """Test deleting a snapshot."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        snapshot = manager.create_snapshot("Test", [test_file])

        result = manager.delete_snapshot(snapshot.id)

        assert result is True
        assert manager.get_snapshot(snapshot.id) is None

    def test_max_snapshots_cleanup(self, manager: RollbackManager, temp_dir: Path):
        """Test automatic cleanup of old snapshots."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        # Create more snapshots than max
        for i in range(7):
            manager.create_snapshot(f"Snapshot {i}", [test_file])

        snapshots = list(manager.list_snapshots())

        # Should be limited to max (5)
        assert len(snapshots) <= 5

    def test_clear_all(self, manager: RollbackManager, temp_dir: Path):
        """Test clearing all snapshots."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        manager.create_snapshot("Snapshot 1", [test_file])
        manager.create_snapshot("Snapshot 2", [test_file])

        count = manager.clear_all()

        assert count == 2
        assert len(list(manager.list_snapshots())) == 0
