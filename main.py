"""
terminal-ai — a lightweight, modular, terminal-based AI coding assistant.

Entry point. Run `python main.py --help` (or `ai --help` once installed)
to see all available commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from commands import config_cmd, history_cmd, models_cmd
from commands.chat import run_chat
from config.config_manager import get_config_manager
from history.history_manager import HistoryManager
from utils.console import console, print_info

app = typer.Typer(
    name="ai",
    help="A lightweight, modular, terminal-based AI coding assistant.",
    no_args_is_help=True,
    add_completion=True,
)

PHASE_2_NOTICE = (
    "'{cmd}' is planned for a later phase of this project "
    "(project analysis / codegen / agent capabilities). "
    "Phase 1 currently covers: chat, config, models, switch-model, history, clear-history."
)


def _not_yet_implemented(cmd: str) -> None:
    print_info(PHASE_2_NOTICE.format(cmd=cmd))


@app.command()
def chat(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the default model for this session."),
    resume: Optional[str] = typer.Option(None, "--resume", "-r", help="Resume a saved session by id."),
) -> None:
    """Start an interactive multi-turn chat session."""
    config_manager = get_config_manager()
    history_manager = HistoryManager()
    run_chat(config_manager, history_manager, model_override=model, resume_session_id=resume)


@app.command()
def explain(
    file: Path = typer.Argument(..., help="File to explain."),
    beginner: bool = typer.Option(False, "--beginner", help="Give a beginner-friendly explanation."),
) -> None:
    """Explain the code in a given file."""
    _not_yet_implemented("ai explain")


@app.command()
def review(
    path: Path = typer.Argument(Path("."), help="Directory to review."),
) -> None:
    """Recursively review a project for quality, bugs, security, and performance issues."""
    _not_yet_implemented("ai review")


@app.command()
def fix(
    path: Path = typer.Argument(Path("."), help="Directory to analyze and fix."),
) -> None:
    """Analyze a project and apply confirmed fixes."""
    _not_yet_implemented("ai fix")


@app.command(name="generate-readme")
def generate_readme() -> None:
    """Generate a README.md for the current project."""
    _not_yet_implemented("ai generate-readme")


@app.command()
def commit() -> None:
    """Generate a commit message from the current git diff."""
    _not_yet_implemented("ai commit")


@app.command()
def agent(
    task: str = typer.Argument(..., help="Natural-language description of the task."),
) -> None:
    """Break a task into steps and execute them (create/modify files, generate code)."""
    _not_yet_implemented("ai agent")


@app.command()
def models() -> None:
    """List available models, providers, context length, and status."""
    config_manager = get_config_manager()
    models_cmd.list_models(config_manager)


@app.command(name="switch-model")
def switch_model(
    model: Optional[str] = typer.Argument(None, help="Model name to switch to directly (skips the interactive picker)."),
) -> None:
    """Interactively switch the default model."""
    config_manager = get_config_manager()
    if model:
        models_cmd.switch_model_direct(config_manager, model)
    else:
        models_cmd.switch_model_interactive(config_manager)


@app.command()
def history(
    session_id: Optional[str] = typer.Argument(None, help="View a specific session by id."),
) -> None:
    """List saved conversations, or view one in full by id."""
    history_manager = HistoryManager()
    history_cmd.show_history(history_manager, session_id=session_id)


@app.command(name="clear-history")
def clear_history(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt."),
) -> None:
    """Delete all saved conversation history."""
    history_manager = HistoryManager()
    history_cmd.clear_history(history_manager, confirm=yes)


@app.command()
def config(
    set_: Optional[str] = typer.Option(
        None, "--set", help="Set a single value non-interactively, e.g. --set temperature=0.5"
    ),
) -> None:
    """View or edit configuration (API key, base URL, model, temperature, etc.)."""
    config_manager = get_config_manager()
    if set_:
        if "=" not in set_:
            console.print("[danger]Expected --set key=value, e.g. --set temperature=0.5[/danger]")
            raise typer.Exit(code=1)
        key, _, value = set_.partition("=")
        try:
            config_cmd.set_config_value(config_manager, key.strip(), value.strip())
        except (KeyError, ValueError) as exc:
            console.print(f"[danger]{exc}[/danger]")
            raise typer.Exit(code=1) from exc
        return

    config_cmd.show_config(config_manager)
    if typer.confirm("Edit configuration now?", default=False):
        config_cmd.edit_config_interactive(config_manager)


@app.command(name="help")
def help_command() -> None:
    """Show help for all commands."""
    import subprocess
    import sys

    subprocess.run([sys.executable, __file__, "--help"], check=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
