"""Tests for configuration module."""

import tempfile
from pathlib import Path

import pytest

from myshell_rfd.core.config import (
    AppConfig,
    ModuleConfig,
    ModuleState,
    ProfileConfig,
)


class TestModuleConfig:
    """Tests for ModuleConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ModuleConfig()

        assert config.enabled is True
        assert config.state == ModuleState.NOT_INSTALLED
        assert config.installed_at is None
        assert config.settings == {}

    def test_settings(self):
        """Test settings dictionary."""
        config = ModuleConfig(settings={"key": "value"})

        assert config.settings["key"] == "value"


class TestProfileConfig:
    """Tests for ProfileConfig."""

    def test_default_values(self):
        """Test default profile values."""
        profile = ProfileConfig()

        assert profile.name == "default"
        assert profile.description == ""
        assert profile.modules == {}

    def test_enable_module(self):
        """Test enabling a module."""
        profile = ProfileConfig()
        profile.enable_module("test", setting1="value1")

        assert "test" in profile.modules
        assert profile.modules["test"].enabled is True
        assert profile.modules["test"].settings["setting1"] == "value1"

    def test_disable_module(self):
        """Test disabling a module."""
        profile = ProfileConfig()
        profile.enable_module("test")
        profile.disable_module("test")

        assert profile.modules["test"].enabled is False

    def test_is_module_enabled(self):
        """Test checking module status."""
        profile = ProfileConfig()

        assert profile.is_module_enabled("test") is False

        profile.enable_module("test")
        assert profile.is_module_enabled("test") is True

        profile.disable_module("test")
        assert profile.is_module_enabled("test") is False

    def test_get_enabled_modules(self):
        """Test getting enabled modules list."""
        profile = ProfileConfig()
        profile.enable_module("module1")
        profile.enable_module("module2")
        profile.enable_module("module3")
        profile.disable_module("module2")

        enabled = profile.get_enabled_modules()

        assert "module1" in enabled
        assert "module2" not in enabled
        assert "module3" in enabled


class TestAppConfig:
    """Tests for AppConfig."""

    def test_default_values(self):
        """Test default application config."""
        config = AppConfig()

        assert config.version == "2.0.0"
        assert config.active_profile == "default"
        assert config.offline_mode is False
        assert "default" in config.profiles

    def test_current_profile(self):
        """Test getting current profile."""
        config = AppConfig()

        profile = config.current_profile
        assert profile.name == "default"

    def test_create_profile(self):
        """Test creating a new profile."""
        config = AppConfig()

        profile = config.create_profile("work", description="Work config")

        assert "work" in config.profiles
        assert profile.name == "work"
        assert profile.description == "Work config"

    def test_create_duplicate_profile_fails(self):
        """Test that creating duplicate profile raises error."""
        config = AppConfig()
        config.create_profile("work")

        with pytest.raises(ValueError, match="already exists"):
            config.create_profile("work")

    def test_switch_profile(self):
        """Test switching profiles."""
        config = AppConfig()
        config.create_profile("work")

        profile = config.switch_profile("work")

        assert config.active_profile == "work"
        assert profile.name == "work"

    def test_switch_nonexistent_profile_fails(self):
        """Test that switching to nonexistent profile raises error."""
        config = AppConfig()

        with pytest.raises(ValueError, match="does not exist"):
            config.switch_profile("nonexistent")

    def test_delete_profile(self):
        """Test deleting a profile."""
        config = AppConfig()
        config.create_profile("work")

        result = config.delete_profile("work")

        assert result is True
        assert "work" not in config.profiles

    def test_delete_active_profile_fails(self):
        """Test that deleting active profile raises error."""
        config = AppConfig()

        with pytest.raises(ValueError, match="active profile"):
            config.delete_profile("default")

    def test_list_profiles(self):
        """Test listing profiles."""
        config = AppConfig()
        config.create_profile("work")
        config.create_profile("personal")

        profiles = config.list_profiles()

        assert "default" in profiles
        assert "work" in profiles
        assert "personal" in profiles

    def test_toml_roundtrip(self, temp_dir: Path):
        """Test saving and loading TOML."""
        config = AppConfig()
        config.create_profile("work", description="Work")
        config.profiles["work"].enable_module("test", key="value")

        config_file = temp_dir / "config.toml"
        config.to_toml(config_file)

        loaded = AppConfig.from_toml(config_file)

        assert loaded.active_profile == config.active_profile
        assert "work" in loaded.profiles
        assert loaded.profiles["work"].description == "Work"
        assert loaded.profiles["work"].is_module_enabled("test")

    def test_export_import_profile(self, temp_dir: Path):
        """Test exporting and importing profiles."""
        config = AppConfig()
        config.create_profile("export_test", description="Test export")
        config.profiles["export_test"].enable_module("module1")

        export_file = temp_dir / "exported.toml"
        config.export_profile("export_test", export_file)

        # Import into new config
        new_config = AppConfig()
        imported = new_config.import_profile(export_file, name="imported")

        assert imported.name == "imported"
        assert imported.is_module_enabled("module1")
