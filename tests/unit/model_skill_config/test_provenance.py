from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import (
    ConfigKind,
    DecisionCategory,
    PolicyOutcome,
)
from multi_agent_platform.config.provenance import (
    ResolvedConfigurationSnapshot,
    SafeRuntimeDecision,
    audit_diff_summary,
)


def test_resolved_configuration_digest_is_stable() -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    run_bundle_id = uuid4()
    workflow_version_bundle_id = uuid4()
    version_ids = (uuid4(), uuid4())
    first = ResolvedConfigurationSnapshot(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        run_bundle_id=run_bundle_id,
        bundle_digest="bundle",
        workflow_version_bundle_id=workflow_version_bundle_id,
        model_routing_version_ids=version_ids,
    )
    second = ResolvedConfigurationSnapshot(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        run_bundle_id=run_bundle_id,
        bundle_digest="bundle",
        workflow_version_bundle_id=workflow_version_bundle_id,
        model_routing_version_ids=tuple(reversed(version_ids)),
    )

    assert first.digest() == second.digest()


def test_safe_runtime_decision_serializes_safe_payload() -> None:
    decision = SafeRuntimeDecision(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        decision_category=DecisionCategory.TOOL,
        outcome=PolicyOutcome.DENY,
        requested_resource="http.fetch",
        idempotency_key="run-step-tool-1",
        denial_category="tool_denied",
        safe_reason="denied",
        evaluated_version_ids=(uuid4(),),
    )

    payload = decision.to_record_payload()

    assert payload["outcome"] == "deny"
    assert payload["idempotency_key"] == "run-step-tool-1"
    assert "evaluated_version_ids" in payload


def test_audit_diff_summary_redacts_sensitive_keys() -> None:
    summary = audit_diff_summary(
        action="activate",
        config_kind=ConfigKind.SECRET_REFERENCE,
        prior_version_id=None,
        new_version_id=uuid4(),
        summary={"token": "secret", "scope": "safe"},
    )

    assert summary["summary"] == {"token": "***REDACTED***", "scope": "safe"}
