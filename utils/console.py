"""
Shared Rich console and small formatting helpers used across commands.
"""
from __future__ import annotations

from collections.abc import Iterable

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from utils.api_client import APIClientError


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


def render_markdown_stream(chunks: Iterable[str]) -> str:
    """Live-render a stream of text chunks as Markdown, returning the full text.

    Shared by any command that streams an LLM response to the terminal
    (`ai chat`, `ai explain`, ...). Text accumulates and is re-rendered as
    Markdown on every chunk so code blocks get syntax highlighting once
    complete. If the underlying stream raises an `APIClientError` partway
    through, whatever was rendered so far stays on screen, a warning is
    printed, and the error is re-raised for the caller to handle.

    Args:
        chunks: An iterable (typically a generator from
            `LLMClient.stream_chat`) yielding response text chunks.

    Returns:
        The full accumulated response text.
    """
    full_text = ""
    with Live(console=console, refresh_per_second=12, transient=False) as live:
        try:
            for chunk in chunks:
                full_text += chunk
                live.update(Markdown(full_text))
        except APIClientError:
            if full_text:
                print_warning("Stream interrupted; showing partial response.")
            raise
    return full_text