"""
`ai chat` — interactive multi-turn chat with streaming responses.
"""

from __future__ import annotations

from rich.live import Live
from rich.markdown import Markdown

from config.config_manager import ConfigManager
from history.history_manager import HistoryManager, Session
from utils.api_client import APIClientError, LLMClient
from utils.console import console, print_error, print_info, print_warning

EXIT_COMMANDS = {"exit", "quit", ":q", ":wq"}
SYSTEM_PROMPT = (
    "You are a helpful, precise AI coding assistant running in a terminal. "
    "Format code in fenced Markdown code blocks with a language tag."
)


def run_chat(
    config_manager: ConfigManager,
    history_manager: HistoryManager,
    model_override: str | None = None,
    resume_session_id: str | None = None,
) -> None:
    cfg = config_manager.get()
    client = LLMClient(cfg)
    model = model_override or cfg.default_model

    if resume_session_id:
        session = history_manager.load(resume_session_id)
        if session is None:
            print_error(f"No saved session found with id '{resume_session_id}'.")
            return
        print_info(f"Resumed session {session.session_id} ({len(session.messages)} messages).")
    else:
        session = history_manager.new_session(model=model)
        session.messages.append({"role": "system", "content": SYSTEM_PROMPT})

    console.print(
        f"[muted]Chatting with model '[bold]{model}[/bold]'. "
        f"Type 'exit' or 'quit' to leave. Session id: {session.session_id}[/muted]\n"
    )

    while True:
        try:
            user_input = console.input("[user]you ›[/user] ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        stripped = user_input.strip()
        if not stripped:
            continue
        if stripped.lower() in EXIT_COMMANDS:
            break

        session.messages.append({"role": "user", "content": stripped})

        console.print("[assistant]assistant ›[/assistant] ", end="")
        full_reply = ""
        try:
            if cfg.stream:
                full_reply = _stream_and_render(client, session.messages, model)
            else:
                full_reply = client.chat(session.messages, model=model)
                console.print(Markdown(full_reply))
        except APIClientError as exc:
            print_error(str(exc))
            session.messages.pop()  # drop the unanswered user turn
            continue

        session.messages.append({"role": "assistant", "content": full_reply})
        history_manager.save(session)

    history_manager.save(session)
    print_info(f"Session saved as '{session.session_id}'. Resume with: ai chat --resume {session.session_id}")


def _stream_and_render(client: LLMClient, messages: list[dict[str, str]], model: str) -> str:
    """Stream tokens live, re-rendering as Markdown for syntax highlighting."""
    full_text = ""
    with Live(console=console, refresh_per_second=12, transient=False) as live:
        try:
            for chunk in client.stream_chat(messages, model=model):
                full_text += chunk
                live.update(Markdown(full_text))
        except APIClientError:
            if full_text:
                print_warning("Stream interrupted; showing partial response.")
            raise
    return full_text
