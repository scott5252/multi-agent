from __future__ import annotations

from pathlib import Path


def test_production_audit_debugging_docs_cover_required_topics() -> None:
    text = Path("docs/production-audit-debugging.md").read_text().lower()
    for topic in (
        "timeline",
        "trace",
        "lineage",
        "version bundles",
        "notification",
        "secret-access",
        "redaction",
        "escalation",
    ):
        assert topic in text
