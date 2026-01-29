"""Configuration models and management for MyShell_RFD.

Uses dataclasses for models and TOML for persistence.
Implements profile support (E2).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import tomllib  # stdlib since Python 3.11
import tomli_w

from myshell_rfd.utils.files import CONFIG_DIR


# ZSH is the only supported shell
SHELL_TYPE = "zsh"


class ModuleState(str, Enum):
    """Module installation state."""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    CONFIGURED = "configured"
    ERROR = "error"


@dataclass
class ModuleConfig:
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
    settings: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        result: dict[str, Any] = {
            "enabled": self.enabled,
            "state": self.state.value if isinstance(self.state, Enum) else self.state,
            "settings": self.settings,
        }
        if self.installed_at is not None:
            result["installed_at"] = self.installed_at.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModuleConfig:
        """Create from dictionary."""
        state = data.get("state", "not_installed")
        if isinstance(state, str):
            state = ModuleState(state)

        installed_at = data.get("installed_at")
        if isinstance(installed_at, str):
            installed_at = datetime.fromisoformat(installed_at)

        return cls(
            enabled=data.get("enabled", True),
            state=state,
            installed_at=installed_at,
            settings=data.get("settings", {}),
        )


@dataclass
class ShellConfig:
    """Shell-specific configuration.

    Attributes:
        config_file: Path to shell config file.
        plugins: Enabled plugins.
        theme: Shell theme name.
        aliases: Custom aliases.
    """

    config_file: Path | None = None
    plugins: list[str] = field(default_factory=list)
    theme: str = "default"
    aliases: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and convert types after initialization."""
        if isinstance(self.config_file, str):
            self.config_file = Path(self.config_file)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        result: dict[str, Any] = {
            "plugins": self.plugins,
            "theme": self.theme,
            "aliases": self.aliases,
        }
        if self.config_file is not None:
            result["config_file"] = str(self.config_file)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShellConfig:
        """Create from dictionary."""
        config_file = data.get("config_file")
        if isinstance(config_file, str):
            config_file = Path(config_file)

        return cls(
            config_file=config_file,
            plugins=data.get("plugins", []),
            theme=data.get("theme", "default"),
            aliases=data.get("aliases", {}),
        )

    def copy(self) -> ShellConfig:
        """Create a deep copy."""
        return ShellConfig(
            config_file=self.config_file,
            plugins=self.plugins.copy(),
            theme=self.theme,
            aliases=self.aliases.copy(),
        )


@dataclass
class ProfileConfig:
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
    modules: dict[str, ModuleConfig] = field(default_factory=dict)
    shell_config: ShellConfig = field(default_factory=ShellConfig)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "modules": {name: cfg.to_dict() for name, cfg in self.modules.items()},
            "shell_config": self.shell_config.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfileConfig:
        """Create from dictionary."""
        modules = {}
        for name, cfg_data in data.get("modules", {}).items():
            modules[name] = ModuleConfig.from_dict(cfg_data)

        shell_config_data = data.get("shell_config", {})
        shell_config = ShellConfig.from_dict(shell_config_data)

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()

        return cls(
            name=data.get("name", "default"),
            description=data.get("description", ""),
            modules=modules,
            shell_config=shell_config,
            created_at=created_at,
            updated_at=updated_at,
        )

    def copy(self) -> ProfileConfig:
        """Create a deep copy."""
        return ProfileConfig(
            name=self.name,
            description=self.description,
            modules={name: copy.deepcopy(cfg) for name, cfg in self.modules.items()},
            shell_config=self.shell_config.copy(),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


@dataclass
class AppConfig:
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
    profiles: dict[str, ProfileConfig] = field(default_factory=dict)
    last_update_check: datetime | None = None

    def __post_init__(self) -> None:
        """Ensure default profile exists."""
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
            profile = source.copy()
            profile.name = name
            profile.description = description or source.description
            profile.created_at = datetime.now()
            profile.updated_at = datetime.now()
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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        result: dict[str, Any] = {
            "version": self.version,
            "active_profile": self.active_profile,
            "auto_detect": self.auto_detect,
            "offline_mode": self.offline_mode,
            "debug": self.debug,
            "profiles": {name: p.to_dict() for name, p in self.profiles.items()},
        }
        if self.last_update_check is not None:
            result["last_update_check"] = self.last_update_check.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        """Create from dictionary."""
        profiles = {}
        for name, profile_data in data.get("profiles", {}).items():
            profiles[name] = ProfileConfig.from_dict(profile_data)

        last_update_check = data.get("last_update_check")
        if isinstance(last_update_check, str):
            last_update_check = datetime.fromisoformat(last_update_check)

        config = cls(
            version=data.get("version", "2.0.0"),
            active_profile=data.get("active_profile", "default"),
            auto_detect=data.get("auto_detect", True),
            offline_mode=data.get("offline_mode", False),
            debug=data.get("debug", False),
            profiles=profiles,
            last_update_check=last_update_check,
        )
        return config

    @classmethod
    def from_toml(cls, path: Path) -> AppConfig:
        """Load configuration from TOML file.

        Args:
            path: Path to TOML file.

        Returns:
            Loaded configuration.
        """
        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    def to_toml(self, path: Path) -> None:
        """Save configuration to TOML file.

        Args:
            path: Path to save to.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()

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
        data = profile.to_dict()

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
            data = tomllib.load(f)

        profile = ProfileConfig.from_dict(data)

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
