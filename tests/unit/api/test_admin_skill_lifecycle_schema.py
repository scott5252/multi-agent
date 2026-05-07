from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_skill_lifecycle import (
    BindingEligibilityPreview,
    ConnectorReadinessSummary,
    CredentialReferenceOption,
    SkillExecutionDiagnosticSummary,
    SkillLegacyRouteMapping,
    SkillLifecycleStatus,
    SkillPackageCandidate,
    safe_skill_lifecycle_text,
)


def test_skill_lifecycle_text_rejects_unsafe_markers() -> None:
    assert safe_skill_lifecycle_text("Safe manifest summary") == "Safe manifest summary"

    for unsafe in (
        "qa032-secret-value",
        "raw manifest text copied into UI",
        "resolved credential copied into UI",
        "authorization header visible",
        "connector request body",
        "raw tool output",
        "/Users/scott/manifest.json",
    ):
        with pytest.raises(ValueError):
            safe_skill_lifecycle_text(unsafe)


def test_package_candidate_rejects_manifest_echo() -> None:
    candidate = SkillPackageCandidate(
        audit_reference_id="audit-skill-candidate-qa032",
        candidate_id="qa032-candidate",
        candidate_revision="candidate-rev-qa032-current",
        manifest_digest="sha256:qa032dailybriefing",
        manifest_source="upload",
        package_slug="daily-briefing-connectors",
        safe_documentation_summary="Documentation summary is safe.",
        safe_manifest_summary="Daily briefing connector package summary.",
        smoke_evidence_status=SkillLifecycleStatus.PASSED,
        validation_status=SkillLifecycleStatus.READY,
    )

    assert candidate.manifest_source == "upload"

    with pytest.raises(ValidationError):
        SkillPackageCandidate(
            audit_reference_id="audit-skill-candidate-qa032",
            candidate_id="qa032-candidate",
            candidate_revision="candidate-rev-qa032-current",
            manifest_digest="sha256:qa032dailybriefing",
            manifest_source="paste",
            package_slug="daily-briefing-connectors",
            safe_documentation_summary="Documentation summary is safe.",
            safe_manifest_summary="raw manifest copied into browser",
            smoke_evidence_status=SkillLifecycleStatus.PASSED,
            validation_status=SkillLifecycleStatus.READY,
        )


def test_credential_connector_diagnostic_and_binding_payloads_are_redacted() -> None:
    credential = CredentialReferenceOption(
        reference_id="cred-ref-acme-briefing",
        label="Acme briefing connector reference",
        source_type="tenant secret reference",
        readiness=SkillLifecycleStatus.READY,
        fingerprint="fp_qa032_acme_briefing",
        policy_reason="Reference is authorized for read-only briefing tools.",
        last_checked_label="Deterministic QA032 check",
        remediation="No action needed.",
    )
    connector = ConnectorReadinessSummary(
        connector_id="connector-calendar",
        connector_label="Calendar",
        tool_names=("calendar.read",),
        readiness=SkillLifecycleStatus.READY,
        credential_status=SkillLifecycleStatus.READY,
        policy_status=SkillLifecycleStatus.READY,
        smoke_test_status=SkillLifecycleStatus.PASSED,
        staging_probe_status=SkillLifecycleStatus.UNAVAILABLE,
        last_safe_summary="Calendar readiness uses deterministic evidence.",
        evidence_reference_id="evidence-qa032-calendar",
        remediation="No action needed.",
    )
    diagnostic = SkillExecutionDiagnosticSummary(
        diagnostic_id="diagnostic-qa032-calendar",
        skill_package_version="daily-briefing-connectors 1.4.0",
        tool_name="calendar.read",
        gateway_decision="allowed_read_only",
        side_effect_posture="read-only connector execution",
        outbound_policy_status=SkillLifecycleStatus.READY,
        credential_policy_status=SkillLifecycleStatus.READY,
        connector_readiness=SkillLifecycleStatus.READY,
        safe_attempt_summary="Deterministic gateway fixture verified readiness.",
        redaction_summary="Attempt details were summarized.",
        audit_reference_id="audit-gateway-diagnostic-qa032-calendar",
        remediation="No action needed.",
    )
    preview = BindingEligibilityPreview(
        preview_id="binding-preview-qa032",
        tenant_label="Acme",
        selected_context="Daily briefing workflow",
        eligible_tools=("calendar.read",),
        blocked_tools=("email.send",),
        policy_reasons=("Preview did not execute tools.",),
        remediation="No action needed.",
        audit_reference_id="audit-binding-preview-qa032",
    )

    assert credential.fingerprint == "fp_qa032_acme_briefing"
    assert connector.readiness == SkillLifecycleStatus.READY
    assert diagnostic.gateway_decision == "allowed_read_only"
    assert preview.blocked_tools == ("email.send",)

    with pytest.raises(ValidationError):
        SkillExecutionDiagnosticSummary(
            diagnostic_id="diagnostic-unsafe",
            skill_package_version="daily-briefing-connectors 1.4.0",
            tool_name="calendar.read",
            gateway_decision="allowed_read_only",
            side_effect_posture="read-only connector execution",
            outbound_policy_status=SkillLifecycleStatus.READY,
            credential_policy_status=SkillLifecycleStatus.READY,
            connector_readiness=SkillLifecycleStatus.READY,
            safe_attempt_summary="raw tool output rendered",
            redaction_summary="Attempt details were summarized.",
            audit_reference_id="audit-gateway-diagnostic-qa032-calendar",
            remediation="No action needed.",
        )


def test_skill_legacy_route_mapping_is_redaction_safe() -> None:
    mapping = SkillLegacyRouteMapping(
        legacy_path="/admin/skill-registry/ui/packages/{package_slug}",
        react_path="/admin/app/skills/packages/{package_slug}",
        compatibility_status="redirected",
        preserved_params=("package_slug", "query"),
        authorization_behavior="authenticated redirect with backend React denial",
        evidence=(
            "tests/integration/api/test_admin_skill_registry_legacy_redirects.py",
        ),
        notes="Legacy route redirects to React without rendering Jinja.",
    )

    assert mapping.compatibility_status == "redirected"
    assert "query" in mapping.preserved_params

    with pytest.raises(ValidationError):
        SkillLegacyRouteMapping(
            legacy_path="/admin/skill-registry/ui/packages",
            react_path="/admin/app/skills/packages",
            compatibility_status="redirected",
            authorization_behavior="raw tool output rendered",
            notes="Unsafe diagnostics.",
        )
