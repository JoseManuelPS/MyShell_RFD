"""Tests for built-in modules."""

from unittest.mock import MagicMock

import pytest

from myshell_rfd.core.config import ModuleConfig
from myshell_rfd.core.module_base import ModuleCategory
from myshell_rfd.modules.aws import AWSModule
from myshell_rfd.modules.containers import DockerModule, PodmanModule
from myshell_rfd.modules.kubernetes import HelmModule, KubectlModule
from myshell_rfd.modules.tools import BatcatModule, PLSModule


@pytest.fixture
def mock_deps():
    """Create mock dependencies for modules."""
    logger = MagicMock()
    file_ops = MagicMock()
    runner = MagicMock()
    detector = MagicMock()

    detector.check_binary.return_value = True
    detector.get_shell_config_file.return_value = "/home/test/.zshrc"
    detector.get_zsh_custom_dir.return_value = "/home/test/.oh-my-zsh/custom"

    return {
        "logger": logger,
        "file_ops": file_ops,
        "runner": runner,
        "detector": detector,
    }


class TestAWSModule:
    """Tests for AWS module."""

    def test_info(self, mock_deps):
        """Test module info."""
        module = AWSModule(**mock_deps)
        info = module.info

        assert info.name == "AWS"
        assert info.category == ModuleCategory.CLOUD
        assert "aws" in info.required_binaries

    def test_config_content(self, mock_deps):
        """Test configuration content."""
        module = AWSModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "aws_completer" in content
        assert "bashcompinit" in content


class TestDockerModule:
    """Tests for Docker module."""

    def test_info(self, mock_deps):
        """Test module info."""
        module = DockerModule(**mock_deps)
        info = module.info

        assert info.name == "Docker"
        assert info.category == ModuleCategory.CONTAINER

    def test_config_content(self, mock_deps):
        """Test configuration content."""
        module = DockerModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "alias dps=" in content
        assert "alias di=" in content


class TestPodmanModule:
    """Tests for Podman module."""

    def test_config_with_docker_alias(self, mock_deps):
        """Test config with docker alias enabled."""
        module = PodmanModule(**mock_deps)
        config = ModuleConfig(settings={"docker_alias": True})
        content = module.get_config_content(config)

        assert "alias docker='podman'" in content

    def test_config_without_docker_alias(self, mock_deps):
        """Test config with docker alias disabled."""
        module = PodmanModule(**mock_deps)
        config = ModuleConfig(settings={"docker_alias": False})
        content = module.get_config_content(config)

        assert "alias docker='podman'" not in content


class TestKubectlModule:
    """Tests for Kubectl module."""

    def test_info(self, mock_deps):
        """Test module info."""
        module = KubectlModule(**mock_deps)
        info = module.info

        assert info.name == "Kubectl"
        assert info.category == ModuleCategory.KUBERNETES
        assert "kubectl" in info.required_binaries

    def test_config_content(self, mock_deps):
        """Test configuration content."""
        module = KubectlModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "alias k='kubectl'" in content
        assert "alias kgp=" in content
        assert "kubectl completion zsh" in content

    def test_config_with_krew(self, mock_deps):
        """Test configuration with Krew enabled."""
        module = KubectlModule(**mock_deps)
        config = ModuleConfig(settings={"krew": True})
        content = module.get_config_content(config)

        assert "KREW_ROOT" in content


class TestHelmModule:
    """Tests for Helm module."""

    def test_info(self, mock_deps):
        """Test module info."""
        module = HelmModule(**mock_deps)
        info = module.info

        assert info.name == "Helm"
        assert info.category == ModuleCategory.KUBERNETES

    def test_config_content(self, mock_deps):
        """Test configuration content."""
        module = HelmModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "helm completion zsh" in content


class TestBatcatModule:
    """Tests for Batcat module."""

    def test_check_available_bat(self, mock_deps):
        """Test availability with bat."""
        mock_deps["detector"].check_binary.side_effect = lambda x: x == "bat"
        module = BatcatModule(**mock_deps)

        assert module.check_available() is True

    def test_check_available_batcat(self, mock_deps):
        """Test availability with batcat."""
        mock_deps["detector"].check_binary.side_effect = lambda x: x == "batcat"
        module = BatcatModule(**mock_deps)

        assert module.check_available() is True

    def test_check_available_neither(self, mock_deps):
        """Test unavailable when neither exists."""
        mock_deps["detector"].check_binary.return_value = False
        module = BatcatModule(**mock_deps)

        assert module.check_available() is False

    def test_config_uses_correct_binary(self, mock_deps):
        """Test config uses the correct binary."""
        mock_deps["detector"].check_binary.side_effect = lambda x: x == "batcat"
        module = BatcatModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "alias cat='batcat'" in content


class TestPLSModule:
    """Tests for PLS module."""

    def test_info(self, mock_deps):
        """Test module info."""
        module = PLSModule(**mock_deps)
        info = module.info

        assert info.name == "PLS"
        assert "sudo" in info.required_binaries

    def test_config_content(self, mock_deps):
        """Test configuration content."""
        module = PLSModule(**mock_deps)
        content = module.get_config_content(ModuleConfig())

        assert "alias pls=" in content
        assert "alias please=" in content
        assert "sudo" in content
