# OpenPaw

> Chat. Explain. Configure. Build.

OpenPaw is an open-source AI coding assistant for your terminal, inspired by tools like Claude Code, Gemini CLI, and Aider.

It works with any OpenAI-compatible API endpoint, allowing you to use local or hosted models with a simple and developer-friendly command-line experience.

Whether you're chatting with your favorite model, explaining unfamiliar code, or managing AI configurations, OpenPaw brings powerful AI capabilities directly to your terminal.

> **Current Status:** Phase 1 is complete. Core chat, code explanation, configuration management, model switching, and conversation history are fully implemented. Advanced project analysis and agent capabilities are planned for future releases.

---

## Why OpenPaw?

* Works with any OpenAI-compatible API provider.
* Supports locally hosted models and custom endpoints.
* Interactive AI chat with streaming responses.
* Explain source code files directly from your terminal.
* Lightweight, modular, and easy to extend.
* Stores configuration and conversation history locally.
* Designed for future AI agent capabilities.
* Beginner-friendly installation and configuration.

---

## Features

OpenPaw currently supports:

* `paw chat` – Interactive multi-turn AI conversations with Markdown and syntax-highlighted code rendering.
* `paw explain` – Explain source code files directly from your terminal.
* `paw models` – View all available models exposed by your configured backend.
* `paw switch-model` – Change your default model interactively or directly.
* `paw history` – View saved conversations.
* `paw clear-history` – Delete saved conversation history.
* `paw config` – Configure API keys, models, themes, and other settings.
* Automatic conversation persistence.
* Streaming and non-streaming AI responses.
* Compatible with any OpenAI-compatible API endpoint.

---

## Requirements

Before installing OpenPaw, make sure you have:

* Python 3.12 or newer
* An OpenAI-compatible API endpoint (FreeLLMAPI or any compatible provider)

Check your Python version:

```bash
python3 --version
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sucxay/OpenPaw.git
cd OpenPaw
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

### 4. Install the Dependencies

```bash
pip install -r requirements.txt
```

### 5. Install OpenPaw Locally

```bash
pip install -e .
```

### 6. Verify the Installation

```bash
paw --help
```

If the installation was successful, you should see the list of available OpenPaw commands.

---

## Quick Start

Start chatting with your AI model:

```bash
paw chat
```

Explain a source code file:

```bash
paw explain main.py
```

View available models:

```bash
paw models
```

Configure OpenPaw:

```bash
paw config
```

Switch your default model:

```bash
paw switch-model
```

View conversation history:

```bash
paw history
```

Delete conversation history:

```bash
paw clear-history
```

---

## Configuration

By default, OpenPaw is configured to work with a FreeLLMAPI-style server running at:

```text
http://localhost:3001/v1
```

View your current configuration:

```bash
paw config
```

Update individual settings:

```bash
paw config --set base_url=http://localhost:3001/v1
paw config --set api_key=your-api-key
paw config --set default_model=your-model-name
paw config --set temperature=0.5
paw config --set max_tokens=4096
paw config --set stream=true
```

---

## Environment Variables

Every configuration option can also be provided through environment variables.

| Environment Variable  | Configuration Field                 |
| --------------------- | ----------------------------------- |
| OPENPAW_API_KEY       | api_key                             |
| OPENPAW_BASE_URL      | base_url                            |
| OPENPAW_DEFAULT_MODEL | default_model                       |
| OPENPAW_TEMPERATURE   | temperature                         |
| OPENPAW_MAX_TOKENS    | max_tokens                          |
| OPENPAW_STREAM        | stream                              |
| OPENPAW_THEME         | theme                               |
| OPENPAW_HOME          | Configuration and history directory |

Environment variables always take priority over values stored in the configuration file.

---

## Configuration Files

OpenPaw stores its configuration locally.

Configuration file:

```text
~/.openpaw/config.json
```

Conversation history:

```text
~/.openpaw/
```

Your data remains local unless it is explicitly sent to your configured AI provider.

---

## Usage

### Chat

Start a new AI conversation:

```bash
paw chat
```

Use a specific model for the current session:

```bash
paw chat --model your-model-name
```

Resume a previous conversation:

```bash
paw chat --resume <session_id>
```

Exit the chat session using:

```text
exit
quit
:q
:wq
```

All conversations are automatically saved.

---

### Explain Code

Explain a source code file:

```bash
paw explain <file>
```

Examples:

```bash
paw explain main.py
paw explain utils/api_client.py
paw explain models/model.py
```

The `paw explain` command is useful for understanding unfamiliar codebases and learning how individual files work.

---

### Models

View all available models:

```bash
paw models
```

---

### Switch Models

Switch interactively:

```bash
paw switch-model
```

Switch directly:

```bash
paw switch-model your-model-name
```

---

### History

List all saved conversations:

```bash
paw history
```

View a specific conversation:

```bash
paw history <session_id>
```

---

### Clear History

Delete all saved conversations:

```bash
paw clear-history
```

Skip the confirmation prompt:

```bash
paw clear-history --yes
```

---

### Help

View all available commands and options:

```bash
paw --help
```

Or:

```bash
paw help
```

---

## Project Structure

```text
OpenPaw/
├── main.py
├── cli/
├── commands/
│   ├── chat.py
│   ├── config_cmd.py
│   ├── models_cmd.py
│   └── history_cmd.py
├── utils/
│   ├── api_client.py
│   └── console.py
├── config/
│   └── config_manager.py
├── history/
│   └── history_manager.py
├── prompts/
├── agents/
├── models/
├── tests/
├── requirements.txt
├── README.md
└── pyproject.toml
```

---

## Technologies Used

OpenPaw is built using:

* Typer
* Rich
* OpenAI Python SDK
* Pytest

These libraries provide a fast, modern, and extensible foundation for building terminal-based AI applications.

---

## Running Tests

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
pytest tests/ -v
```

The current test suite covers:

* Configuration management
* Environment variable overrides
* Conversation history persistence
* API client functionality
* Streaming and non-streaming responses
* Error handling

---

## Roadmap

The following features are planned for future releases:

### Project Review

```bash
paw review .
```

* Recursive project scanning.
* Code quality analysis.
* Performance and security suggestions.
* Overall project scoring.

---

### Automatic Fixes

```bash
paw fix .
```

* Detect and propose fixes across multiple programming languages.
* Show diffs before applying changes.

---

### README Generation

```bash
paw generate-readme
```

* Automatically generate professional project documentation.

---

### Git Commit Assistant

```bash
paw commit
```

* Analyze Git changes.
* Suggest conventional commit messages.
* Confirm before committing.

---

### AI Agent Mode

```bash
paw agent "<task>"
```

* Break natural language tasks into executable steps.
* Create or modify files.
* Generate code.
* Confirm before performing destructive operations.

---

## Contributing

Contributions are welcome.

If you'd like to improve OpenPaw, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.

---

Built with Python for developers who love working in the terminal.
