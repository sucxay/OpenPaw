import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import APIConnectionError

from config.config_manager import AppConfig
from utils.api_client import APIClientError, LLMClient


class _FakeCompletions:
    def __init__(self, response=None, chunks=None, raise_error=None):
        self._response = response
        self._chunks = chunks or []
        self._raise_error = raise_error

    def create(self, **kwargs):
        if self._raise_error:
            raise self._raise_error
        if kwargs.get("stream"):
            return iter(self._chunks)
        return self._response


def _make_client(monkeypatch, completions):
    cfg = AppConfig(api_key="x", base_url="http://fake", default_model="fake-model")
    client = LLMClient(cfg)
    client._client.chat.completions = completions  # type: ignore[attr-defined]
    return client


def test_chat_returns_message_content(monkeypatch):
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="hello there"))]
    )
    client = _make_client(monkeypatch, _FakeCompletions(response=fake_response))
    result = client.chat([{"role": "user", "content": "hi"}])
    assert result == "hello there"


def test_stream_chat_yields_text_chunks(monkeypatch):
    chunks = [
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Hel"))]),
        SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="lo"))]),
        SimpleNamespace(choices=[]),  # some servers send an empty terminal chunk
    ]
    client = _make_client(monkeypatch, _FakeCompletions(chunks=chunks))
    result = "".join(client.stream_chat([{"role": "user", "content": "hi"}]))
    assert result == "Hello"


def test_connection_error_raises_friendly_api_client_error(monkeypatch):
    err = APIConnectionError(request=SimpleNamespace())
    client = _make_client(monkeypatch, _FakeCompletions(raise_error=err))
    try:
        client.chat([{"role": "user", "content": "hi"}])
        assert False, "expected APIClientError"
    except APIClientError as exc:
        assert "localhost" in str(exc) or "http://fake" in str(exc)
        assert "base URL" in str(exc) or "backend" in str(exc)
