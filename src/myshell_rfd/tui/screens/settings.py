"""Settings screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from myshell_rfd.core.config import get_config, save_config


class SettingsScreen(Screen[None]):
    """Settings and profile management screen."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "save", "Save"),
    ]

    CSS = """
    SettingsScreen {
        background: $surface;
    }

    #settings-container {
        padding: 2;
    }

    .settings-section {
        margin-bottom: 2;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .setting-row {
        height: 3;
        margin-bottom: 1;
    }

    .setting-label {
        width: 20;
    }

    Input {
        width: 40;
    }

    #profiles-list {
        height: 10;
        margin: 1;
    }

    #settings-buttons {
        dock: bottom;
        height: 3;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the settings screen."""
        with Container(id="settings-container"):
            # General settings
            with Vertical(classes="settings-section"):
                yield Label("General Settings", classes="section-title")

                with Horizontal(classes="setting-row"):
                    yield Label("Debug mode:", classes="setting-label")
                    yield Checkbox("Enable debug logging", id="chk-debug")

                with Horizontal(classes="setting-row"):
                    yield Label("Offline mode:", classes="setting-label")
                    yield Checkbox("Use cached resources only", id="chk-offline")

            # Profile management
            with Vertical(classes="settings-section"):
                yield Label("Profiles", classes="section-title")
                yield OptionList(id="profiles-list")

                with Horizontal():
                    yield Button("New Profile", id="btn-new-profile", variant="primary")
                    yield Button("Delete", id="btn-delete-profile", variant="error")
                    yield Button("Switch", id="btn-switch-profile", variant="default")

            # Action buttons
            with Horizontal(id="settings-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Back", id="btn-back", variant="default")

    def on_mount(self) -> None:
        """Load current settings."""
        config = get_config()

        # Set checkbox values
        self.query_one("#chk-debug", Checkbox).value = config.debug
        self.query_one("#chk-offline", Checkbox).value = config.offline_mode

        # Populate profiles
        self._refresh_profiles()

    def _refresh_profiles(self) -> None:
        """Refresh the profiles list."""
        config = get_config()
        profiles_list = self.query_one("#profiles-list", OptionList)
        profiles_list.clear_options()

        for name in sorted(config.profiles.keys()):
            active = " [green](active)[/green]" if name == config.active_profile else ""
            profiles_list.add_option(Option(f"{name}{active}", id=name))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-save":
            self.action_save()
        elif button_id == "btn-back":
            self.action_back()
        elif button_id == "btn-new-profile":
            self._create_profile()
        elif button_id == "btn-delete-profile":
            self._delete_profile()
        elif button_id == "btn-switch-profile":
            self._switch_profile()

    def action_save(self) -> None:
        """Save settings."""
        config = get_config()

        config.debug = self.query_one("#chk-debug", Checkbox).value
        config.offline_mode = self.query_one("#chk-offline", Checkbox).value

        save_config()
        self.notify("Settings saved", title="Success")

    def action_back(self) -> None:
        """Go back to main screen."""
        self.app.pop_screen()

    def _create_profile(self) -> None:
        """Create a new profile."""
        from myshell_rfd.tui.screens.input import InputScreen

        def on_input(name: str | None) -> None:
            if name:
                config = get_config()
                try:
                    config.create_profile(name)
                    save_config()
                    self._refresh_profiles()
                    self.notify(f"Created profile: {name}", title="Success")
                except ValueError as e:
                    self.notify(str(e), title="Error", severity="error")

        self.app.push_screen(
            InputScreen("New Profile", "Enter profile name:"),
            on_input,
        )

    def _delete_profile(self) -> None:
        """Delete selected profile."""
        profiles_list = self.query_one("#profiles-list", OptionList)

        if profiles_list.highlighted is None:
            return

        option = profiles_list.get_option_at_index(profiles_list.highlighted)
        name = str(option.id)

        config = get_config()
        try:
            if config.delete_profile(name):
                save_config()
                self._refresh_profiles()
                self.notify(f"Deleted profile: {name}", title="Success")
        except ValueError as e:
            self.notify(str(e), title="Error", severity="error")

    def _switch_profile(self) -> None:
        """Switch to selected profile."""
        profiles_list = self.query_one("#profiles-list", OptionList)

        if profiles_list.highlighted is None:
            return

        option = profiles_list.get_option_at_index(profiles_list.highlighted)
        name = str(option.id)

        config = get_config()
        try:
            config.switch_profile(name)
            save_config()
            self._refresh_profiles()
            self.notify(f"Switched to profile: {name}", title="Success")
        except ValueError as e:
            self.notify(str(e), title="Error", severity="error")
