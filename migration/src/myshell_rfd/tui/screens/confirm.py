"""Confirmation modal screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmScreen(ModalScreen[bool]):
    """Modal confirmation dialog.

    Returns True if confirmed, False if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]

    CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #confirm-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $warning;
        padding: 2;
    }

    #confirm-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    #confirm-message {
        text-align: center;
        margin-bottom: 2;
    }

    #confirm-buttons {
        align: center middle;
        height: 3;
    }

    Button {
        margin-left: 1;
        margin-right: 1;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        """Initialize the confirmation dialog.

        Args:
            title: Dialog title.
            message: Confirmation message.
        """
        super().__init__()
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="confirm-container"):
            yield Label(self._title, id="confirm-title")
            yield Label(self._message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes", variant="warning", id="btn-yes")
                yield Button("No", variant="default", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm(self) -> None:
        """Confirm the action."""
        self.dismiss(True)

    def action_cancel(self) -> None:
        """Cancel the action."""
        self.dismiss(False)
