# Export Contract: Schemas and Formats

This document specifies the exact format contracts for exported session transcripts.

---

## 1. Markdown Contract (`.md`)

Exported Markdown files must adhere to the following template:

```markdown
# Session Transcript: {persona}

**Export Date:** {ISO_8601_TIMESTAMP}  
**Model:** {model}  
**Temperature:** {temperature}  
**Max Tokens:** {max_tokens}  

## Session Usage
| Metric | Count |
| ------ | ----- |
| Prompt Tokens | {prompt_tokens} |
| Completion Tokens | {completion_tokens} |
| Total Tokens | {total_tokens} |

---

## System Prompt
> {system_prompt_content}

---

## Conversation

### Turn 1 — User
{user_message_1}

### Turn 1 — Assistant
{assistant_message_1}

...
```

---

## 2. JSON Contract (`.json`)

Exported JSON files must adhere to the following JSON Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SessionExport",
  "type": "object",
  "required": ["metadata", "messages"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["persona", "model", "temperature", "max_tokens", "timestamp", "usage"],
      "properties": {
        "persona": { "type": "string" },
        "model": { "type": "string" },
        "temperature": { "type": "number" },
        "max_tokens": { "type": "integer" },
        "timestamp": { "type": "string" },
        "usage": {
          "type": "object",
          "required": ["prompt_tokens", "completion_tokens", "total_tokens"],
          "properties": {
            "prompt_tokens": { "type": "integer" },
            "completion_tokens": { "type": "integer" },
            "total_tokens": { "type": "integer" }
          }
        }
      }
    },
    "messages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["role", "content"],
        "properties": {
          "role": { "type": "string", "enum": ["system", "user", "assistant"] },
          "content": { "type": "string" }
        }
      }
    }
  }
}
```
