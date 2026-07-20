"""
`ai history` and `ai clear-history` — inspect and manage saved sessions.
"""

from __future__ import annotations

from rich.table import Table

from history.history_manager import HistoryManager
from utils.console import console, print_success, print_warning


def show_history(history_manager: HistoryManager, session_id: str | None = None) -> None:
    if session_id:
        session = history_manager.load(session_id)
        if session is None:
            print_warning(f"No session found with id '{session_id}'.")
            return
        console.print(f"[bold]Session {session.session_id}[/bold] (model: {session.model})")
        console.print(f"[muted]Created {session.created_at} — updated {session.updated_at}[/muted]\n")
        for msg in session.messages:
            if msg["role"] == "system":
                continue
            role_style = "user" if msg["role"] == "user" else "assistant"
            console.print(f"[{role_style}]{msg['role']} ›[/{role_style}] {msg['content']}\n")
        return

    sessions = history_manager.list_sessions()
    if not sessions:
        console.print("[muted]No saved conversations yet. Start one with `ai chat`.[/muted]")
        return

    table = Table(title="Conversation history")
    table.add_column("Session ID", style="bold cyan")
    table.add_column("Model")
    table.add_column("Messages")
    table.add_column("Last updated")

    for s in sessions:
        turn_count = sum(1 for m in s.messages if m["role"] != "system")
        table.add_row(s.session_id, s.model, str(turn_count), s.updated_at)

    console.print(table)
    console.print("\n[muted]View one: `ai history <session_id>`   Resume it: `ai chat --resume <session_id>`[/muted]")


def clear_history(history_manager: HistoryManager, confirm: bool) -> None:
    if not confirm:
        answer = console.input(r"Delete all saved conversation history? \[y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            console.print("[muted]Cancelled.[/muted]")
            return
    count = history_manager.clear_all()
    print_success(f"Deleted {count} saved session(s).")
