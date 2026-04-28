from __future__ import annotations

from pathlib import Path


def test_admin_console_delivery_docs_cover_required_review_topics() -> None:
    docs = Path("docs/admin-console-shell.md").read_text()
    testing = Path("specs/010-admin-console-shell/testing-instructions.md").read_text()
    notes = Path("specs/010-admin-console-shell/pr-review-notes.md").read_text()
    readme = Path("README.md").read_text()

    required = [
        "platform scope",
        "tenant scope",
        "navigation",
        "common states",
        "safe messages",
        "saved filters",
        "audit",
        "route preservation",
        "no-js",
        "coverage",
    ]
    combined = "\n".join([docs, testing, notes, readme]).lower()

    for phrase in required:
        assert phrase in combined
