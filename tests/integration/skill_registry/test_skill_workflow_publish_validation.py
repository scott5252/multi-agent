from __future__ import annotations

from multi_agent_platform.admin.skill_registry.eligibility import InstalledSkillEvidence
from multi_agent_platform.admin.workflow_registry.publish_gate import (
    validate_installed_skill_references,
)


def test_workflow_publish_blocks_not_ready_installed_skill() -> None:
    findings = validate_installed_skill_references(
        [
            InstalledSkillEvidence(
                tenant_id="tenant-1",
                installation_id="install-1",
                installation_version=1,
                package_slug="calendar-assistant",
                semantic_version="1.2.3",
                manifest_digest="sha256:manifest",
                artifact_digest="sha256:artifact",
                readiness_state="blocked",
            )
        ]
    )

    assert findings
    assert findings[0].code == "publish_gate.skill_registry.not_eligible"
