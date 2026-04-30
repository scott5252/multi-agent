from __future__ import annotations

from multi_agent_platform.admin.skill_registry.eligibility import InstalledSkillEvidence
from multi_agent_platform.runtime.skill_registry import evaluate_runtime_skill_use


def test_runtime_blocks_quarantined_installation() -> None:
    decision = evaluate_runtime_skill_use(
        InstalledSkillEvidence(
            tenant_id="tenant-1",
            installation_id="install-1",
            installation_version=1,
            package_slug="calendar-assistant",
            semantic_version="1.2.3",
            manifest_digest="sha256:manifest",
            artifact_digest="sha256:artifact",
            readiness_state="ready",
            quarantine_state="quarantined",
            runtime_blocked=True,
        )
    )

    assert decision.allowed is False
    assert "quarantine.runtime_blocked" in decision.reason_codes
