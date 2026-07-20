"""
Reusable file-reading utilities shared by the code-aware commands
(`explain`, `review`, `fix`, `generate-readme`, `agent`).

No CLI logic lives here — only pure functions for checking file support,
reading source files, and extracting code from Jupyter notebooks.
"""

from __future__ import annotations

import json
from pathlib import Path

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".js", ".ts", ".java", ".cpp", ".c", ".rs", ".md", ".json", ".txt",".ipynb"}
)


def is_supported_file(file_path: str) -> bool:
    """Check whether a file's extension is supported by OpenPaw."""
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS


def read_file(file_path: str) -> str:
    """Read a text file's contents using UTF-8 encoding."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file but got a directory: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"File is not valid UTF-8 text: {path}") from exc
    except OSError as exc:
        raise OSError(f"Could not read file '{path}': {exc}") from exc


def extract_notebook_code(file_path: str) -> str:
    """Extract and combine all code-cell source from a Jupyter notebook."""
    raw = read_file(file_path)
    try:
        notebook = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"File is not valid notebook JSON: {file_path}") from exc

    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise ValueError(f"Notebook is missing a valid 'cells' list: {file_path}")

    code_blocks: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        code_text = "".join(source) if isinstance(source, list) else str(source)
        if code_text.strip():
            code_blocks.append(code_text)

    return "\n\n".join(code_blocks)