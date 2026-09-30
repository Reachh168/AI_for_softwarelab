# Feature Specification: Session Conversation Export (`/export`)

**Feature Branch / Identifier:** `001-conversation-export`  
**Status:** Clarified & Approved  
**Author:** AI Software Lab Developer  

---

## 1. Overview & Outcomes
Users of the Configurable Text Assistant need a seamless way to save their interactive dialogues for future reference, review, code extraction, or grading verification. 

### Precise Outcome Statement
The user can issue an interactive `/export [filename]` command during an active session, which saves the complete conversation history and session metadata (persona, model parameters, total token usage, timestamp) to a local file in either formatted Markdown (`.md`) or structured JSON (`.json`). If the session has no user messages or if an invalid path/format is provided, the application blocks the export with a descriptive error message without crashing.

---

## 2. User Stories

### Story 1: Default Markdown Export
As a student or developer interacting with the assistant,  
I want to type `/export` to save my session,  
So that I get a neatly formatted, human-readable Markdown log with turn-by-turn dialogue and metadata.

### Story 2: Custom Filename & JSON Format Export
As a developer building automated pipelines or archives,  
I want to specify a destination path like `/export my_session.json`,  
So that the assistant exports structured JSON data containing exact message objects and token usage stats.

### Story 3: Guardrail Against Empty History
As a user who accidentally types `/export` right after launching or clearing the session,  
I want the system to inform me that there are no conversation turns to export,  
So that empty or redundant files are not written to my workspace.

---

## 3. Functional Requirements

- **FR-1 (Command Interface):** The CLI interactive loop must recognize `/export` and `/export <filepath>`.
- **FR-2 (Format Support):** Support Markdown (`.md`) and JSON (`.json`) formats determined by file extension. If no argument is passed, default to a timestamped Markdown file: `session_<persona>_YYYYMMDD_HHMMSS.md`.
- **FR-3 (Metadata Inclusion):** Exported files must contain session metadata:
  - Persona name
  - Model name, temperature, and max tokens
  - Session timestamp (ISO 8601 format)
  - Total tokens used (prompt, completion, total)
- **FR-4 (Transcript Content):** All conversation messages (user, assistant, and system prompt) must be included in chronological order.
- **FR-5 (Empty History Handling):** If the session contains only the initial system prompt (no user interactions), export is rejected with a message: `"No messages to export yet."`.
- **FR-6 (Error Handling):** Invalid extensions (e.g., `.txt`, `.csv`, `.exe`) must display `"Unsupported format. Please use .md or .json."`. File system write failures (read-only directories, bad permissions) must be caught and displayed cleanly without tracebacks.

---

## 4. Boundaries (Non-Goals)

- **Does NOT** export history across multiple historical sessions (only in-memory messages of the active session).
- **Does NOT** upload files to external cloud storage or remote APIs.
- **Does NOT** convert messages into PDF or binary document formats.
- **Does NOT** encrypt exported files.

---

## 5. Acceptance Scenarios

1. **Scenario: Default Markdown export**
   - *Given* an active session with 2 user turns in persona `tutor`.
   - *When* the user runs `/export`.
   - *Then* a file named `session_tutor_<timestamp>.md` is created in the working directory containing a Markdown table of metadata, system prompt, and user/assistant turns, and the CLI prints the saved file path.

2. **Scenario: Custom JSON export**
   - *Given* an active session with conversation turns.
   - *When* the user runs `/export transcript.json`.
   - *Then* `transcript.json` is created with valid JSON containing keys `metadata` and `messages`, matching the schema contract.

3. **Scenario: Empty session guard**
   - *Given* a newly started or just-cleared session with 0 user turns.
   - *When* the user runs `/export`.
   - *Then* no file is created, and the CLI displays `"No messages to export yet."`.

4. **Scenario: Unsupported file extension**
   - *Given* an active session with conversation turns.
   - *When* the user runs `/export notes.pdf`.
   - *Then* no file is created, and the CLI displays `"Unsupported format. Please use .md or .json."`.

---

## 6. Edge Cases & Clarifications Resolved

1. **What if the target directory does not exist?**
   - *Decision:* Automatically create any missing parent directories specified in the path (e.g. `exports/session.md`).
2. **Should system prompts be included in the export?**
   - *Decision:* Yes, both formats will record the system prompt in the metadata/transcript so the assistant's persona context is preserved.
3. **What if the target file already exists?**
   - *Decision:* Overwrite the file and confirm saved path to keep CLI non-interactive and predictable.
