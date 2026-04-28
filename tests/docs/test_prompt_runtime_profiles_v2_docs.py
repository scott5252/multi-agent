from __future__ import annotations

from pathlib import Path


def test_prompt_runtime_profiles_v2_docs_include_reviewer_commands_and_safety() -> None:
    docs = Path("docs/prompt-runtime-profiles.md").read_text()
    testing = Path("docs/prompt-runtime-profiles-testing.md").read_text()
    notes = Path("docs/prompt-runtime-profiles-pr-notes.md").read_text()
    readme = Path("README.md").read_text()

    for source in (docs, testing, notes, readme):
        assert "Spec 012 V2" in source
        assert "ModelGateway" in source

    assert "uv run pytest tests/unit/model_providers" in testing
    assert "no destructive migrations" in notes.lower()
    assert "prompt-runtime-profiles-testing.md" in readme
