"""Tests for file operations utility."""

from pathlib import Path

import pytest

from myshell_rfd.utils.files import FileOperations


class TestFileOperations:
    """Tests for FileOperations class."""

    def test_backup_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test file backup creation."""
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("original content")

        backup = file_ops.backup_file(test_file)

        assert backup is not None
        assert backup.exists()
        assert backup.read_text() == "original content"

    def test_backup_nonexistent_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test backing up nonexistent file returns None."""
        test_file = temp_dir / "nonexistent.txt"

        backup = file_ops.backup_file(test_file)

        assert backup is None

    def test_read_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test reading file contents."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        content = file_ops.read_file(test_file)

        assert content == "test content"

    def test_read_nonexistent_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test reading nonexistent file returns None."""
        test_file = temp_dir / "nonexistent.txt"

        content = file_ops.read_file(test_file)

        assert content is None

    def test_write_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test writing file contents."""
        test_file = temp_dir / "test.txt"

        file_ops.write_file(test_file, "new content", backup=False)

        assert test_file.read_text() == "new content"

    def test_write_file_with_backup(self, file_ops: FileOperations, temp_dir: Path):
        """Test writing file creates backup."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("original")

        backup = file_ops.write_file(test_file, "new content", backup=True)

        assert test_file.read_text() == "new content"
        assert backup is not None
        assert backup.read_text() == "original"

    def test_write_creates_parents(self, file_ops: FileOperations, temp_dir: Path):
        """Test writing file creates parent directories."""
        test_file = temp_dir / "subdir" / "nested" / "test.txt"

        file_ops.write_file(test_file, "content", create_parents=True)

        assert test_file.exists()
        assert test_file.read_text() == "content"

    def test_append_file(self, file_ops: FileOperations, temp_dir: Path):
        """Test appending to file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("line1")

        file_ops.append_file(test_file, "line2", backup=False)

        assert "line1" in test_file.read_text()
        assert "line2" in test_file.read_text()

    def test_add_to_config_new_section(self, file_ops: FileOperations, temp_dir: Path):
        """Test adding new config section."""
        config_file = temp_dir / "config"
        config_file.write_text("# existing config\n")

        result = file_ops.add_to_config(
            config_file,
            "TestModule",
            "alias test='echo test'",
            backup=False,
        )

        assert result is True
        content = config_file.read_text()
        assert "#  [TestModule]" in content
        assert "alias test='echo test'" in content
        # Ensure no end marker is written
        assert "# <<< MyShell_RFD" not in content

    def test_add_to_config_duplicate(self, file_ops: FileOperations, temp_dir: Path):
        """Test adding duplicate section returns False."""
        config_file = temp_dir / "config"
        config_file.write_text("# existing config\n")

        file_ops.add_to_config(config_file, "TestModule", "content", backup=False)
        result = file_ops.add_to_config(config_file, "TestModule", "new content", backup=False)

        assert result is False

    def test_remove_from_config(self, file_ops: FileOperations, temp_dir: Path):
        """Test removing config section."""
        config_file = temp_dir / "config"
        config_file.write_text("# existing\n")

        file_ops.add_to_config(config_file, "TestModule", "content", backup=False)
        result = file_ops.remove_from_config(config_file, "TestModule", backup=False)

        assert result is True
        content = config_file.read_text()
        assert "#  [TestModule]" not in content
        assert "content" not in content

    def test_remove_from_config_legacy(self, file_ops: FileOperations, temp_dir: Path):
        """Test removing legacy config section."""
        config_file = temp_dir / "config"
        content = (
            "# existing\n"
            "# >>> MyShell_RFD [TestModule]\n"
            "legacy content\n"
            "# <<< MyShell_RFD [TestModule]\n"
        )
        config_file.write_text(content)

        result = file_ops.remove_from_config(config_file, "TestModule", backup=False)

        assert result is True
        content = config_file.read_text()
        assert "TestModule" not in content
        assert "legacy content" not in content

    def test_remove_nonexistent_section(self, file_ops: FileOperations, temp_dir: Path):
        """Test removing nonexistent section returns False."""
        config_file = temp_dir / "config"
        config_file.write_text("# config\n")

        result = file_ops.remove_from_config(config_file, "NonExistent", backup=False)

        assert result is False

    def test_list_backups(self, file_ops: FileOperations, temp_dir: Path):
        """Test listing backups."""
        # Create backups from different files to avoid timestamp collision
        for i in range(3):
            test_file = temp_dir / f"test_{i}.txt"
            test_file.write_text(f"content {i}")
            file_ops.backup_file(test_file)

        backups = list(file_ops.list_backups("test_*.txt.*"))

        assert len(backups) == 3

    def test_restore_backup(self, file_ops: FileOperations, temp_dir: Path):
        """Test restoring from backup."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("original")

        backup = file_ops.backup_file(test_file)
        test_file.write_text("modified")

        result = file_ops.restore_backup(backup, test_file)

        assert result is True
        assert test_file.read_text() == "original"
