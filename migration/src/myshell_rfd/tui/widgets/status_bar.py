"""Status bar widget for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Static

from myshell_rfd.core.config import get_config


class StatusBar(Static):
    """A status bar showing current state.

    Displays profile, module count, and system status.
    """

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        dock: bottom;
        background: $primary;
        padding-left: 1;
        padding-right: 1;
    }

    .status-item {
        margin-right: 3;
    }

    .status-label {
        color: $text-muted;
    }

    .status-value {
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the status bar."""
        with Horizontal():
            yield Label("Profile: ", classes="status-label")
            yield Label("default", classes="status-value", id="profile-name")
            yield Label("  │  ", classes="status-label")
            yield Label("Modules: ", classes="status-label")
            yield Label("0", classes="status-value", id="module-count")
            yield Label("  │  ", classes="status-label")
            yield Label("Status: ", classes="status-label")
            yield Label("Ready", classes="status-value", id="status-text")

    def on_mount(self) -> None:
        """Update status on mount."""
        self.refresh_status()

    def refresh_status(self) -> None:
        """Refresh the status bar."""
        try:
            config = get_config()

            # Update profile
            profile_label = self.query_one("#profile-name", Label)
            profile_label.update(config.active_profile)

            # Update module count
            enabled = len(config.current_profile.get_enabled_modules())
            count_label = self.query_one("#module-count", Label)
            count_label.update(str(enabled))
        except Exception:
            pass

    def set_status(self, status: str) -> None:
        """Set the status text.

        Args:
            status: Status message.
        """
        status_label = self.query_one("#status-text", Label)
        status_label.update(status)
