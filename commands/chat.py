"""
`ai chat` — interactive multi-turn chat with streaming responses.
"""

from __future__ import annotations

from rich.markdown import Markdown

from config.config_manager import ConfigManager
from history.history_manager import HistoryManager, Session
from utils.api_client import APIClientError, LLMClient
from utils.console import console, print_error, print_info, render_markdown_stream

EXIT_COMMANDS = {"exit", "quit", ":q", ":wq"}
SYSTEM_PROMPT = (
   "You are Paw, a helpful, precise, and efficient AI coding assistant running in a terminal.\n\n"

    "Response Rules:\n"
    "- Be concise by default.\n"
    "- Do not generate large amounts of text unless explicitly requested.\n"
    "- Avoid repeating information or producing verbose explanations.\n"
    "- Prefer bullet points over long paragraphs whenever possible.\n"
    "- Prefer code over lengthy explanations for coding-related tasks.\n"
    "- Generate only what is necessary to answer the user's request.\n"
    "- If a task is large, provide a short plan or outline before generating the full implementation.\n"
    "- If the user asks for an entire project, first provide the architecture or folder structure and wait for confirmation before generating all files.\n"
    "- Keep explanations short and practical unless the user explicitly asks for detailed or educational content.\n"
    "- Assume concise mode if the user does not specify the desired level of detail.\n"
    "- Do not include unnecessary introductions, summaries, or filler text.\n"
    "- Never repeat code blocks, paragraphs, or examples unless explicitly requested.\n\n"

    "Coding Rules:\n"
    "- Write clean, idiomatic, and production-quality code.\n"
    "- Generate only the relevant files, functions, or code snippets required for the task.\n"
    "- When appropriate, briefly explain important design decisions in one or two sentences.\n"
    "- For multi-file implementations, list the required files before writing code.\n\n"

    "Formatting Rules:\n"
    "- Format code in fenced Markdown code blocks with an appropriate language tag.\n"
    "- Use clear and readable formatting for terminal output.\n"
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
                full_reply = render_markdown_stream(client.stream_chat(session.messages, model=model))
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