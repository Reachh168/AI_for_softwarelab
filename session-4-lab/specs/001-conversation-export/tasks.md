# Tasks: Feature 001 - Session Conversation Export

This task breakdown converts the technical plan into discrete, actionable steps.

---

## Phase 1: Setup & Foundations

- [x] **T-1.1 (Setup):** Create module file `session-4-lab/exporter.py` with custom exception class `ExportError`.
- [x] **T-1.2 (Foundation):** Implement `generate_default_filename(persona: str, extension: str = "md")` with timestamp formatting.

---

## Phase 2: Core Exporter Implementation

- [x] **T-2.1 (Implementation):** Implement `format_markdown(messages: list[dict], metadata: dict) -> str` respecting the Markdown contract.
- [x] **T-2.2 (Implementation):** Implement `format_json(messages: list[dict], metadata: dict) -> str` respecting the JSON contract.
- [x] **T-2.3 (Implementation):** Implement `export_session(filepath: str | Path, messages: list[dict], metadata: dict) -> str` with validation rules:
  - Validate that at least one non-system message exists.
  - Validate file extension (`.md` or `.json`).
  - Auto-create parent directories (`parents=True, exist_ok=True`).
  - Save file with UTF-8 encoding and return resolved path.
  *(Depends on T-1.1, T-1.2, T-2.1, T-2.2)*

---

## Phase 3: CLI Integration

- [x] **T-3.1 (CLI Integration):** Update `HELP_TEXT` in `main.py` to document `/export [filename]`.
- [x] **T-3.2 (CLI Integration):** Implement `Session.export_session(self, arg: str)` in `main.py` and connect it in `handle_command()`.
  *(Depends on T-2.3)*

---

## Phase 4: Automated Testing

- [x] **T-4.1 (Testing):** Create `test_exporter.py` with unit tests for:
  - Default filename generation regex.
  - Markdown export format correctness and metadata table presence.
  - JSON export validation and schema conformance.
  - Empty conversation error guard (`ValueError: No messages to export yet.`).
  - Unsupported extension error guard (`ValueError: Unsupported format...`).
  - Automatic creation of nested subdirectories.
  *(Depends on T-2.3)*

---

## Phase 5: Verification & Traceability

- [x] **T-5.1 (Verification):** Run automated test suite (`python -m unittest session-4-lab/test_exporter.py -v`).
- [x] **T-5.2 (Traceability):** Validate each requirement in `spec.md` against test results and implementation artifacts.
