"""Main screen for MyShell_RFD TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DataTable, Label, OptionList
from textual.widgets.option_list import Option

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
                yield OptionList(id="categories-list")

            # Main content
            with Vertical(id="content"):
                yield Label("Modules", classes="category-header")
                yield DataTable(id="modules-table")

    def on_mount(self) -> None:
        """Initialize the screen."""
        self._registry = init_registry()
        self._current_category: str | None = None

        # Setup categories list
        categories_list = self.query_one("#categories-list", OptionList)
        categories_list.add_option(Option("All Modules", id="all"))
        categories_list.add_option(Option("Shell", id="shell"))
        categories_list.add_option(Option("Containers", id="container"))
        categories_list.add_option(Option("Kubernetes", id="kubernetes"))
        categories_list.add_option(Option("Cloud", id="cloud"))
        categories_list.add_option(Option("VCS", id="vcs"))
        categories_list.add_option(Option("Tools", id="tools"))
        categories_list.add_option(Option("Themes", id="theme"))
        # Select "All Modules" by default
        categories_list.highlighted = 0

        # Setup table
        table = self.query_one("#modules-table", DataTable)
        table.add_columns("Name", "Category", "Description", "Status")
        table.cursor_type = "row"

        self.refresh_modules()

        # Set focus on the modules table by default
        table.focus()

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

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle category selection."""
        category_id = str(event.option.id)
        if category_id == "all":
            self.refresh_modules()
        else:
            self.refresh_modules(category_id)

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
