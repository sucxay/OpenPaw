"""
Shared Rich console and small formatting helpers used across commands.
"""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "danger": "bold red",
        "muted": "grey58",
        "user": "bold blue",
        "assistant": "bold magenta",
    }
)

console = Console(theme=_theme)
error_console = Console(theme=_theme, stderr=True)


def print_error(message: str) -> None:
    error_console.print(f"[danger]✖ {message}[/danger]")


def print_success(message: str) -> None:
    console.print(f"[success]✔ {message}[/success]")


def print_info(message: str) -> None:
    console.print(f"[info]ℹ {message}[/info]")


def print_warning(message: str) -> None:
    console.print(f"[warning]⚠ {message}[/warning]")


def print_markdown(text: str) -> None:
    console.print(Markdown(text))


def print_panel(text: str, title: str = "", style: str = "info") -> None:
    console.print(Panel(text, title=title, border_style=style))
