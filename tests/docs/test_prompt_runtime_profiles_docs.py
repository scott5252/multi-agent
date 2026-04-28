from __future__ import annotations


def test_prompt_runtime_docs_are_linked_and_reviewer_ready() -> None:
    docs = open("docs/prompt-runtime-profiles.md", encoding="utf-8").read()
    testing = open("docs/prompt-runtime-profiles-testing.md", encoding="utf-8").read()
    pr_notes = open("docs/prompt-runtime-profiles-pr-notes.md", encoding="utf-8").read()
    readme = open("README.md", encoding="utf-8").read()

    assert "Prompt Library" in docs
    assert "uv run pytest" in testing
    assert "rollback" in pr_notes.lower()
    assert "prompt-runtime-profiles.md" in readme
