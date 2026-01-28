"""Module card widget for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Label, Static

from myshell_rfd.core.module_base import BaseModule


class ModuleCard(Static):
    """A card widget displaying module information.

    Attributes:
        module: The module to display.
    """

    class Selected(Message):
        """Message sent when module is selected."""

        def __init__(self, module: BaseModule) -> None:
            super().__init__()
            self.module = module

    DEFAULT_CSS = """
    ModuleCard {
        height: auto;
        padding: 1;
        margin: 1;
        background: $panel;
        border: solid $primary;
    }

    ModuleCard:hover {
        background: $primary-lighten-2;
        border: solid $primary-lighten-1;
    }

    ModuleCard.installed {
        border: solid $success;
    }

    ModuleCard.unavailable {
        opacity: 0.6;
    }

    .card-header {
        height: 1;
    }

    .card-name {
        text-style: bold;
    }

    .card-status {
        dock: right;
    }

    .card-description {
        color: $text-muted;
    }

    .card-tags {
        color: $primary;
        text-style: italic;
    }
    """

    def __init__(self, module: BaseModule, **kwargs) -> None:
        """Initialize the module card.

        Args:
            module: The module to display.
            **kwargs: Additional widget arguments.
        """
        super().__init__(**kwargs)
        self._module = module

        # Add classes based on status
        if module.check_installed():
            self.add_class("installed")
        if not module.check_available():
            self.add_class("unavailable")

    @property
    def module(self) -> BaseModule:
        """Get the module."""
        return self._module

    def compose(self) -> ComposeResult:
        """Compose the card layout."""
        info = self._module.info

        # Status indicator
        if self._module.check_installed():
            status = "[green]● Installed[/green]"
        elif self._module.check_available():
            status = "[blue]○ Available[/blue]"
        else:
            status = "[yellow]⊘ Missing deps[/yellow]"

        with Horizontal(classes="card-header"):
            yield Label(info.name, classes="card-name")
            yield Label(status, classes="card-status")

        yield Label(info.description, classes="card-description")

        if info.tags:
            tags_str = " ".join(f"#{tag}" for tag in info.tags[:5])
            yield Label(tags_str, classes="card-tags")

    def on_click(self) -> None:
        """Handle click event."""
        self.post_message(self.Selected(self._module))
