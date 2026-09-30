# Spec-Driven Development (SDD) Report: Session Conversation Export

**Course:** Practical AI for Software Engineering / Software Development  
**Deliverable:** Lab 2 / Week 4 Individual Deliverable  
**Feature:** Session Conversation Export (`/export [filename]`)  
**Repository Branch:** `lab4-spec-driven`  

---

## 1. Feature & Outcomes

### Chosen Feature
The feature specified and implemented is **Session Conversation Export (`/export [filename]`)** for the Configurable Text Assistant application. This feature allows users to persist active interactive dialogues, persona prompts, and token consumption statistics to local storage on demand.

### Why It Is Mine to Specify
In our team's capstone architecture, other members are building the core LLM streaming service, persona configuration engine, and prompt engineering utilities. The session transcript exporter is an independent operational feature that consumes session state without mutating conversational logic or conflicting with other components.

### Precise Outcomes Statement
The interactive CLI provides an `/export [filename]` command during an active session that writes the complete conversation history and session metadata (persona, model name, temperature, max tokens, session timestamp, and prompt/completion/total token usage) to a local file in either formatted Markdown (`.md`) or structured JSON (`.json`). If the session contains no user messages, or if an unsupported file extension is provided, the application blocks the export and outputs a user-friendly error message without crashing.

---

## 2. The Specification (Six Elements)

### 1. Outcomes
- Persists active conversation messages (system prompt, user turns, assistant replies) in chronological order.
- Injects full session metadata (persona, model, parameters, token usage counters, ISO-8601 timestamp).
- Supports `.md` (human-readable transcript with metadata table) and `.json` (strict schema-compliant payload).
- Generates a default timestamped filename (`session_<persona>_YYYYMMDD_HHMMSS.md`) if no path argument is provided.
- Blocks execution with `"No messages to export yet."` if 0 user messages exist.
- Rejects unsupported extensions with `"Unsupported format. Please use .md or .json."`.

### 2. Boundaries (Non-Goals)
- **Does NOT** export historical conversations from prior application runs (memory-scoped to active session).
- **Does NOT** upload transcripts to external cloud storage, databases, or third-party APIs.
- **Does NOT** convert messages into PDF, DOCX, HTML, or other binary formats.
- **Does NOT** perform encryption or password protection on exported files.
- **Does NOT** alter or clear the in-memory conversation state upon export.

### 3. Constraints
- **Runtime & Language:** Python 3.10+ standard library only (`json`, `datetime`, `pathlib`, `re`). No heavy third-party export dependencies.
- **Encoding:** Explicitly enforce `UTF-8` encoding across all file operations to guarantee cross-platform compatibility on Windows and POSIX systems.
- **Fault Isolation:** The CLI must never terminate or print raw exception stack traces on file system failures (e.g. permission errors, read-only paths). All exceptions must be caught and presented as user-facing messages.
- **Directory Safety:** Missing parent directories in specified paths must be created automatically (`parents=True, exist_ok=True`).

### 4. Prior Decisions
- **Session State Structure:** Messages are represented as a mutable list of dictionaries: `[{"role": "...", "content": "..."}]` initialized with the persona system prompt (`session-2-lab` architecture).
- **Token Tracking Contract:** Usage is tracked via `LLMService.total_usage` with properties `input_tokens`, `output_tokens`, and `total_tokens`.
- **Command Syntax:** Interactive commands begin with a forward slash (`/`), parsed in `Session.handle_command(line)`.
- **User Safety Principle:** All user interactions follow Constitution Principle 2 (zero raw tracebacks for operational errors).

### 5. Task Breakdown
- **T-1.1 (Setup):** Create `exporter.py` module and define `ExportError` exception class.
- **T-1.2 (Foundation):** Implement `generate_default_filename(persona, extension, now)` with timestamp formatting.
- **T-2.1 (Implementation):** Implement `format_markdown(messages, metadata)` adhering to Markdown format contract.
- **T-2.2 (Implementation):** Implement `format_json(messages, metadata)` adhering to JSON schema contract.
- **T-2.3 (Implementation):** Implement `export_session(filepath, messages, metadata)` with format validation, empty history guards, directory auto-creation, and UTF-8 writing. *(Depends on T-1.1, T-1.2, T-2.1, T-2.2)*
- **T-3.1 (CLI Integration):** Update `HELP_TEXT` in `main.py` with `/export [filename]` documentation.
- **T-3.2 (CLI Integration):** Implement `Session.export_session(arg)` in `main.py` to extract metadata and invoke exporter. *(Depends on T-2.3)*
- **T-4.1 (Testing):** Build comprehensive unit tests in `test_exporter.py` covering format schemas, filename generation, directory creation, empty session rejection, and invalid extension handling. *(Depends on T-2.3)*
- **T-5.1 (Verification):** Execute test suite and perform manual CLI verification against acceptance scenarios.

