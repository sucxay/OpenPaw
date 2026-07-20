import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from config.config_manager import AppConfig, ConfigManager, DEFAULT_BASE_URL


@pytest.fixture
def tmp_config_path(tmp_path):
    return tmp_path / "config.json"


def test_defaults_when_no_file(tmp_config_path):
    mgr = ConfigManager(config_path=tmp_config_path)
    cfg = mgr.get()
    assert cfg.base_url == DEFAULT_BASE_URL
    assert cfg.stream is True
    assert cfg.temperature == 0.7


def test_save_and_reload_round_trip(tmp_config_path):
    mgr = ConfigManager(config_path=tmp_config_path)
    mgr.update(default_model="test-model", temperature=0.2)

    mgr2 = ConfigManager(config_path=tmp_config_path)
    cfg2 = mgr2.get()
    assert cfg2.default_model == "test-model"
    assert cfg2.temperature == 0.2


def test_update_ignores_unknown_and_none(tmp_config_path):
    mgr = ConfigManager(config_path=tmp_config_path)
    before = mgr.get().default_model
    mgr.update(default_model=None, nonexistent_field="x")
    assert mgr.get().default_model == before


def test_env_override_takes_precedence(tmp_config_path, monkeypatch):
    monkeypatch.setenv("TERMINAL_AI_DEFAULT_MODEL", "env-model")
    mgr = ConfigManager(config_path=tmp_config_path)
    assert mgr.get().default_model == "env-model"


def test_remember_model_deduplicates(tmp_config_path):
    mgr = ConfigManager(config_path=tmp_config_path)
    mgr.remember_model("model-a")
    mgr.remember_model("model-a")
    mgr.remember_model("model-b")
    assert mgr.get().known_models.count("model-a") == 1
    assert "model-b" in mgr.get().known_models


def test_corrupt_config_file_falls_back_to_defaults(tmp_config_path):
    tmp_config_path.write_text("{not valid json", encoding="utf-8")
    mgr = ConfigManager(config_path=tmp_config_path)
    assert mgr.get().base_url == DEFAULT_BASE_URL
