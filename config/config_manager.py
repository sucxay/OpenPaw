"""
Configuration management for the terminal AI assistant.

Configuration is stored as JSON in the user's home directory
(``~/.terminal-ai/config.json``) and can be overridden by environment
variables. Values resolve in this order, highest priority first:

    1. Environment variables (e.g. ``TERMINAL_AI_API_KEY``)
    2. Values stored in the config file
    3. Built-in defaults
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


CONFIG_DIR = Path(os.environ.get("TERMINAL_AI_HOME", Path.home() / ".terminal-ai"))
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_PREFIX = "TERMINAL_AI_"

DEFAULT_BASE_URL = "http://localhost:3001/v1"
DEFAULT_MODEL = "gpt-3.5-turbo"


@dataclass
class AppConfig:
    """Typed representation of everything the assistant needs to run."""

    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    default_model: str = DEFAULT_MODEL
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = True
    theme: str = "default"
    # Models the user has previously seen/used, so `ai switch-model` has
    # something to offer even if `ai models` hasn't been run yet.
    known_models: list[str] = field(default_factory=lambda: [DEFAULT_MODEL])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


class ConfigManager:
    """Loads, saves, and resolves configuration values."""

    def __init__(self, config_path: Path = CONFIG_FILE) -> None:
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load()

    def _load(self) -> AppConfig:
        if self.config_path.exists():
            try:
                raw = json.loads(self.config_path.read_text(encoding="utf-8"))
                cfg = AppConfig.from_dict(raw)
            except (json.JSONDecodeError, TypeError, ValueError):
                cfg = AppConfig()
        else:
            cfg = AppConfig()
        return self._apply_env_overrides(cfg)

    @staticmethod
    def _apply_env_overrides(cfg: AppConfig) -> AppConfig:
        env_map = {
            "API_KEY": "api_key",
            "BASE_URL": "base_url",
            "DEFAULT_MODEL": "default_model",
            "TEMPERATURE": "temperature",
            "MAX_TOKENS": "max_tokens",
            "STREAM": "stream",
            "THEME": "theme",
        }
        for env_suffix, field_name in env_map.items():
            env_var = f"{ENV_PREFIX}{env_suffix}"
            if env_var in os.environ:
                raw_value = os.environ[env_var]
                current = getattr(cfg, field_name)
                if isinstance(current, bool):
                    value: Any = raw_value.strip().lower() in {"1", "true", "yes", "on"}
                elif isinstance(current, int):
                    value = int(raw_value)
                elif isinstance(current, float):
                    value = float(raw_value)
                else:
                    value = raw_value
                setattr(cfg, field_name, value)
        return cfg

    def save(self) -> None:
        self.config_path.write_text(
            json.dumps(self._config.to_dict(), indent=2), encoding="utf-8"
        )

    def get(self) -> AppConfig:
        return self._config

    def update(self, **kwargs: Any) -> AppConfig:
        for key, value in kwargs.items():
            if value is None:
                continue
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save()
        return self._config

    def remember_model(self, model_name: str) -> None:
        """Track a model name so it shows up in `ai switch-model` later."""
        if model_name and model_name not in self._config.known_models:
            self._config.known_models.append(model_name)
            self.save()


def get_config_manager() -> ConfigManager:
    """Convenience factory used by CLI commands."""
    return ConfigManager()
