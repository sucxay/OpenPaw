# terminal-ai

A lightweight, modular, terminal-based AI coding assistant, in the spirit of
Claude Code, Gemini CLI, and Aider — built to work against **any
OpenAI-compatible API endpoint**, including a locally-running
[FreeLLMAPI](http://localhost:3001/v1) server.

> **Status: Phase 1.** Core CLI, interactive chat, configuration management,
> model listing/switching, and history are fully implemented. Project
> review/fix, `explain`, `generate-readme`, `commit`, and `agent` are wired
> into the CLI as commands but are stubbed for a later phase — see
> [Roadmap](#roadmap).

## Features (Phase 1)

- **`ai chat`** — interactive, multi-turn, streaming chat with Markdown /
  syntax-highlighted code rendering, and automatic conversation persistence.
- **`ai models`** — list models exposed by your backend (name, provider,
  context length, status).
- **`ai switch-model`** — interactively (or directly) change the default
  model.
- **`ai history`** / **`ai clear-history`** — list, inspect, and wipe saved
  conversations.
- **`ai config`** — view and edit API key, base URL, default model,
  temperature, max tokens, streaming, and theme, either interactively or
  with `--set key=value`.
- No hardcoded model names — works with any OpenAI-compatible server.
- Config and history are stored locally under `~/.terminal-ai/`.

## Installation

```bash
cd terminal-ai
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# optional: install the `ai` command on your PATH
pip install -e .
```

Requires Python 3.12+.

## Configuration

By default the assistant talks to a FreeLLMAPI-style server at
`http://localhost:3001/v1`. Configure it with:

```bash
ai config                          # view current config, offers interactive edit
ai config --set base_url=http://localhost:3001/v1
ai config --set api_key=sk-...
ai config --set default_model=my-model
ai config --set temperature=0.5
ai config --set max_tokens=4096
ai config --set stream=true
```

Every setting can also be provided via environment variable, which takes
priority over the config file:

| Env var                      | Config field    |
|-------------------------------|-----------------|
| `TERMINAL_AI_API_KEY`         | `api_key`       |
| `TERMINAL_AI_BASE_URL`        | `base_url`      |
| `TERMINAL_AI_DEFAULT_MODEL`   | `default_model` |
| `TERMINAL_AI_TEMPERATURE`     | `temperature`   |
| `TERMINAL_AI_MAX_TOKENS`      | `max_tokens`    |
| `TERMINAL_AI_STREAM`          | `stream`        |
| `TERMINAL_AI_THEME`           | `theme`         |
| `TERMINAL_AI_HOME`            | config/history root directory (default `~/.terminal-ai`) |

Config is stored as JSON at `~/.terminal-ai/config.json`.

## Usage

```bash
ai chat                       # start a new interactive session
ai chat --model other-model   # override the model for this session
ai chat --resume <session_id> # continue a saved conversation

ai models                     # list models from the backend
ai switch-model               # interactive picker
ai switch-model my-model      # switch directly

ai history                    # list saved sessions
ai history <session_id>       # view a session in full
ai clear-history               # delete all saved sessions (asks to confirm)
ai clear-history --yes         # skip confirmation

ai help                       # full command reference
```

Inside `ai chat`, type `exit`, `quit`, `:q`, or `:wq` to leave — the session
is saved automatically either way.

## Project structure

```
terminal-ai/
├── main.py            # Typer CLI entry point — wires up all commands
├── cli/                # (reserved for future CLI-only helpers)
├── commands/           # one module per command's logic
│   ├── chat.py
│   ├── config_cmd.py
│   ├── models_cmd.py
│   └── history_cmd.py
├── utils/
│   ├── api_client.py   # OpenAI-compatible client wrapper (streaming + non-streaming)
│   └── console.py       # shared Rich console + formatting helpers
├── config/
│   └── config_manager.py
├── history/
│   └── history_manager.py
├── prompts/            # (reserved for phase-2 system/task prompt templates)
├── agents/             # (reserved for `ai agent` task planning/execution)
├── models/              # (reserved for phase-2 model-specific helpers)
├── tests/               # pytest unit tests
├── requirements.txt
└── pyproject.toml
```

## Technologies used

- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Rich](https://rich.readthedocs.io/) — terminal formatting, tables,
  Markdown/syntax rendering, live-updating streaming output
- [openai](https://github.com/openai/openai-python) Python SDK, pointed at
  a custom `base_url` — used purely as an OpenAI-compatible HTTP client,
  works against FreeLLMAPI or any other compatible server
- [pytest](https://pytest.org/) — unit tests

## Testing

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

15 unit tests cover configuration loading/saving/env-overrides, history
persistence, and the API client's streaming/non-streaming/error paths
(using a fake completions client, so no network or live server is needed).

## Roadmap

Planned for later phases, per the original project spec:

- `ai review .` — recursive project scan with a code-quality report, bugs,
  security/performance issues, and a score out of 10.
- `ai fix .` — analyze, diff, confirm, and apply fixes across Python, JS,
  TS, C++, Java, Markdown, and JSON.
- `ai explain <file>` — code explanation, with a `--beginner` mode.
- `ai generate-readme` — auto-generate a full README from the project.
- `ai commit` — read `git diff`, propose a conventional-commit message,
  confirm, then commit.
- `ai agent "<task>"` — break a natural-language task into steps and
  execute them (create/modify files, generate code), confirming before
  destructive changes.

These commands are already registered in the CLI (`ai <command> --help`
works today) and currently print a short notice pointing here; their logic
lives in `commands/`, `agents/`, and `prompts/` once implemented.
