from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_governance import (
    GovernanceLegacyRouteMapping,
    GovernanceStatus,
    PolicyHistoryRecord,
    ProviderCredentialReference,
    ProviderProbeDiagnostic,
    SafePromptPreview,
    safe_governance_text,
)


def test_governance_text_rejects_secret_and_payload_markers() -> None:
    assert safe_governance_text("Safe provider summary") == "Safe provider summary"

    for unsafe in (
        "qa031-secret-value",
        "resolved credential copied into UI",
        "authorization header visible",
        "raw prompt text",
        "raw completion text",
        "/Users/scott/provider.json",
    ):
        with pytest.raises(ValueError):
            safe_governance_text(unsafe)


def test_governance_legacy_route_mapping_allows_only_safe_admin_paths() -> None:
    mapping = GovernanceLegacyRouteMapping(
        legacy_path="/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview",
        react_path="/admin/app/governance/prompts/{prompt_lineage_id}/preview",
        preserved_params=("tenant_id", "fixture_set_id"),
        compatibility_status="redirected",
        authorization_behavior="authenticated redirect with backend JSON denial",
        evidence_summary="Legacy route redirects without rendering Jinja.",
    )

    assert mapping.react_path.startswith("/admin/app/governance")

    with pytest.raises(ValidationError):
        GovernanceLegacyRouteMapping(
            legacy_path="/users/scott/secret.txt",
            react_path="/admin/app/governance/prompts",
            compatibility_status="redirected",
            authorization_behavior="authenticated redirect",
            evidence_summary="Unsafe local path rejected.",
        )


def test_provider_credential_reference_rejects_resolved_values() -> None:
    reference = ProviderCredentialReference(
        reference_id="secret-ref-openai-primary",
        label="OpenAI production reference",
        source_type="secret manager reference",
        readiness=GovernanceStatus.READY,
        fingerprint="fp_qa031_openai",
        last_resolution_status="resolved by ProviderSecretResolver",
        last_checked_label="Deterministic check",
        policy_reason="Reference is authorized for gateway use.",
        remediation="No action needed.",
    )

    assert reference.fingerprint == "fp_qa031_openai"

    with pytest.raises(ValidationError):
        ProviderCredentialReference(
            reference_id="unsafe",
            label="Unsafe reference",
            source_type="secret manager reference",
            readiness=GovernanceStatus.READY,
            fingerprint="qa031-secret-value",
            last_resolution_status="resolved credential was displayed",
            last_checked_label="Deterministic check",
            policy_reason="Reference is authorized.",
            remediation="No action needed.",
        )


def test_probe_prompt_and_history_payloads_are_redacted() -> None:
    probe = ProviderProbeDiagnostic(
        probe_id="probe-qa031-openai-primary",
        provider_id="openai-primary",
        status=GovernanceStatus.READY,
        summary="Explicit probe completed with safe diagnostics.",
        latency_bucket="under 300 ms",
        retry_state="no retry needed",
        breaker_state="closed",
        credential_resolution_status="safe reference selected",
        audit_reference_id="audit-governance-probe-qa031",
        redaction_summary="Attempt evidence is summarized.",
    )
    preview = SafePromptPreview(
        preview_id="preview-qa031",
        prompt_lineage_id="daily-briefing",
        fixture_label="Safe fixture",
        status=GovernanceStatus.SUMMARIZED,
        safe_output="Preview was summarized.",
        redaction_findings=("Prompt body summarized before rendering.",),
        variable_summary="Variables are summarized.",
        artifact_reference_id="artifact-ref-qa031-preview",
        audit_reference_id="audit-preview-qa031",
    )
    history = PolicyHistoryRecord(
        history_id="history-qa031",
        domain="routing",
        actor_label="Policy Resolver",
        tenant_scope_label="Acme",
        timestamp_label="Today",
        change_category="routing_preview",
        outcome=GovernanceStatus.READY,
        safe_diff_summary="Routing evaluated without side effects.",
        audit_reference_id="audit-history-qa031",
    )

    assert probe.status == GovernanceStatus.READY
    assert preview.status == GovernanceStatus.SUMMARIZED
    assert history.outcome == GovernanceStatus.READY

    with pytest.raises(ValidationError):
        SafePromptPreview(
            preview_id="preview-unsafe",
            prompt_lineage_id="daily-briefing",
            fixture_label="Unsafe fixture",
            status=GovernanceStatus.SUMMARIZED,
            safe_output="raw completion was rendered",
            variable_summary="Variables are summarized.",
            audit_reference_id="audit-preview-qa031",
        )
