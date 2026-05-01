from __future__ import annotations

import re
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


def test_qa014_ui_is_browser_first_and_screenshot_backed() -> None:
    guide_path = Path("specs/014-skill-registry-lifecycle/qa014_ui.md")
    guide = guide_path.read_text(encoding="utf-8")

    assert "curl" not in guide.lower()

    image_paths = re.findall(
        r"!\[[^\]]+\]\((\.\./\.\./output/playwright/qa014_ui/[^)]+\.png)\)", guide
    )
    assert len(image_paths) >= 24

    missing = [
        image_path
        for image_path in image_paths
        if not (guide_path.parent / image_path).resolve().exists()
    ]
    assert missing == []
