"""
`ai config` — view or interactively edit configuration values.
"""

from __future__ import annotations

from rich.table import Table

from config.config_manager import ConfigManager
from utils.console import console, print_success


FIELD_PROMPTS: list[tuple[str, str, type]] = [
    ("api_key", "API key (leave blank to keep current)", str),
    ("base_url", "Base URL", str),
    ("default_model", "Default model", str),
    ("temperature", "Temperature (0.0 - 2.0)", float),
    ("max_tokens", "Max tokens", int),
    ("stream", "Stream responses? (true/false)", bool),
    ("theme", "Theme", str),
]


def show_config(config_manager: ConfigManager) -> None:
    cfg = config_manager.get()
    table = Table(title="terminal-ai configuration", show_lines=False)
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value")

    masked_key = "•" * 8 + cfg.api_key[-4:] if cfg.api_key else "[muted](not set)[/muted]"
    table.add_row("API key", masked_key)
    table.add_row("Base URL", cfg.base_url)
    table.add_row("Default model", cfg.default_model)
    table.add_row("Temperature", str(cfg.temperature))
    table.add_row("Max tokens", str(cfg.max_tokens))
    table.add_row("Streaming", str(cfg.stream))
    table.add_row("Theme", cfg.theme)
    table.add_row("Config file", str(config_manager.config_path))

    console.print(table)


def edit_config_interactive(config_manager: ConfigManager) -> None:
    cfg = config_manager.get()
    console.print("[muted]Press Enter to keep the current value.[/muted]\n")

    updates: dict[str, object] = {}
    for field_name, prompt, field_type in FIELD_PROMPTS:
        current = getattr(cfg, field_name)
        display_current = "•" * 8 if field_name == "api_key" and current else current
        raw = console.input(f"{prompt} [muted]({display_current})[/muted]: ").strip()
        if not raw:
            continue
        if field_type is bool:
            updates[field_name] = raw.lower() in {"1", "true", "yes", "y", "on"}
        elif field_type is float:
            updates[field_name] = float(raw)
        elif field_type is int:
            updates[field_name] = int(raw)
        else:
            updates[field_name] = raw

    if updates:
        config_manager.update(**updates)
        print_success("Configuration updated.")
    else:
        console.print("[muted]No changes made.[/muted]")

    show_config(config_manager)


def set_config_value(config_manager: ConfigManager, key: str, value: str) -> None:
    """Non-interactive single-field update, e.g. `ai config --set temperature=0.5`."""
    cfg = config_manager.get()
    if not hasattr(cfg, key):
        raise KeyError(f"Unknown config key '{key}'.")

    current = getattr(cfg, key)
    if isinstance(current, bool):
        parsed: object = value.lower() in {"1", "true", "yes", "y", "on"}
    elif isinstance(current, int):
        parsed = int(value)
    elif isinstance(current, float):
        parsed = float(value)
    else:
        parsed = value

    config_manager.update(**{key: parsed})
    print_success(f"Set {key} = {parsed}")
