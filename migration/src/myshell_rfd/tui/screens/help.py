"""Help screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown

from myshell_rfd import __version__

HELP_TEXT = f"""
# MyShell_RFD v{__version__}

Professional ZSH configuration tool.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `?` | Show this help |
| `d` | Toggle dark/light theme |
| `r` | Refresh current view |
| `i` | Install selected module |
| `u` | Uninstall selected module |
| `a` | Auto-detect and configure |
| `c` | Clean all configuration |
| `p` | Manage profiles |
| `s` | Open settings |
| `↑/↓` | Navigate list |
| `Enter` | Select item |
| `Esc` | Go back / Cancel |

## Features

- **22+ Modules**: AWS, Kubectl, Docker, Terraform, and more
- **Profiles**: Save different configurations for work/personal use
- **Rollback**: Safely revert changes with snapshots
- **Auto-detect**: Automatically configure detected tools
- **Offline mode**: Use cached resources

## Getting Started

1. Use arrow keys to navigate the module list
2. Press `i` to install the selected module
3. Press `a` to auto-detect and configure all available tools

## Configuration

Configuration is stored in `~/.myshell_rfd/config.toml`

Backups are stored in `~/.myshell_rfd/backups/`

---

Press `Esc` or click Close to return.
"""


class HelpScreen(ModalScreen[None]):
    """Help and documentation screen."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-container {
        width: 80;
        height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    #help-scroll {
        height: 1fr;
    }

    Markdown {
        margin: 1;
    }

    #help-close {
        dock: bottom;
        width: 100%;
        height: 3;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Container(id="help-container"):
            with VerticalScroll(id="help-scroll"):
                yield Markdown(HELP_TEXT)
            with Container(id="help-close"):
                yield Button("Close", variant="primary", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle close button."""
        self.dismiss()

    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss()
