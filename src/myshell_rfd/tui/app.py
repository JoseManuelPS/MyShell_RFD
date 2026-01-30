"""Main TUI application for MyShell_RFD.

Provides the Textual-based terminal user interface.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from myshell_rfd import __version__
from myshell_rfd.tui.screens.main import MainScreen


class MyShellApp(App[None]):
    """MyShell_RFD Terminal User Interface.

    A modern TUI for configuring shell environments.
    """

    TITLE = "MyShell_RFD"
    SUB_TITLE = f"v{__version__}"
    CSS_PATH = None  # Will use inline CSS

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("?", "help", "Help", show=True),
        Binding("d", "toggle_dark", "Dark/Light", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("i", "install", "Install"),
        Binding("u", "uninstall", "Uninstall"),
        Binding("a", "auto_detect", "Auto-detect"),
        Binding("c", "clean", "Clean"),
        Binding("p", "profiles", "Profiles"),
        Binding("s", "settings", "Settings"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    .module-card {
        background: $panel;
        border: solid $primary;
        margin: 1;
        padding: 1;
        height: auto;
    }

    .module-card:hover {
        background: $primary-lighten-2;
    }

    .module-card.installed {
        border: solid $success;
    }

    .module-name {
        text-style: bold;
        color: $text;
    }

    .module-description {
        color: $text-muted;
    }

    .module-status {
        dock: right;
    }

    .status-installed {
        color: $success;
    }

    .status-available {
        color: $primary;
    }

    .status-unavailable {
        color: $warning;
    }

    .category-header {
        background: $primary-darken-2;
        padding: 1;
        text-style: bold;
        text-align: center;
    }

    #sidebar {
        width: 30;
        dock: left;
        background: $panel;
        border-right: solid $primary;
    }

    #content {
        width: 1fr;
        padding: 1;
    }

    .progress-panel {
        height: 5;
        margin: 1;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    DataTable {
        height: 100%;
    }

    DataTable > .datatable--header {
        text-style: bold;
        background: $primary;
    }

    .button-bar {
        dock: bottom;
        height: 3;
        padding: 1;
        background: $panel;
    }

    Button {
        margin-right: 1;
    }

    Button.primary {
        background: $primary;
    }

    Button.success {
        background: $success;
    }

    Button.danger {
        background: $error;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield MainScreen()
        yield Footer()

    def on_mount(self) -> None:
        """Check prerequisites on app startup."""
        from myshell_rfd.core.installer import get_installer

        installer = get_installer()
        status = installer.get_prerequisites_status()

        if not status.all_ok:
            missing = ", ".join(status.missing)
            self.notify(
                f"Missing prerequisites: {missing}\nRun 'myshell doctor --fix' to resolve.",
                title="Prerequisites Warning",
                severity="warning",
                timeout=10,
            )

    def action_toggle_dark(self) -> None:
        """Toggle dark/light theme."""
        self.dark = not self.dark

    def action_help(self) -> None:
        """Show help screen."""
        from myshell_rfd.tui.screens.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_refresh(self) -> None:
        """Refresh the current view."""
        self.query_one(MainScreen).refresh_modules()

    def action_install(self) -> None:
        """Install selected module."""
        self.query_one(MainScreen).action_install()

    def action_uninstall(self) -> None:
        """Uninstall selected module."""
        self.query_one(MainScreen).action_uninstall()

    def action_auto_detect(self) -> None:
        """Run auto-detection."""
        self.query_one(MainScreen).action_auto_detect()

    def action_clean(self) -> None:
        """Clean all configuration."""
        self.query_one(MainScreen).action_clean()

    def action_profiles(self) -> None:
        """Show profiles screen."""
        self.query_one(MainScreen).action_profiles()

    def action_settings(self) -> None:
        """Show settings screen."""
        self.query_one(MainScreen).action_settings()


def run() -> None:
    """Run the TUI application."""
    app = MyShellApp()
    app.run()


if __name__ == "__main__":
    run()
