from __future__ import annotations

from pathlib import Path

QA014_SCREENSHOTS = Path("output/playwright/qa014_ui")
QA014_UI_GUIDE = Path("specs/014-skill-registry-lifecycle-v2/qa014_ui.md")


def test_platform_admin_browser_evidence_is_complete() -> None:
    expected = {
        "01-login-platform-admin.png",
        "02-package-list-empty.png",
        "03-package-create-form.png",
        "05-manifest-candidate-form.png",
        "06-validation-findings.png",
        "07-publish-gate.png",
        "08-tenant-grant-form.png",
        "09-package-detail-published-granted.png",
        "10-version-detail-provenance.png",
    }

    actual = {path.name for path in QA014_SCREENSHOTS.glob("*.png")}

    assert expected.issubset(actual)


def test_tenant_admin_browser_evidence_is_complete() -> None:
    expected = {
        "11-login-acme-tenant-admin.png",
        "12-acme-available-versions.png",
        "13-install-granted-skill.png",
        "14-installation-detail-blocked.png",
        "15-credential-picker.png",
        "16-installation-detail-ready.png",
        "17-installation-list-ready.png",
        "18-binding-eligibility-preview.png",
    }

    actual = {path.name for path in QA014_SCREENSHOTS.glob("*.png")}

    assert expected.issubset(actual)


def test_isolation_conflict_and_redaction_browser_evidence_is_complete() -> None:
    expected = {
        "19-stale-revision-recovery.png",
        "20-login-globex-tenant-admin.png",
        "21-globex-available-versions-empty.png",
        "22-globex-installation-list-empty.png",
        "23-globex-direct-link-denied.png",
        "24-redaction-evidence.png",
    }

    actual = {path.name for path in QA014_SCREENSHOTS.glob("*.png")}

    assert expected.issubset(actual)


def test_qa014_ui_keeps_primary_lifecycle_actions_browser_first() -> None:
    guide = QA014_UI_GUIDE.read_text(encoding="utf-8").lower()
    forbidden_primary_actions = (
        "post /admin/skill-registry/packages",
        "post /admin/skill-registry/installations",
        "post /admin/skill-registry/ui/installations",
        "curl http://",
        "curl https://",
        "curl -x",
        "curl -h",
        "curl -d",
        "curl --data",
        "curl --request",
    )

    assert all(action not in guide for action in forbidden_primary_actions)
    assert "browser walkthrough" in guide
    assert "stale revision" in guide
    assert "redaction" in guide
