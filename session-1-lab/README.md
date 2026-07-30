# AskBot — Week 1, Session 1 Lab

A tiny command-line chatbot built on a large language model. You build it up in
five parts: a single completion, an interactive chat with memory, CLI
persona/temperature controls, production-grade error handling with token
tracking, and optional stretch goals. Full instructions are in the lab handout
(`Week1_Session1_Coding_Lab.docx`).

---

## Prerequisites

- Python 3.9+
- An API key from an OpenAI-compatible provider (see [Configuration](#configuration))

## Setup

```bash
# create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# create your .env from the template, then paste in your key
cp .env.example .env
```

## Configuration

Your key and model live in `.env` (never commit this file — it's git-ignored).
Pick **one** provider in `.env.example` and fill it in:

| Provider | Cost | Notes |
|----------|------|-------|
| **Groq** (recommended) | Free, no credit card | Fast; get a key at <https://console.groq.com> |
| OpenAI | Paid (credits) | Use if your account has billing set up |
| Ollama | Free, local | Runs offline; start `ollama serve` first |

The code is identical across providers — only `.env` changes.

## Usage

```bash
# single question, then exit
python askbot.py --once "Explain what an API is in one sentence."

# interactive chat (type 'quit' to exit)
python askbot.py

# set a persona and temperature
python askbot.py --persona "You are a terse senior code reviewer." --temp 0.2
```

## Files

```
askbot.py            # your work — implement the TODOs, part by part
requirements.txt     # dependencies
.env.example         # config template — copy to .env
NOTES.md             # your observations (part of submission)
Week1_Session1_Coding_Lab.docx   # the full lab handout
```

## The lab, in five parts

1. **First completion** — send one prompt, print the reply.
2. **Interactive REPL** — keep the conversation so the bot remembers context.
3. **Persona & temperature** — control behaviour from the command line.
4. **Production-ready** — handle API errors, retry on failure, track tokens.
5. **Stretch** — streaming output, slash commands (`/tokens`, `/reset`, `/summarize`), file summarisation.

## Submission (Lab 0)

Commit your working `askbot.py`, the config files, and a completed `NOTES.md`
(what you observed about statelessness, temperature, and token usage).
**Do not commit your `.env`.**

## Troubleshooting

| Symptom | Likely fix |
|---------|-----------|
| `No module named openai` | Activate your venv, then `pip install -r requirements.txt` |
| `401` / authentication error | Key missing or misnamed in `.env`; confirm `load_dotenv()` runs |
| Bot forgets everything | You're not appending to `history` (or you rebuild it each turn) |
| Rate-limited | Expected on free tiers — this is what Part 4's retry handles |

---

*Course: Practical AI for Software Engineering · Week 1, Session 1*
