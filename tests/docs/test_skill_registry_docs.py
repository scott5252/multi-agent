from __future__ import annotations

from pathlib import Path


def test_skill_registry_docs_and_qa_guides_exist() -> None:
    required = [
        Path("docs/skill-registry.md"),
        Path("docs/skill-registry-testing.md"),
        Path("docs/skill-registry-pr-notes.md"),
        Path("specs/014-skill-registry-lifecycle/qa014.md"),
        Path("specs/014-skill-registry-lifecycle/qa014_ui.md"),
        Path("specs/014-skill-registry-lifecycle/.env.qa014"),
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_readme_links_skill_registry_surfaces() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "/admin/skill-registry/ui/packages" in readme
    assert "/admin/skill-registry/ui/installations" in readme
