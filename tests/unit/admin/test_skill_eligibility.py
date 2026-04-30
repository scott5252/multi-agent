from __future__ import annotations

from multi_agent_platform.admin.skill_registry.eligibility import (
    InstalledSkillEvidence,
    evaluate_binding_eligibility,
)


def _evidence(**overrides: object) -> InstalledSkillEvidence:
    values = {
        "tenant_id": "tenant-1",
        "installation_id": "install-1",
        "installation_version": 1,
        "package_slug": "calendar-assistant",
        "semantic_version": "1.2.3",
        "manifest_digest": "sha256:manifest",
        "artifact_digest": "sha256:artifact",
        "readiness_state": "ready",
        "action_categories": ("read",),
    }
    values.update(overrides)
    return InstalledSkillEvidence(**values)


def test_binding_eligibility_allows_ready_installation() -> None:
    decision = evaluate_binding_eligibility(
        _evidence(),
        required_action_categories={"read"},
    )

    assert decision.allowed is True
    assert decision.evidence["installation_version"] == 1


def test_binding_eligibility_denies_quarantined_installation() -> None:
    decision = evaluate_binding_eligibility(
        _evidence(quarantine_state="quarantined", runtime_blocked=True),
    )

    assert decision.allowed is False
    assert "quarantine.runtime_blocked" in decision.reason_codes


def test_binding_eligibility_reports_readiness_policy_and_credential_reasons() -> None:
    decision = evaluate_binding_eligibility(
        _evidence(
            readiness_state="blocked",
            credential_status="blocked",
            compatibility_status="blocked",
            permission_status="blocked",
        )
    )

    assert decision.allowed is False
    assert "installation.not_ready" in decision.reason_codes
    assert "credential.not_ready" in decision.reason_codes
    assert "compatibility.not_ready" in decision.reason_codes
    assert "permission.not_ready" in decision.reason_codes
