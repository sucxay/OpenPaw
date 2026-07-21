"""
`ai explain` — explain the contents of a file using the configured LLM.
"""

from __future__ import annotations

from pathlib import Path

from config.config_manager import ConfigManager
from prompts.explain_prompt import build_explain_messages
from utils.api_client import APIClientError, LLMClient
from utils.console import print_error, print_info, print_markdown, render_markdown_stream
from utils.file_reader import extract_notebook_code, is_supported_file, read_file


def run_explain(config_manager: ConfigManager, file_path: Path, beginner: bool = False) -> None:
    """Explain a file's contents by sending it to the configured LLM.

    Validates that the file exists and is a supported type, reads its
    contents (handling `.ipynb` notebooks specially), builds an explain
    prompt, and streams or prints the model's response.

    Args:
        config_manager: Provides the active configuration and, indirectly,
            the LLM client used for chat.py — reused here for consistency.
        file_path: Path to the file to explain.
        beginner: If True, request a beginner-friendly explanation suited
            for a first-year CS student.
    """
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return
    if file_path.is_dir():
        print_error(f"Expected a file but got a directory: {file_path}")
        return

    is_notebook = file_path.suffix.lower() == ".ipynb"
    if not is_notebook and not is_supported_file(str(file_path)):
        suffix = file_path.suffix or "(no extension)"
        print_error(f"Unsupported file type '{suffix}'. See `ai explain --help` for supported types.")
        return

    try:
        content = extract_notebook_code(str(file_path)) if is_notebook else read_file(str(file_path))
    except (FileNotFoundError, IsADirectoryError, ValueError, OSError) as exc:
        print_error(str(exc))
        return

    if not content.strip():
        print_info(f"'{file_path.name}' is empty — nothing to explain.")
        return

    messages = build_explain_messages(content, file_path.name, beginner=beginner)

    cfg = config_manager.get()
    client = LLMClient(cfg)

    mode_label = "beginner-friendly " if beginner else ""
    print_info(f"Explaining '{file_path.name}' ({mode_label}mode) using model '{cfg.default_model}'...\n")

    try:
        if cfg.stream:
            render_markdown_stream(client.stream_chat(messages, model=cfg.default_model))
        else:
            reply = client.chat(messages, model=cfg.default_model)
            print_markdown(reply)
    except APIClientError as exc:
        print_error(str(exc))