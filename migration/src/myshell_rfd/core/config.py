"""Configuration models and management for MyShell_RFD.

Uses Pydantic v2 for validation and TOML for persistence.
Implements profile support (E2).
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Self

import tomli
import tomli_w
from pydantic import BaseModel, Field, field_validator

from myshell_rfd.utils.files import CONFIG_DIR, PROFILES_DIR


# ZSH is the only supported shell
SHELL_TYPE = "zsh"


class ModuleState(str, Enum):
    """Module installation state."""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    CONFIGURED = "configured"
    ERROR = "error"


class ModuleConfig(BaseModel):
    """Configuration for a single module.

    Attributes:
        enabled: Whether the module is enabled.
        state: Current installation state.
        installed_at: When the module was installed.
        settings: Module-specific settings.
    """

    enabled: bool = True
    state: ModuleState = ModuleState.NOT_INSTALLED
    installed_at: datetime | None = None
    settings: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class ShellConfig(BaseModel):
    """Shell-specific configuration.

    Attributes:
        config_file: Path to shell config file.
        plugins: Enabled plugins.
        theme: Shell theme name.
        aliases: Custom aliases.
    """

    config_file: Path | None = None
    plugins: list[str] = Field(default_factory=list)
    theme: str = "default"
    aliases: dict[str, str] = Field(default_factory=dict)

    @field_validator("config_file", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path | None:
        """Convert string to Path."""
        if v is None:
            return None
        return Path(v) if isinstance(v, str) else v


class ProfileConfig(BaseModel):
    """A named configuration profile.

    Attributes:
        name: Profile name.
        description: Profile description.
        modules: Module configurations.
        shell_config: ZSH-specific settings.
        created_at: When the profile was created.
        updated_at: Last update time.
    """

    name: str = "default"
    description: str = ""
    modules: dict[str, ModuleConfig] = Field(default_factory=dict)
    shell_config: ShellConfig = Field(default_factory=ShellConfig)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"use_enum_values": True}

    def enable_module(self, name: str, **settings: Any) -> None:
        """Enable a module with optional settings.

        Args:
            name: Module name.
            **settings: Module-specific settings.
        """
        if name not in self.modules:
            self.modules[name] = ModuleConfig()

        self.modules[name].enabled = True
        if settings:
            self.modules[name].settings.update(settings)

        self.updated_at = datetime.now()

    def disable_module(self, name: str) -> None:
        """Disable a module.

        Args:
            name: Module name.
        """
        if name in self.modules:
            self.modules[name].enabled = False
            self.updated_at = datetime.now()

    def is_module_enabled(self, name: str) -> bool:
        """Check if a module is enabled.

        Args:
            name: Module name.

        Returns:
            True if enabled, False otherwise.
        """
        return name in self.modules and self.modules[name].enabled

    def get_enabled_modules(self) -> list[str]:
        """Get list of enabled module names.

        Returns:
            List of enabled module names.
        """
        return [name for name, config in self.modules.items() if config.enabled]


class AppConfig(BaseModel):
    """Main application configuration.

    Attributes:
        version: Config schema version.
        active_profile: Name of the active profile.
        auto_detect: Enable automatic tool detection (E3).
        offline_mode: Enable offline mode (E5).
        debug: Enable debug logging.
        profiles: Available profiles (E2).
        last_update_check: Last update check timestamp.
    """

    version: str = "2.0.0"
    active_profile: str = "default"
    auto_detect: bool = True
    offline_mode: bool = False
    debug: bool = False
    profiles: dict[str, ProfileConfig] = Field(default_factory=dict)
    last_update_check: datetime | None = None

    model_config = {"use_enum_values": True}

    def __init__(self, **data: Any) -> None:
        """Initialize with default profile if empty."""
        super().__init__(**data)
        if not self.profiles:
            self.profiles["default"] = ProfileConfig(name="default")

    @property
    def current_profile(self) -> ProfileConfig:
        """Get the active profile.

        Returns:
            The current profile configuration.
        """
        if self.active_profile not in self.profiles:
            self.profiles[self.active_profile] = ProfileConfig(name=self.active_profile)
        return self.profiles[self.active_profile]

    def switch_profile(self, name: str) -> ProfileConfig:
        """Switch to a different profile.

        Args:
            name: Profile name to switch to.

        Returns:
            The newly active profile.

        Raises:
            ValueError: If profile doesn't exist.
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' does not exist")

        self.active_profile = name
        return self.profiles[name]

    def create_profile(
        self,
        name: str,
        *,
        description: str = "",
        copy_from: str | None = None,
    ) -> ProfileConfig:
        """Create a new profile.

        Args:
            name: Profile name.
            description: Profile description.
            copy_from: Copy settings from existing profile.

        Returns:
            The new profile.

        Raises:
            ValueError: If profile already exists.
        """
        if name in self.profiles:
            raise ValueError(f"Profile '{name}' already exists")

        if copy_from and copy_from in self.profiles:
            # Deep copy from existing profile
            source = self.profiles[copy_from]
            profile = ProfileConfig(
                name=name,
                description=description or source.description,
                modules=source.modules.copy(),
                shell_config=source.shell_config.model_copy(),
            )
        else:
            profile = ProfileConfig(
                name=name,
                description=description,
            )

        self.profiles[name] = profile
        return profile

    def delete_profile(self, name: str) -> bool:
        """Delete a profile.

        Args:
            name: Profile name to delete.

        Returns:
            True if deleted, False if not found.

        Raises:
            ValueError: If trying to delete the active profile.
        """
        if name == self.active_profile:
            raise ValueError("Cannot delete the active profile")

        if name in self.profiles:
            del self.profiles[name]
            return True

        return False

    def list_profiles(self) -> list[str]:
        """Get list of profile names.

        Returns:
            List of profile names.
        """
        return list(self.profiles.keys())

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        """Load configuration from TOML file.

        Args:
            path: Path to TOML file.

        Returns:
            Loaded configuration.
        """
        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomli.load(f)

        return cls.model_validate(data)

    def to_toml(self, path: Path) -> None:
        """Save configuration to TOML file.

        Args:
            path: Path to save to.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict, exclude None values (not TOML serializable)
        data = self.model_dump(mode="json", exclude_none=True)

        with open(path, "wb") as f:
            tomli_w.dump(data, f)

    def export_profile(self, name: str, path: Path) -> None:
        """Export a profile to a TOML file.

        Args:
            name: Profile name.
            path: Export path.

        Raises:
            ValueError: If profile doesn't exist.
        """
        if name not in self.profiles:
            raise ValueError(f"Profile '{name}' does not exist")

        profile = self.profiles[name]
        data = profile.model_dump(mode="json", exclude_none=True)

        with open(path, "wb") as f:
            tomli_w.dump(data, f)

    def import_profile(self, path: Path, name: str | None = None) -> ProfileConfig:
        """Import a profile from a TOML file.

        Args:
            path: Path to import from.
            name: Override profile name.

        Returns:
            The imported profile.

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"Profile file not found: {path}")

        with open(path, "rb") as f:
            data = tomli.load(f)

        profile = ProfileConfig.model_validate(data)

        if name:
            profile.name = name

        self.profiles[profile.name] = profile
        return profile


# Global config paths
CONFIG_FILE = CONFIG_DIR / "config.toml"

# Global config instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        The application configuration.
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from file.

    Args:
        path: Config file path. Defaults to ~/.myshell_rfd/config.toml.

    Returns:
        The loaded configuration.
    """
    config_path = path or CONFIG_FILE

    if config_path.exists():
        return AppConfig.from_toml(config_path)

    return AppConfig()


def save_config(config: AppConfig | None = None, path: Path | None = None) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save. Defaults to global config.
        path: Save path. Defaults to ~/.myshell_rfd/config.toml.
    """
    cfg = config or get_config()
    config_path = path or CONFIG_FILE

    cfg.to_toml(config_path)


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: Configuration to set.
    """
    global _config
    _config = config
