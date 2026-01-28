"""Pytest configuration and fixtures for MyShell_RFD tests."""

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from myshell_rfd.core.config import AppConfig, ProfileConfig
from myshell_rfd.utils.files import FileOperations
from myshell_rfd.utils.logger import Logger

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def temp_dir() -> "Iterator[Path]":
    """Provide a temporary directory for tests.

    Yields:
        Path to temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_home(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a fake home directory.

    Args:
        temp_dir: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        Path to fake home directory.
    """
    fake_home = temp_dir / "home"
    fake_home.mkdir()

    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    return fake_home


@pytest.fixture
def logger() -> Logger:
    """Provide a logger instance for tests.

    Returns:
        Logger configured for testing.
    """
    return Logger(debug_mode=True, quiet=False)


@pytest.fixture
def file_ops(temp_dir: Path) -> FileOperations:
    """Provide FileOperations with temp backup directory.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        FileOperations instance.
    """
    backup_dir = temp_dir / "backups"
    backup_dir.mkdir()
    return FileOperations(backup_dir=backup_dir)


@pytest.fixture
def sample_config() -> AppConfig:
    """Provide a sample configuration for tests.

    Returns:
        Sample AppConfig instance.
    """
    config = AppConfig()

    # Add work profile
    work_profile = ProfileConfig(
        name="work",
        description="Work configuration",
    )
    work_profile.enable_module("kubectl", namespace="production")
    work_profile.enable_module("aws", region="us-east-1")
    config.profiles["work"] = work_profile

    # Add personal profile
    personal_profile = ProfileConfig(
        name="personal",
        description="Personal configuration",
    )
    personal_profile.enable_module("docker")
    personal_profile.enable_module("fzf")
    config.profiles["personal"] = personal_profile

    return config


@pytest.fixture
def mock_zshrc(temp_home: Path) -> Path:
    """Create a mock .zshrc file.

    Args:
        temp_home: Fake home directory.

    Returns:
        Path to mock .zshrc.
    """
    zshrc = temp_home / ".zshrc"
    zshrc.write_text(
        """# Mock .zshrc
export ZSH="$HOME/.oh-my-zsh"
plugins=(git)
source $ZSH/oh-my-zsh.sh
"""
    )
    return zshrc


@pytest.fixture
def mock_omz(temp_home: Path) -> Path:
    """Create a mock Oh My Zsh directory.

    Args:
        temp_home: Fake home directory.

    Returns:
        Path to mock Oh My Zsh.
    """
    omz = temp_home / ".oh-my-zsh"
    omz.mkdir()
    (omz / "custom").mkdir()
    (omz / "custom" / "plugins").mkdir()
    (omz / "custom" / "themes").mkdir()
    return omz
