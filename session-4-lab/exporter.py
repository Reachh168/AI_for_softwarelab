"""
exporter.py — Pure session transcript exporter for Configurable Text Assistant.

Implements Feature 001: Session Conversation Export (/export).
Supports Markdown (.md) and JSON (.json) transcript generation with full metadata.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ExportError(Exception):
    """Raised when an export operation fails due to filesystem or I/O errors."""


def generate_default_filename(persona: str, extension: str = "md", now: datetime | None = None) -> str:
    """Generate a timestamped filename for session export."""
    if now is None:
        now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    sanitized_persona = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in persona.lower())
    ext = extension.lstrip(".")
    return f"session_{sanitized_persona}_{timestamp}.{ext}"


def format_markdown(messages: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    """Format session messages and metadata into a clean Markdown transcript."""
    persona = metadata.get("persona", "default")
    model = metadata.get("model", "N/A")
    temp = metadata.get("temperature", "N/A")
    max_tokens = metadata.get("max_tokens", "N/A")
    timestamp = metadata.get("timestamp", datetime.now().isoformat())
    usage = metadata.get("usage", {})

    prompt_tok = usage.get("prompt_tokens", 0)
    compl_tok = usage.get("completion_tokens", 0)
    total_tok = usage.get("total_tokens", prompt_tok + compl_tok)

    lines: list[str] = [
        f"# Session Transcript: {persona}",
        "",
        f"**Export Date:** {timestamp}  ",
        f"**Model:** {model}  ",
        f"**Temperature:** {temp}  ",
        f"**Max Tokens:** {max_tokens}  ",
        "",
        "## Session Usage",
        "| Metric | Count |",
        "| ------ | ----- |",
        f"| Prompt Tokens | {prompt_tok} |",
        f"| Completion Tokens | {compl_tok} |",
        f"| Total Tokens | {total_tok} |",
        "",
        "---",
        "",
    ]

    # Find and format system prompt if present
    system_msgs = [m for m in messages if m.get("role") == "system"]
    if system_msgs:
        sys_content = system_msgs[0].get("content", "").strip()
        lines.append("## System Prompt")
        for sys_line in sys_content.splitlines():
            lines.append(f"> {sys_line}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Conversation")
    lines.append("")

    turn_counter = 1
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "").strip()
        if role == "system":
            continue

        role_display = "User" if role == "user" else "Assistant"
        lines.append(f"### Turn {turn_counter} — {role_display}")
        lines.append(content)
        lines.append("")
        if role == "assistant":
            turn_counter += 1

    return "\n".join(lines).strip() + "\n"


def format_json(messages: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    """Format session messages and metadata into a JSON string conforming to the contract."""
    payload = {
        "metadata": metadata,
        "messages": messages,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def export_session(
    filepath: str | Path | None,
    messages: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> str:
    """
    Export the current session transcript to disk in either .md or .json format.

    Args:
        filepath: Destination file path, or None to generate default timestamped filename.
        messages: List of conversation message dictionaries.
        metadata: Session configuration and token usage metadata.

    Returns:
        The string representation of the resolved output file path.

    Raises:
        ValueError: If there are no user conversation turns or file format is unsupported.
        ExportError: If an I/O or filesystem error prevents writing the file.
    """
    # Guard: Require at least one non-system interaction (FR-5)
    non_system = [m for m in messages if m.get("role") != "system"]
    if not non_system:
        raise ValueError("No messages to export yet.")

    # Determine file path and extension
    persona = metadata.get("persona", "default")
    if not filepath or not str(filepath).strip():
        resolved_path = Path(generate_default_filename(persona, "md"))
    else:
        resolved_path = Path(str(filepath).strip())

    ext = resolved_path.suffix.lower()
    if ext not in (".md", ".json"):
        raise ValueError("Unsupported format. Please use .md or .json.")

    # Set ISO timestamp if not already provided
    if "timestamp" not in metadata:
        metadata["timestamp"] = datetime.now().isoformat()

    # Format content
    if ext == ".md":
        content = format_markdown(messages, metadata)
    else:
        content = format_json(messages, metadata)

    # Write file safely
    try:
        if resolved_path.parent and str(resolved_path.parent) != ".":
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(content, encoding="utf-8")
    except OSError as err:
        raise ExportError(f"Failed to write export file: {err}") from err

    return str(resolved_path)
