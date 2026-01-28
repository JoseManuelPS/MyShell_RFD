"""Input modal screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class InputScreen(ModalScreen[str | None]):
    """Modal input dialog.

    Returns the input string or None if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    CSS = """
    InputScreen {
        align: center middle;
    }

    #input-container {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    #input-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    #input-label {
        margin-bottom: 1;
    }

    #input-field {
        margin-bottom: 2;
    }

    #input-buttons {
        align: center middle;
        height: 3;
    }

    Button {
        margin-left: 1;
        margin-right: 1;
    }
    """

    def __init__(
        self,
        title: str,
        prompt: str,
        default: str = "",
        placeholder: str = "",
    ) -> None:
        """Initialize the input dialog.

        Args:
            title: Dialog title.
            prompt: Input prompt.
            default: Default value.
            placeholder: Placeholder text.
        """
        super().__init__()
        self._title = title
        self._prompt = prompt
        self._default = default
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="input-container"):
            yield Label(self._title, id="input-title")
            yield Label(self._prompt, id="input-label")
            yield Input(
                value=self._default,
                placeholder=self._placeholder,
                id="input-field",
            )
            with Horizontal(id="input-buttons"):
                yield Button("OK", variant="primary", id="btn-ok")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        """Focus the input field."""
        self.query_one("#input-field", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-ok":
            value = self.query_one("#input-field", Input).value
            self.dismiss(value if value else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        self.dismiss(event.value if event.value else None)

    def action_cancel(self) -> None:
        """Cancel the input."""
        self.dismiss(None)
