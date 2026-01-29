"""Rich-based logging system for MyShell_RFD.

Replaces colors.sh and lecho.sh functionality with modern Rich output.
"""

from enum import Enum
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.style import Style
from rich.text import Text
from rich.theme import Theme


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARN = "warn"
    ERROR = "error"


# Custom theme for MyShell_RFD
MYSHELL_THEME = Theme(
    {
        "info": Style(color="blue"),
        "success": Style(color="green", bold=True),
        "warn": Style(color="yellow"),
        "error": Style(color="red", bold=True),
        "debug": Style(color="magenta", dim=True),
        "header": Style(color="cyan", bold=True),
        "highlight": Style(color="cyan"),
        "muted": Style(dim=True),
        "module.name": Style(color="green"),
        "module.status.installed": Style(color="green"),
        "module.status.missing": Style(color="yellow"),
        "module.status.error": Style(color="red"),
    }
)

# Prefixes for each log level (matching original lecho.sh behavior)
LOG_PREFIXES: dict[LogLevel, tuple[str, str]] = {
    LogLevel.DEBUG: ("[DEBUG]", "debug"),
    LogLevel.INFO: ("[INFO]", "info"),
    LogLevel.SUCCESS: ("[OK]", "success"),
    LogLevel.WARN: ("[WARN]", "warn"),
    LogLevel.ERROR: ("[ERROR]", "error"),
}


class Logger:
    """Centralized logging with Rich formatting.

    Provides colored, formatted output similar to the original Bash
    lecho() function but with Rich enhancements.
    """

    def __init__(
        self,
        *,
        debug_mode: bool = False,
        quiet: bool = False,
        console: Console | None = None,
    ) -> None:
        """Initialize the logger.

        Args:
            debug_mode: Enable debug output.
            quiet: Suppress non-essential output.
            console: Optional Rich console instance.
        """
        self._debug_mode = debug_mode
        self._quiet = quiet
        self._console = console or Console(theme=MYSHELL_THEME)
        self._err_console = Console(theme=MYSHELL_THEME, stderr=True)

    @property
    def console(self) -> Console:
        """Get the Rich console instance."""
        return self._console

    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = enabled

    def set_quiet(self, enabled: bool) -> None:
        """Enable or disable quiet mode."""
        self._quiet = enabled

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Log a message with the specified level.

        Args:
            level: The log level.
            message: The message to log.
            **kwargs: Additional arguments passed to console.print.
        """
        if level == LogLevel.DEBUG and not self._debug_mode:
            return

        if self._quiet and level == LogLevel.INFO:
            return

        prefix, style = LOG_PREFIXES[level]
        text = Text()
        text.append(f"{prefix} ", style=style)
        text.append(message)

        console = self._err_console if level == LogLevel.ERROR else self._console
        console.print(text, **kwargs)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.log(LogLevel.INFO, message)

    def success(self, message: str) -> None:
        """Log a success message."""
        self.log(LogLevel.SUCCESS, message)

    def warn(self, message: str) -> None:
        """Log a warning message."""
        self.log(LogLevel.WARN, message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log(LogLevel.ERROR, message)

    def header(self, title: str, *, subtitle: str | None = None) -> None:
        """Print a section header.

        Replaces print_header() from ui.sh.

        Args:
            title: The header title.
            subtitle: Optional subtitle.
        """
        content = Text(title, style="header")
        if subtitle:
            content.append(f"\n{subtitle}", style="muted")

        panel = Panel(
            content,
            border_style="cyan",
            padding=(0, 2),
        )
        self._console.print(panel)

    def footer(self, message: str = "Execution Complete") -> None:
        """Print a footer message.

        Args:
            message: The footer message.
        """
        self.header(message)

    def rule(self, title: str = "") -> None:
        """Print a horizontal rule.

        Args:
            title: Optional title in the middle of the rule.
        """
        self._console.rule(title, style="cyan")

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to the console with Rich formatting.

        Args:
            *args: Positional arguments passed to console.print.
            **kwargs: Keyword arguments passed to console.print.
        """
        self._console.print(*args, **kwargs)

    def progress(
        self,
        *,
        transient: bool = True,
    ) -> Progress:
        """Create a progress bar context manager.

        Args:
            transient: If True, remove progress bar after completion.

        Returns:
            A Rich Progress instance.
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self._console,
            transient=transient,
        )

    def status(self, message: str) -> Any:
        """Create a status spinner context manager.

        Args:
            message: The status message.

        Returns:
            A Rich Status instance.
        """
        return self._console.status(message, spinner="dots")


# Global logger instance
_logger: Logger | None = None


def get_logger() -> Logger:
    """Get the global logger instance.

    Returns:
        The global Logger instance.
    """
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger


def set_logger(logger: Logger) -> None:
    """Set the global logger instance.

    Args:
        logger: The Logger instance to use globally.
    """
    global _logger
    _logger = logger
