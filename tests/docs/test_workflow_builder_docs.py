from __future__ import annotations

from pathlib import Path


def test_workflow_builder_docs_include_required_reviewer_sections() -> None:
    guide = Path("docs/admin-workflow-builder.md").read_text()
    testing = Path("docs/admin-workflow-builder-testing.md").read_text()
    notes = Path("docs/admin-workflow-builder-pr-notes.md").read_text()
    readme = Path("README.md").read_text()

    for expected in (
        "Authoring Flow",
        "Validation Flow",
        "Publication Flow",
        "Revision And Audit Flow",
    ):
        assert expected in guide
    for expected in (
        "Local Principal Setup",
        "Negative Path Checks",
        "Security And Redaction Checks",
        "Automated Evidence",
    ):
        assert expected in testing
    assert "QA Evidence Checklist" in notes
    assert "admin-workflow-builder.md" in readme
