"""
Prompt construction for `ai explain`.

No CLI logic, file I/O, or API calls live here — only pure functions that
turn source code into the chat messages sent to the LLM.
"""

from __future__ import annotations

STANDARD_SYSTEM_PROMPT = (
    "You are an expert software engineer explaining code to another "
    "developer. Explain what the file does at a high level, then describe "
    "the purpose of each significant function or class. Point out any bugs, "
    "unclear logic, or opportunities for improvement. Be precise and avoid "
    "restating the code line by line. Format code references in fenced "
    "Markdown code blocks with a language tag."
)

BEGINNER_SYSTEM_PROMPT = (
    "You are a patient programming tutor explaining code to a first-year "
    "Computer Science undergraduate who is still learning to code. Avoid "
    "unexplained jargon — define any technical term you need to use in "
    "plain language, and use simple, everyday analogies where they help. "
    "Walk through what the file does step by step, and explain each "
    "function or class in a way that builds understanding rather than "
    "just describing syntax. Keep the tone encouraging. Still mention any "
    "bugs or improvements, but explain *why* they matter. Format code "
    "references in fenced Markdown code blocks with a language tag."
)


def build_explain_messages(
    code: str, file_name: str, beginner: bool = False
) -> list[dict[str, str]]:
    """Build the chat messages used to ask the LLM to explain a file.

    Args:
        code: The source code (or extracted notebook code) to explain.
        file_name: Display name of the file, used for context in the prompt.
        beginner: If True, use the beginner-friendly system prompt suited
            for a first-year CS student instead of the standard one.

    Returns:
        A list of chat messages (`system` then `user`) ready to pass to
        `LLMClient.chat` or `LLMClient.stream_chat`.
    """
    system_prompt = BEGINNER_SYSTEM_PROMPT if beginner else STANDARD_SYSTEM_PROMPT
    user_prompt = f"Explain the following file: `{file_name}`.\n\n```\n{code}\n```"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]