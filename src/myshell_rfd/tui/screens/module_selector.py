"""Module selector screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, OptionList
from textual.widgets.option_list import Option

from myshell_rfd.core.registry import get_registry


class ModuleSelectorScreen(ModalScreen[str | None]):
    """Modal screen for selecting a module.

    Returns the selected module name or None if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
    ]

    CSS = """
    ModuleSelectorScreen {
        align: center middle;
    }

    #selector-container {
        width: 60;
        height: 30;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #selector-title {
        text-style: bold;
        text-align: center;
        padding: 1;
        background: $primary;
    }

    OptionList {
        height: 1fr;
        margin: 1;
    }

    #selector-buttons {
        dock: bottom;
        height: 3;
        align: center middle;
    }
    """

    def __init__(
        self,
        title: str = "Select Module",
        filter_available: bool = True,
        filter_installed: bool = False,
    ) -> None:
        """Initialize the selector.

        Args:
            title: Screen title.
            filter_available: Only show available modules.
            filter_installed: Only show installed modules.
        """
        super().__init__()
        self._title = title
        self._filter_available = filter_available
        self._filter_installed = filter_installed

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        with Container(id="selector-container"):
            yield Label(self._title, id="selector-title")
            yield OptionList(id="module-list")
            with Container(id="selector-buttons"):
                yield Button("Select", variant="primary", id="btn-select")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        """Populate the module list."""
        registry = get_registry()
        option_list = self.query_one("#module-list", OptionList)

        for module in sorted(registry.get_all(), key=lambda m: m.name):
            # Apply filters
            if self._filter_available and not module.check_available():
                continue
            if self._filter_installed and not module.check_installed():
                continue

            status = ""
            if module.check_installed():
                status = " [green](installed)[/green]"
            elif not module.check_available():
                status = " [yellow](missing deps)[/yellow]"

            option_list.add_option(
                Option(f"{module.name}{status}", id=module.name)
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-select":
            self.action_select()
        elif event.button.id == "btn-cancel":
            self.action_cancel()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        self.dismiss(str(event.option.id))

    def action_select(self) -> None:
        """Select the highlighted option."""
        option_list = self.query_one("#module-list", OptionList)
        if option_list.highlighted is not None:
            option = option_list.get_option_at_index(option_list.highlighted)
            self.dismiss(str(option.id))

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss(None)
