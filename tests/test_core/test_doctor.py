"""Tests for prerequisites and doctor functionality."""

from pathlib import Path

from myshell_rfd.core.installer import PrerequisiteStatus


class TestPrerequisiteStatus:
    """Tests for PrerequisiteStatus dataclass."""

    def test_all_ok_true_when_all_installed(self):
        """Test all_ok returns True when all prerequisites are met."""
        status = PrerequisiteStatus(
            zsh_installed=True,
            zsh_default=True,
            git_installed=True,
            curl_installed=True,
            omz_installed=True,
            config_sourced=True,
        )

        assert status.all_ok is True

    def test_all_ok_false_when_zsh_missing(self):
        """Test all_ok returns False when ZSH is missing."""
        status = PrerequisiteStatus(
            zsh_installed=False,
            zsh_default=False,
            git_installed=True,
            curl_installed=True,
            omz_installed=False,
            config_sourced=False,
        )

        assert status.all_ok is False

    def test_all_ok_false_when_zsh_not_default(self):
        """Test all_ok returns False when ZSH is not default shell."""
        status = PrerequisiteStatus(
            zsh_installed=True,
            zsh_default=False,
            git_installed=True,
            curl_installed=True,
            omz_installed=True,
            config_sourced=True,
        )

        assert status.all_ok is False

    def test_missing_returns_correct_list(self):
        """Test missing property returns correct list."""
        status = PrerequisiteStatus(
            zsh_installed=False,
            zsh_default=False,
            git_installed=True,
            curl_installed=False,
            omz_installed=False,
            config_sourced=False,
        )

        missing = status.missing
        assert "zsh" in missing
        assert "curl" in missing
        assert "git" not in missing

    def test_missing_includes_zsh_not_default(self):
        """Test missing includes 'zsh not default' when applicable."""
        status = PrerequisiteStatus(
            zsh_installed=True,
            zsh_default=False,
            git_installed=True,
            curl_installed=True,
            omz_installed=True,
            config_sourced=True,
        )

        missing = status.missing
        assert "zsh not default shell" in missing
        assert "zsh" not in missing  # zsh is installed, so shouldn't be in missing


class TestInstallerPrerequisites:
    """Tests for InstallerService prerequisites methods."""

    def test_get_prerequisites_status_returns_status(self, temp_home: Path):  # noqa: ARG002
        """Test get_prerequisites_status returns PrerequisiteStatus."""
        from myshell_rfd.core.installer import get_installer

        installer = get_installer()
        status = installer.get_prerequisites_status()

        assert isinstance(status, PrerequisiteStatus)
        # In most test environments, git should be installed
        # But we just verify the structure is correct
        assert hasattr(status, "zsh_installed")
        assert hasattr(status, "zsh_default")
        assert hasattr(status, "git_installed")
        assert hasattr(status, "curl_installed")
