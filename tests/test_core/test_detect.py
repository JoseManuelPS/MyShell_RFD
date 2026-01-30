"""Tests for binary detection utility."""

from pathlib import Path
import pytest
from myshell_rfd.utils.detect import BinaryDetector


class TestBinaryDetector:
    """Tests for BinaryDetector class."""

    @pytest.fixture
    def detector(self) -> BinaryDetector:
        """Create detector instance."""
        return BinaryDetector()

    def test_check_binary_exists(self, detector: BinaryDetector):
        """Test checking for existing binary."""
        # 'ls' should exist on all Unix systems
        assert detector.check_binary("ls") is True

    def test_check_binary_not_exists(self, detector: BinaryDetector):
        """Test checking for nonexistent binary."""
        assert detector.check_binary("nonexistent_binary_xyz123") is False

    def test_get_binary_path(self, detector: BinaryDetector):
        """Test getting binary path."""
        path = detector.get_binary_path("ls")

        assert path is not None
        assert Path(path).exists()

    def test_get_binary_path_not_found(self, detector: BinaryDetector):
        """Test getting path for nonexistent binary."""
        path = detector.get_binary_path("nonexistent_binary_xyz123")

        assert path is None

    def test_get_shell_config_file(self, detector: BinaryDetector):
        """Test getting shell config path returns myshell_rfd config."""
        from myshell_rfd.utils.files import SHELL_CONFIG_FILE

        path = detector.get_shell_config_file()

        assert path == SHELL_CONFIG_FILE

    def test_get_zshrc_path(self, detector: BinaryDetector):
        """Test getting .zshrc path."""
        path = detector.get_zshrc_path()

        assert path == Path.home() / ".zshrc"

    def test_get_zsh_custom_dir(self, detector: BinaryDetector):
        """Test getting ZSH custom directory."""
        custom = detector.get_zsh_custom_dir()

        assert isinstance(custom, Path)
        # It's either a custom path or based on .oh-my-zsh or .zsh
        assert "custom" in str(custom) or ".zsh" in str(custom)
