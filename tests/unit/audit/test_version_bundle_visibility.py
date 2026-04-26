from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.inspection import bundle_to_dict
from multi_agent_platform.audit.models import VersionBundleSnapshotCreate
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_version_bundle_visibility_uses_safe_refs(session) -> None:
    repository = AuditDebuggingRepository(session)
    tenant_id = uuid4()
    run_id = uuid4()
    bundle = await repository.create_version_bundle_snapshot(
        VersionBundleSnapshotCreate(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            workflow_version_bundle_id=uuid4(),
            execution_bundle_id=uuid4(),
            bundle_digest="digest",
            workflow_version={"workflow": "v1"},
            contract_version_refs={"handoff": "contract-v1"},
            prompt_version_refs={"agent": "prompt-v1"},
            model_config_version_refs={"agent": "model-v1"},
            tool_policy_version_refs={"tool": "policy-v1"},
            activation_state_at_acceptance="active",
            migration_record_refs=["migration-1"],
        )
    )
    visible = bundle_to_dict(bundle)
    assert visible["bundle_digest"] == "digest"
    assert visible["activation_state_at_acceptance"] == "active"
    assert "prompt body" not in str(visible).lower()
