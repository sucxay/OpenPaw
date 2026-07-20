"""
`ai models` and `ai switch-model` — list and switch the active model.
"""

from __future__ import annotations

from rich.table import Table

from config.config_manager import ConfigManager
from utils.api_client import APIClientError, LLMClient
from utils.console import console, print_error, print_success, print_warning


def list_models(config_manager: ConfigManager) -> None:
    cfg = config_manager.get()
    client = LLMClient(cfg)

    table = Table(title="Available models")
    table.add_column("Model", style="bold cyan")
    table.add_column("Provider")
    table.add_column("Context length")
    table.add_column("Status")

    try:
        models = client.list_models()
    except APIClientError as exc:
        print_warning(f"Could not fetch models from the server: {exc}")
        models = []

    if not models:
        # Fall back to whatever models we've seen used before, so the
        # command is still useful if the backend doesn't implement /models.
        for m in cfg.known_models:
            table.add_row(m, "unknown", "—", "unverified")
    else:
        for m in models:
            active = " (active)" if m.id == cfg.default_model else ""
            table.add_row(
                f"{m.id}{active}",
                m.owned_by,
                str(m.context_length) if m.context_length else "—",
                m.status,
            )

    console.print(table)


def switch_model_interactive(config_manager: ConfigManager) -> None:
    cfg = config_manager.get()
    client = LLMClient(cfg)

    try:
        models = client.list_models()
        choices = [m.id for m in models] or list(cfg.known_models)
    except APIClientError as exc:
        print_warning(f"Could not fetch models from the server: {exc}")
        choices = list(cfg.known_models)

    if not choices:
        print_error("No known models to choose from. Try `ai models` first, or pass a model name directly.")
        return

    console.print("[muted]Available models:[/muted]")
    for i, m in enumerate(choices, start=1):
        marker = " [success](current)[/success]" if m == cfg.default_model else ""
        console.print(f"  {i}. {m}{marker}")

    raw = console.input("\nSelect a model by number or type a model name: ").strip()
    if not raw:
        console.print("[muted]No change made.[/muted]")
        return

    if raw.isdigit() and 1 <= int(raw) <= len(choices):
        selected = choices[int(raw) - 1]
    else:
        selected = raw

    config_manager.update(default_model=selected)
    config_manager.remember_model(selected)
    print_success(f"Default model switched to '{selected}'.")


def switch_model_direct(config_manager: ConfigManager, model_name: str) -> None:
    config_manager.update(default_model=model_name)
    config_manager.remember_model(model_name)
    print_success(f"Default model switched to '{model_name}'.")