### 6. Verification Criteria
- **VC-1 (Default Markdown Generation):** Calling `export_session(None, messages, meta)` produces a file matching pattern `session_<persona>_\d{8}_\d{6}\.md` containing `# Session Transcript: <persona>`, a Markdown usage table, system prompt blockquote, and alternating User/Assistant turns.
- **VC-2 (JSON Conformance):** Calling `export_session("out.json", messages, meta)` produces valid JSON deserializable by `json.loads()` containing top-level keys `"metadata"` and `"messages"`.
- **VC-3 (Empty History Guard):** Invoking `export_session()` on a session containing only a system prompt raises `ValueError` with `"No messages to export yet."` and creates no files.
- **VC-4 (Format Validation):** Invoking `export_session("log.pdf", messages, meta)` raises `ValueError` with `"Unsupported format. Please use .md or .json."` and creates no files.
- **VC-5 (Directory Scaffolding):** Invoking `export_session("nested/sub/dir/chat.md", ...)` creates the directory tree and writes the file successfully.
- **VC-6 (CLI Resilience):** The `/export` command in `main.py` catches `ValueError` and `ExportError`, printing the message without terminating the process or printing tracebacks.

---

## 3. Execution Log

### Prompt Provided to AI Coding Agent
The following specification and context prompt was provided to the AI agent:
```text
Task: Implement Feature 001 - Session Conversation Export for Configurable Text Assistant.
Context: Follow specs/001-conversation-export/spec.md, plan.md, and constitution.md.
Create session-4-lab/exporter.py with format_markdown(), format_json(), and export_session().
Integrate /export [filename] into session-4-lab/main.py.
Create comprehensive unit test suite in session-4-lab/test_exporter.py.
Ensure all tests pass using python -m unittest and no raw tracebacks occur.
```

### What the Agent Produced
1. **`exporter.py`**: Pure utility module containing:
   - `ExportError` exception class.
   - `generate_default_filename()` with regex-tested timestamping.
   - `format_markdown()` generating structured Markdown tables and turn blocks.
   - `format_json()` producing schema-valid indented JSON.
   - `export_session()` orchestrating input validation, folder creation, and file output.
2. **`main.py`**: Updated CLI session handler adding `/export` dispatching, metadata gathering from `LLMService.total_usage`, and error boundary catching.
3. **`test_exporter.py`**: Seven unit test cases validating all acceptance criteria using isolated temporary directories.

---

## 4. Verification Results

Every criterion was verified against the real output using automated unit tests (`python -m unittest session-4-lab/test_exporter.py -v`) and interactive CLI execution:

| Criterion | Expected Behavior | Actual Output | Status |
| --------- | ----------------- | ------------- | :----: |
| **VC-1** | Generate default timestamped Markdown transcript with metadata | Output `session_tutor_20260917_153000.md` containing `# Session Transcript: tutor`, metadata table, and turns | **PASS** |
| **VC-2** | Output schema-compliant JSON file with `metadata` and `messages` | `json.loads()` passes; keys `metadata` (with persona and usage) and `messages` verified | **PASS** |
| **VC-3** | Block export on empty session (0 user turns) with friendly error | `ValueError: No messages to export yet.` raised; 0 files created | **PASS** |
| **VC-4** | Reject unsupported extensions (`.pdf`, `.txt`) cleanly | `ValueError: Unsupported format. Please use .md or .json.` raised | **PASS** |
| **VC-5** | Auto-create missing nested parent directories | Path `nested/archive/chat.md` created; parents automatically made | **PASS** |
| **VC-6** | CLI interactive safety (zero tracebacks on error) | CLI prints `No messages to export yet.` or `Unsupported format...` and keeps running smoothly | **PASS** |

### Boundary & Constraint Checks
- **Boundary Check (No Cloud/External APIs):** Verified that `exporter.py` uses only local filesystem operations. No network calls exist.
- **Constraint Check (UTF-8 Encoding):** Verified that `open(..., encoding="utf-8")` is explicitly passed in all file write calls.
- **Constraint Check (No Extra Dependencies):** Verified that `exporter.py` imports only standard library modules (`json`, `datetime`, `pathlib`, `typing`).

---

## 5. Reflection

### Decision Matrix Evaluation
In Session 1, the decision matrix asked: *When is writing a full specification worth the overhead vs. skipping straight to code?*

| Factor | Assessment for this Feature |
| ------ | --------------------------- |
| **Ambiguity Risk** | High. Without clear specs, file format, schema, empty state behavior, and directory handling would be interpreted inconsistently. |
| **Blast Radius** | Moderate. Faulty file writing could crash the interactive session or overwrite user files. |
| **Delegation to AI** | High. An AI coding agent given vague instructions ("add export") would likely generate ad-hoc txt files, import heavy libraries like ReportLab or Pandas, or fail on empty sessions. |

**Judgment:** This feature fully warranted an executable specification. While simple in concept, the contract boundaries (Markdown table format, JSON schema, empty history guard, error isolation) directly prevented AI drift.

### What to Tighten in the Spec Next Time
Next time, I would specify an explicit **token and message truncation policy** for massive conversations. For chat sessions with hundreds of turns, writing the entire history into a single uncompressed JSON/Markdown file could consume significant memory. Adding an explicit boundary or option for pagination/filtering would make the specification even more robust for production-scale workloads.
