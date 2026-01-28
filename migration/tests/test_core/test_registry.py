"""Tests for module registry."""

import pytest

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import (
    BaseModule,
    ConfigOnlyModule,
    InstallResult,
    ModuleCategory,
    ModuleInfo,
)
from myshell_rfd.core.registry import ModuleRegistry


class MockModule(ConfigOnlyModule):
    """Mock module for testing."""

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="MockModule",
            description="A mock module for testing",
            category=ModuleCategory.TOOLS,
            required_binaries=[],
            tags=["test", "mock"],
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        return "# Mock configuration"


class AnotherMockModule(ConfigOnlyModule):
    """Another mock module."""

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="AnotherMock",
            description="Another mock module",
            category=ModuleCategory.CLOUD,
        )

    def get_config_content(self, config: ModuleConfig) -> str:
        return "# Another mock"


class TestModuleRegistry:
    """Tests for ModuleRegistry class."""

    @pytest.fixture
    def registry(self) -> ModuleRegistry:
        """Create a fresh registry."""
        return ModuleRegistry()

    def test_register_module(self, registry: ModuleRegistry):
        """Test registering a module."""
        registry.register(MockModule)

        assert "MockModule" in registry.list_names()

    def test_get_module(self, registry: ModuleRegistry):
        """Test getting a module by name."""
        registry.register(MockModule)

        module = registry.get("MockModule")

        assert module is not None
        assert module.name == "MockModule"

    def test_get_module_case_insensitive(self, registry: ModuleRegistry):
        """Test case-insensitive module lookup."""
        registry.register(MockModule)

        module = registry.get("mockmodule")

        assert module is not None
        assert module.name == "MockModule"

    def test_get_nonexistent_module(self, registry: ModuleRegistry):
        """Test getting nonexistent module returns None."""
        module = registry.get("NonExistent")

        assert module is None

    def test_get_all_modules(self, registry: ModuleRegistry):
        """Test getting all modules."""
        registry.register(MockModule)
        registry.register(AnotherMockModule)

        modules = list(registry.get_all())

        assert len(modules) == 2

    def test_get_by_category(self, registry: ModuleRegistry):
        """Test filtering by category."""
        registry.register(MockModule)
        registry.register(AnotherMockModule)

        tools = list(registry.get_by_category(ModuleCategory.TOOLS))
        cloud = list(registry.get_by_category(ModuleCategory.CLOUD))

        assert len(tools) == 1
        assert tools[0].name == "MockModule"
        assert len(cloud) == 1
        assert cloud[0].name == "AnotherMock"

    def test_list_names(self, registry: ModuleRegistry):
        """Test listing module names."""
        registry.register(MockModule)
        registry.register(AnotherMockModule)

        names = registry.list_names()

        assert "AnotherMock" in names
        assert "MockModule" in names
        # Should be sorted
        assert names == sorted(names)

    def test_list_info(self, registry: ModuleRegistry):
        """Test listing module info."""
        registry.register(MockModule)

        infos = registry.list_info()

        assert len(infos) == 1
        assert infos[0].name == "MockModule"
        assert infos[0].description == "A mock module for testing"

    def test_install_module(self, registry: ModuleRegistry):
        """Test installing a module through registry."""
        registry.register(MockModule)

        result = registry.install_module("MockModule", ModuleConfig())

        assert isinstance(result, InstallResult)

    def test_install_nonexistent_module(self, registry: ModuleRegistry):
        """Test installing nonexistent module."""
        result = registry.install_module("NonExistent", ModuleConfig())

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_uninstall_module(self, registry: ModuleRegistry):
        """Test uninstalling a module."""
        registry.register(MockModule)

        result = registry.uninstall_module("MockModule")

        assert isinstance(result, InstallResult)
