"""Tests for the doctor CLI command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch

from myshell_rfd.cli import app

runner = CliRunner()

@pytest.fixture
def mock_installer():
    with patch("myshell_rfd.core.installer.get_installer") as mock:
        yield mock

@pytest.fixture
def mock_status(mock_installer):
    # Setup a default status where everything is okay but maybe not sourced
    # or some things missing to trigger output if needed.
    # But current logic only calls fix if --fix or --change-shell is present.
    
    status = MagicMock()
    status.all_ok = False
    status.zsh_installed = True
    status.zsh_default = False  # To test change-shell
    status.git_installed = True
    status.curl_installed = True
    status.omz_installed = True
    status.config_sourced = False
    
    installer = mock_installer.return_value
    installer.get_prerequisites_status.return_value = status
    installer.fix_prerequisites.return_value = True
    
    return status

def test_doctor_no_args_shows_status(mock_installer, mock_status):
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1  # Exits 1 if issues found and no fix
    assert "System Health Check" in result.stdout
    assert "Run with --fix" in result.stdout

def test_doctor_fix_calls_fix_prerequisites(mock_installer, mock_status):
    result = runner.invoke(app, ["doctor", "--fix"])
    
    assert result.exit_code == 0
    installer = mock_installer.return_value
    installer.fix_prerequisites.assert_called_once_with(change_shell=False)
    assert "All issues fixed!" in result.stdout

def test_doctor_change_shell_calls_fix_prerequisites_with_change_shell(mock_installer, mock_status):
    # Test --change-shell long option
    result = runner.invoke(app, ["doctor", "--change-shell"])
    
    assert result.exit_code == 0
    installer = mock_installer.return_value
    installer.fix_prerequisites.assert_called_once_with(change_shell=True)
    assert "All issues fixed!" in result.stdout

def test_doctor_short_c_calls_fix_prerequisites_with_change_shell(mock_installer, mock_status):
    # Test -c short option
    result = runner.invoke(app, ["doctor", "-c"])
    
    assert result.exit_code == 0
    installer = mock_installer.return_value
    # It might have been called twice if we run consecutive tests in same session without reset, 
    # but fixtures reset mocks usually.
    installer.fix_prerequisites.assert_called_once_with(change_shell=True)
    assert "All issues fixed!" in result.stdout

def test_doctor_fix_and_change_shell(mock_installer, mock_status):
    result = runner.invoke(app, ["doctor", "--fix", "-c"])
    
    assert result.exit_code == 0
    installer = mock_installer.return_value
    installer.fix_prerequisites.assert_called_once_with(change_shell=True)
