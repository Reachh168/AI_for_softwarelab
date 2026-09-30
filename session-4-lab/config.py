"""
config.py — defaults and personas for the Configurable Text Assistant.
"""

# ---- generation defaults -------------------------------------------------
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# ---- retry / backoff -----------------------------------------------------
MAX_RETRIES = 3          # never retry more than this many times
BACKOFF_BASE = 1.0       # seconds; delay = BACKOFF_BASE * 2 ** attempt
BACKOFF_MAX = 30.0       # cap the wait so we never sleep absurdly long

# ---- personas (system prompts) ------------------------------------------
DEFAULT_PERSONA = """\
You are a helpful programming assistant.
Explain concepts clearly to a Year 3 software engineering student.
"""

PERSONAS = {
    "tutor": """\
You are a programming tutor.
Explain concepts step by step.
Do not immediately provide complete solutions.
""",
    "reviewer": """\
You are a strict code reviewer.
Identify bugs, maintainability issues, and possible improvements.
""",
    "interviewer": """\
You are a software engineering interviewer.
Ask one question at a time.
Do not reveal the answer immediately.
""",
    "default": DEFAULT_PERSONA,
}


def get_persona(name: str) -> str:
    """Return the system prompt for a named persona, falling back to default."""
    return PERSONAS.get(name, DEFAULT_PERSONA)
