
from __future__ import annotations

import os
from pathlib import Path

from utils.file_reader import is_supported_file

IGNORED_DIRS: frozenset[str] = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist",
     ".ipynb_checkpoints", ".pytest_cache"}
)

IGNORED_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".csv",
     ".pth", ".pt", ".onnx", ".mp4", ".mov"}
)

IGNORED_FILENAMES: frozenset[str] = frozenset(
    {".DS_Store", "package-lock.json", "yarn.lock"}
)


def should_ignore(path: Path) -> bool:
    """Check whether a file or directory should be excluded from scans."""
    if path.name in IGNORED_DIRS or path.name in IGNORED_FILENAMES:
        return True
    if path.suffix.lower() in IGNORED_EXTENSIONS:
        return True
    return False


def scan_project(project_path: str) -> list[Path]:
    """Recursively scan a project directory for supported source files."""
    root = Path(project_path)
    found_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not should_ignore(current_dir / d)]

        for filename in filenames:
            file_path = current_dir / filename
            if should_ignore(file_path):
                continue
            if is_supported_file(str(file_path)):
                found_files.append(file_path)

    return found_files


def get_source_files(project_path: str) -> list[Path]:
    """Get all supported source files in a project, sorted alphabetically."""
    return sorted(scan_project(project_path))


def get_project_tree(project_path: str) -> str:
    """Build a clean, tree-style string representation of a project."""
    root = Path(project_path).resolve()
    root_label = root.name or str(root)
    lines = [f"{root_label}/"]
    _append_tree_lines(root, prefix="", lines=lines)
    return "\n".join(lines)


def _append_tree_lines(directory: Path, prefix: str, lines: list[str]) -> None:
    """Recursively append tree-formatted entries for a directory."""
    try:
        entries = [p for p in directory.iterdir() if not should_ignore(p)]
    except OSError:
        return

    entries.sort(key=lambda p: (p.is_dir(), p.name.lower()))

    for index, entry in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        display_name = f"{entry.name}/" if entry.is_dir() else entry.name
        lines.append(f"{prefix}{connector}{display_name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            _append_tree_lines(entry, prefix + extension, lines)