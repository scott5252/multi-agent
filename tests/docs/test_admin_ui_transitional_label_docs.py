from __future__ import annotations

from pathlib import Path

FEATURE_DIR = Path("specs/059-admin-ui-transitional-react-label-removal")


def test_qa059_docs_explain_admin_terminology_gate() -> None:
    combined = "\n".join(
        (FEATURE_DIR / name).read_text(encoding="utf-8")
        for name in ("qa059.md", "qa059_ui.md", "qa059_user_guide.md", "pr_notes.md")
    )

    assert "Admin terminology gate" in combined
    assert "Transitional label gate" in combined
    assert "allowed implementation references" in combined.lower()
    assert "blocked_count=0" in combined
    assert "qa059-admin-entry.png" in combined
    assert "qa059-domain-pages.png" in combined


def test_qa059_docs_are_redaction_safe() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in FEATURE_DIR.glob("qa059*.md")
    )

    assert "/Users/" not in combined
    assert "qa059-secret-value" not in combined
    assert "authorization header value" not in combined.lower()
    assert "raw completion text" not in combined.lower()
