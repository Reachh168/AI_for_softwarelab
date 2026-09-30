"""
test_exporter.py — Unit tests for session conversation exporter.

Validates all functional requirements and acceptance criteria from specs/001-conversation-export/spec.md.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import exporter
from exporter import ExportError


class TestExporter(unittest.TestCase):

    def setUp(self):
        self.sample_metadata = {
            "persona": "tutor",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.5,
            "max_tokens": 400,
            "timestamp": "2026-09-17T15:30:00",
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 80,
                "total_tokens": 230,
            },
        }
        self.sample_messages = [
            {"role": "system", "content": "You are a programming tutor."},
            {"role": "user", "content": "What is recursion?"},
            {
                "role": "assistant",
                "content": "Recursion is when a function calls itself to solve a smaller subproblem.",
            },
        ]

    def test_default_filename_format(self):
        """Test timestamped default filename format."""
        dt = datetime(2026, 9, 17, 15, 30, 0)
        filename = exporter.generate_default_filename("tutor", "md", now=dt)
        self.assertEqual(filename, "session_tutor_20260917_153000.md")

        # Test regex pattern with live datetime
        live_filename = exporter.generate_default_filename("interviewer", "json")
        pattern = r"^session_interviewer_\d{8}_\d{6}\.json$"
        self.assertTrue(re.match(pattern, live_filename))

    def test_export_markdown_structure(self):
        """Test Markdown export satisfies contract schema and content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_session.md"
            result_path = exporter.export_session(
                target, self.sample_messages, self.sample_metadata
            )
            self.assertEqual(result_path, str(target))
            self.assertTrue(target.exists())

            content = target.read_text(encoding="utf-8")
            self.assertIn("# Session Transcript: tutor", content)
            self.assertIn("**Model:** llama-3.3-70b-versatile", content)
            self.assertIn("## Session Usage", content)
            self.assertIn("| Prompt Tokens | 150 |", content)
            self.assertIn("| Completion Tokens | 80 |", content)
            self.assertIn("| Total Tokens | 230 |", content)
            self.assertIn("## System Prompt", content)
            self.assertIn("> You are a programming tutor.", content)
            self.assertIn("### Turn 1 — User", content)
            self.assertIn("What is recursion?", content)
            self.assertIn("### Turn 1 — Assistant", content)
            self.assertIn("Recursion is when a function calls itself", content)

    def test_export_json_structure(self):
        """Test JSON export validates against JSON contract schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_session.json"
            result_path = exporter.export_session(
                target, self.sample_messages, self.sample_metadata
            )
            self.assertEqual(result_path, str(target))
            self.assertTrue(target.exists())

            data = json.loads(target.read_text(encoding="utf-8"))
            self.assertIn("metadata", data)
            self.assertIn("messages", data)
            self.assertEqual(data["metadata"]["persona"], "tutor")
            self.assertEqual(data["metadata"]["usage"]["total_tokens"], 230)
            self.assertEqual(len(data["messages"]), 3)
            self.assertEqual(data["messages"][1]["role"], "user")
            self.assertEqual(data["messages"][1]["content"], "What is recursion?")

    def test_empty_conversation_rejected(self):
        """Test that attempting to export without user messages raises ValueError (FR-5)."""
        empty_session = [{"role": "system", "content": "You are a tutor."}]
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "empty.md"
            with self.assertRaises(ValueError) as ctx:
                exporter.export_session(target, empty_session, self.sample_metadata)
            self.assertIn("No messages to export yet.", str(ctx.exception))
            self.assertFalse(target.exists())

    def test_invalid_extension_rejected(self):
        """Test that invalid file extensions are rejected (FR-6)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_target = Path(tmpdir) / "session.pdf"
            with self.assertRaises(ValueError) as ctx:
                exporter.export_session(
                    bad_target, self.sample_messages, self.sample_metadata
                )
            self.assertIn("Unsupported format. Please use .md or .json.", str(ctx.exception))
            self.assertFalse(bad_target.exists())

    def test_auto_creates_missing_directories(self):
        """Test that export automatically creates non-existent parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_target = Path(tmpdir) / "nested" / "archive" / "chat.md"
            self.assertFalse(nested_target.parent.exists())

            result_path = exporter.export_session(
                nested_target, self.sample_messages, self.sample_metadata
            )
            self.assertTrue(nested_target.exists())
            self.assertEqual(result_path, str(nested_target))

    def test_overwrite_existing_file(self):
        """Test that export overwrites an existing file cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "chat.md"
            target.write_text("Old content", encoding="utf-8")

            exporter.export_session(target, self.sample_messages, self.sample_metadata)
            new_content = target.read_text(encoding="utf-8")
            self.assertNotIn("Old content", new_content)
            self.assertIn("# Session Transcript: tutor", new_content)


if __name__ == "__main__":
    unittest.main()
