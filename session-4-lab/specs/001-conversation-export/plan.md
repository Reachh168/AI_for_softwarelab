# Technical Implementation Plan: Session Conversation Export

**Feature Identifier:** `001-conversation-export`  
**Parent System:** Configurable Text Assistant (Python 3.10+)  

---

## 1. Technical Architecture & File Changes

In alignment with **Constitution Principle 1 (Separation of Concerns)**, the export logic is isolated into a standalone helper module `exporter.py`, keeping `main.py` lean and focused on command dispatching and user interaction.

```text
session-4-lab/
├── .specify/
│   └── memory/
│       └── constitution.md
├── specs/
│   └── 001-conversation-export/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── research.md
│       └── contracts/
│           └── export-contract.md
├── config.py             # Existing persona & default configuration
├── llm.py                # Existing LLM service & usage tracking
├── exporter.py           # [NEW] Pure export engine (formatters, file I/O)
├── main.py               # [MODIFIED] Interactive CLI handling /export command
└── test_exporter.py      # [NEW] Automated unit test suite
```

---

## 2. Component Design & Responsibilities

### `exporter.py`
Provides stateless pure functions and a clean public API:
- `generate_default_filename(persona: str, extension: str = "md") -> str`:
  Generates `session_{persona}_{timestamp}.{ext}` where timestamp is `YYYYMMDD_HHMMSS`.
- `format_markdown(messages: list[dict], metadata: dict) -> str`:
  Converts session messages and metadata into standard Markdown with frontmatter/metadata table and blockquoted role turns.
- `format_json(messages: list[dict], metadata: dict) -> str`:
  Converts session into indented, formatted JSON (`indent=2`).
- `export_session(filepath: str | Path, messages: list[dict], metadata: dict) -> str`:
  Validates extension (`.md` or `.json`), ensures non-empty conversation, creates parent directories if needed, writes file with UTF-8 encoding, and returns resolved output path. Raises `ValueError` or `ExportError` on invalid input or failure.

### `main.py` (`Session.handle_command`)
- Adds command routing for `/export`:
  ```python
  elif cmd == "/export":
      self.export_session(arg)
  ```
- Implements `Session.export_session(filepath: str)`:
  Gathers metadata (`persona`, `model`, `temperature`, `max_tokens`, `usage`), passes to `exporter.export_session()`, prints success message with destination path, and catches `ExportError` / `ValueError` to display friendly feedback without tracebacks.

---

## 3. Data Model

### Metadata Dictionary
```python
{
    "persona": "tutor",
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 500,
    "timestamp": "2026-09-17T15:30:00",
    "usage": {
        "prompt_tokens": 120,
        "completion_tokens": 85,
        "total_tokens": 205
    }
}
```

### Message Structure
```python
[
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Explain recursion"},
    {"role": "assistant", "content": "Recursion is when a function calls itself..."}
]
```

---

## 4. Error Handling Strategy (Constitution Principle 2)

| Error Scenario | Caught Exception | User-Facing CLI Message |
| -------------- | ---------------- | ----------------------- |
| No user messages | `ValueError` | `No messages to export yet.` |
| Invalid extension | `ValueError` | `Unsupported format. Please use .md or .json.` |
| File I/O / OS error | `OSError` -> `ExportError` | `Failed to export session: <reason>` |

---

## 5. Testing Strategy (Constitution Principle 4)

Use Python's built-in `unittest` module. Tests will run against temporary directories (`tempfile.TemporaryDirectory`) ensuring zero side effects:
1. `test_default_filename_format`: Verifies regex pattern `session_<persona>_\d{8}_\d{6}\.md`.
2. `test_export_markdown`: Verifies Markdown file creation, headers, metadata table, and turns.
3. `test_export_json`: Verifies JSON deserialization, structure, and values.
4. `test_empty_conversation_rejected`: Asserts `ValueError` when only system prompt exists.
5. `test_invalid_extension_rejected`: Asserts `ValueError` when saving as `.pdf` or `.txt`.
6. `test_missing_parent_directories_created`: Verifies nested subdirectories are created on demand.
