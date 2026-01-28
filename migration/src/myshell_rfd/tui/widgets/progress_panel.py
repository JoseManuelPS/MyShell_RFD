"""Progress panel widget for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar, Static


class ProgressPanel(Static):
    """A panel showing installation progress.

    Displays current operation, progress bar, and status messages.
    """

    DEFAULT_CSS = """
    ProgressPanel {
        height: 5;
        padding: 1;
        margin: 1;
        background: $panel;
        border: solid $primary;
    }

    .progress-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .progress-status {
        color: $text-muted;
    }

    ProgressBar {
        height: 1;
    }
    """

    def __init__(
        self,
        title: str = "Progress",
        total: float = 100.0,
        **kwargs,
    ) -> None:
        """Initialize the progress panel.

        Args:
            title: Panel title.
            total: Total progress value.
            **kwargs: Additional widget arguments.
        """
        super().__init__(**kwargs)
        self._title = title
        self._total = total
        self._current = 0.0
        self._status = ""

    def compose(self) -> ComposeResult:
        """Compose the panel layout."""
        yield Label(self._title, classes="progress-title")
        yield ProgressBar(total=self._total, show_eta=True)
        yield Label("", classes="progress-status", id="status-label")

    def update_progress(self, value: float, status: str = "") -> None:
        """Update the progress.

        Args:
            value: Current progress value.
            status: Status message.
        """
        self._current = value
        self._status = status

        progress_bar = self.query_one(ProgressBar)
        progress_bar.update(progress=value)

        if status:
            status_label = self.query_one("#status-label", Label)
            status_label.update(status)

    def advance(self, amount: float = 1.0, status: str = "") -> None:
        """Advance progress by an amount.

        Args:
            amount: Amount to advance.
            status: Status message.
        """
        self.update_progress(self._current + amount, status)

    def complete(self, message: str = "Complete") -> None:
        """Mark progress as complete.

        Args:
            message: Completion message.
        """
        self.update_progress(self._total, message)

    def reset(self, total: float | None = None) -> None:
        """Reset the progress.

        Args:
            total: New total value.
        """
        if total is not None:
            self._total = total
            progress_bar = self.query_one(ProgressBar)
            progress_bar.total = total

        self._current = 0.0
        self.update_progress(0.0, "")
