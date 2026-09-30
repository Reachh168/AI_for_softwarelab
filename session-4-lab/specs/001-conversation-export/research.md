# Research & Prior Decisions: Session Conversation Export

## 1. Prior Decisions Context
- **Session Architecture:** The assistant (`session-2-lab`) maintains state as a mutable list of dictionaries: `self.messages = [{"role": "system", "content": ...}, ...]`.
- **Token Tracking:** `LLMService` encapsulates token tracking via the `Usage` dataclass (`prompt_tokens`, `completion_tokens`, `total_tokens`).
- **Command Handling:** `Session.handle_command(line)` parses leading slashes (`/command`) and returns a boolean indicating whether the loop continues.
- **Error Handling Pattern:** User errors and configuration issues are reported via friendly console messages without raw stack traces.

## 2. Decision Matrix & Format Selection
- **Why Markdown (`.md`)?** Excellent for human readability, documentation, notes, and direct integration into student submission logs.
- **Why JSON (`.json`)?** Enables downstream automated evaluation, grading scripts, replay tools, and benchmarking.
- **Why reject HTML or PDF?** Extra external dependencies (e.g. `weasyprint`, `reportlab`) would violate the lightweight constraint of the project and complicate setup.

## 3. Ambiguity & Resolution Analysis
- *Question:* Should an export overwrite existing files or prompt the user?
  - *Analysis:* Interactive prompts break scripting and test automation. Overwrite is safe when explicitly named, and default filenames use millisecond/second-level timestamps, eliminating collisions.
- *Question:* How should missing directories be treated?
  - *Analysis:* If the user specifies `exports/test.md`, failing because `exports/` doesn't exist is frustrating. Calling `pathlib.Path.mkdir(parents=True, exist_ok=True)` provides smooth developer ergonomics.
