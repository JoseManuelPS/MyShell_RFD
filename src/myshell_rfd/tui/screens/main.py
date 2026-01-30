"""Main screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Label

from myshell_rfd.core.registry import init_registry


class MainScreen(Container):
    """Main dashboard container.

    Shows module overview and quick actions.
    """

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        with Container(id="main-container"):
            # Sidebar with categories
            with Vertical(id="sidebar"):
                yield Label("Categories", classes="category-header")
                yield Button("All Modules", id="cat-all", classes="primary")
                yield Button("Shell", id="cat-shell")
                yield Button("Containers", id="cat-container")
                yield Button("Kubernetes", id="cat-kubernetes")
                yield Button("Cloud", id="cat-cloud")
                yield Button("VCS", id="cat-vcs")
                yield Button("Tools", id="cat-tools")
                yield Button("Themes", id="cat-theme")

            # Main content
            with Vertical(id="content"):
                yield Label("Modules", classes="category-header")
                yield DataTable(id="modules-table")

                # Action buttons
                with Horizontal(classes="button-bar"):
                    yield Button("Install Selected", id="btn-install", variant="success")
                    yield Button("Uninstall", id="btn-uninstall", variant="warning")
                    yield Button("Clean All", id="btn-clean", variant="error")

    def on_mount(self) -> None:
        """Initialize the screen."""
        self._registry = init_registry()
        self._current_category: str | None = None

        # Setup table
        table = self.query_one("#modules-table", DataTable)
        table.add_columns("Name", "Category", "Description", "Status")
        table.cursor_type = "row"

        self.refresh_modules()

    def refresh_modules(self, category: str | None = None) -> None:
        """Refresh the modules table.

        Args:
            category: Optional category filter.
        """
        self._current_category = category

        table = self.query_one("#modules-table", DataTable)
        table.clear()

        for module in sorted(self._registry.get_all(), key=lambda m: m.name):
            # Filter by category
            if category and module.category.value != category:
                continue

            # Determine status
            if module.check_installed():
                status = "[green]Installed[/green]"
            elif module.check_available():
                status = "[blue]Available[/blue]"
            else:
                status = "[yellow]Missing deps[/yellow]"

            table.add_row(
                module.name,
                module.category.value,
                module.info.description[:40] + "..." if len(module.info.description) > 40 else module.info.description,
                status,
                key=module.name,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-install":
            self.action_install()
        elif button_id == "btn-uninstall":
            self.action_uninstall()
        elif button_id == "btn-clean":
            self.action_clean()
        elif button_id and button_id.startswith("cat-"):
            category = button_id[4:]
            if category == "all":
                self.refresh_modules()
            else:
                self.refresh_modules(category)

    def action_install(self) -> None:
        """Install selected module."""
        table = self.query_one("#modules-table", DataTable)

        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                module_name = str(row_key[0])
                self._install_module(module_name)

    def action_uninstall(self) -> None:
        """Uninstall selected module."""
        table = self.query_one("#modules-table", DataTable)

        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            if row_key:
                module_name = str(row_key[0])
                self._uninstall_module(module_name)

    def action_clean(self) -> None:
        """Clean all configuration."""
        from myshell_rfd.tui.screens.confirm import ConfirmScreen

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                from myshell_rfd.core.installer import get_installer

                installer = get_installer()
                installer.clean_config()
                self.refresh_modules()
                self.notify("Configuration cleaned", title="Clean")

        self.app.push_screen(
            ConfirmScreen(
                "Clean Configuration",
                "This will remove all MyShell_RFD configuration from your .zshrc. Continue?",
            ),
            on_confirm,
        )

    def action_profiles(self) -> None:
        """Show profiles screen."""
        from myshell_rfd.tui.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_settings(self) -> None:
        """Show settings screen."""
        from myshell_rfd.tui.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def _install_module(self, name: str) -> None:
        """Install a module by name."""
        from myshell_rfd.core.config import ModuleConfig
        from myshell_rfd.core.installer import get_installer

        installer = get_installer()
        result = installer.install_module(name)

        if result.success:
            self.notify(f"Installed {name}", title="Success", severity="information")
        else:
            self.notify(f"Failed: {result.message}", title="Error", severity="error")

        self.refresh_modules(self._current_category)

    def _uninstall_module(self, name: str) -> None:
        """Uninstall a module by name."""
        from myshell_rfd.core.installer import get_installer

        installer = get_installer()
        result = installer.uninstall_module(name)

        if result.success:
            self.notify(f"Uninstalled {name}", title="Success", severity="information")
        else:
            self.notify(f"Failed: {result.message}", title="Error", severity="error")

        self.refresh_modules(self._current_category)
