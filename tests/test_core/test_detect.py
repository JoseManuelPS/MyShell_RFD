"""Tests for binary detection utility."""

from pathlib import Path

import pytest

from myshell_rfd.utils.detect import BinaryDetector, ToolCategory, ToolInfo


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
        assert path.exists()

    def test_get_binary_path_not_found(self, detector: BinaryDetector):
        """Test getting path for nonexistent binary."""
        path = detector.get_binary_path("nonexistent_binary_xyz123")

        assert path is None

    def test_get_version(self, detector: BinaryDetector):
        """Test getting binary version."""
        # Most binaries support --version
        version = detector.get_version("ls")

        # May or may not work depending on ls implementation
        # Just verify it doesn't crash
        assert version is None or isinstance(version, str)

    def test_get_tool_info(self, detector: BinaryDetector):
        """Test getting tool info."""
        info = detector.get_tool_info("zsh")

        assert isinstance(info, ToolInfo)
        assert info.name == "zsh"
        assert info.category == ToolCategory.SHELL

    def test_get_tool_info_unknown(self, detector: BinaryDetector):
        """Test getting info for unknown tool."""
        info = detector.get_tool_info("unknown_tool_xyz")

        assert isinstance(info, ToolInfo)
        assert info.name == "unknown_tool_xyz"
        assert info.installed is False
        assert info.category == ToolCategory.OTHER

    def test_scan_known_tools(self, detector: BinaryDetector):
        """Test scanning for known tools."""
        tools = detector.scan_known_tools()

        assert isinstance(tools, dict)
        assert "zsh" in tools

    def test_get_installed_tools(self, detector: BinaryDetector):
        """Test getting installed tools."""
        installed = list(detector.get_installed_tools())

        # Should find at least some tools
        assert isinstance(installed, list)
        for tool in installed:
            assert isinstance(tool, ToolInfo)
            assert tool.installed is True

    def test_get_tools_by_category(self, detector: BinaryDetector):
        """Test filtering tools by category."""
        shell_tools = list(detector.get_tools_by_category(ToolCategory.SHELL))

        for tool in shell_tools:
            assert tool.category == ToolCategory.SHELL

    def test_get_system_info(self, detector: BinaryDetector):
        """Test getting system info."""
        info = detector.get_system_info()

        assert info.os_name is not None
        assert info.arch is not None
        assert info.shell is not None
        assert info.home is not None
        assert isinstance(info.tools, dict)

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
        assert "custom" in str(custom)

    def test_cache_clearing(self, detector: BinaryDetector):
        """Test cache clearing."""
        # Populate cache
        detector.get_tool_info("zsh")
        assert len(detector._cache) > 0

        detector.clear_cache()
        assert len(detector._cache) == 0
