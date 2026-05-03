from __future__ import annotations

from pathlib import Path

FEATURE_DIR = Path("specs/018-user-tenant-membership-administration")


def test_membership_administration_spec_docs_exist() -> None:
    required = [
        "spec.md",
        "plan.md",
        "research.md",
        "data-model.md",
        "quickstart.md",
        "contracts/memberships.openapi.yaml",
        "contracts/admin-memberships-ui.md",
    ]

    for relative in required:
        assert (FEATURE_DIR / relative).exists(), relative


def test_membership_administration_docs_mention_safe_boundaries() -> None:
    spec = (FEATURE_DIR / "spec.md").read_text()
    plan = (FEATURE_DIR / "plan.md").read_text()

    assert "Membership Administration" in spec
    assert "MUST NOT store user passwords" in spec
    assert "tenant admins" in spec.lower()
    assert "Auth0" in plan
