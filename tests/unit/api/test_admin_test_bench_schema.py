from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_test_bench import (
    ArtifactReferenceSummary,
    AssertionDefinition,
    PublishGateEvidence,
    TestBenchStatus,
    TestRunLaunchRequest,
    TestSuiteSaveRequest,
    safe_test_bench_text,
)


def test_test_bench_text_rejects_unsafe_markers() -> None:
    assert safe_test_bench_text("Safe run summary") == "Safe run summary"

    for unsafe in (
        "qa033-secret-value",
        "raw prompt copied into UI",
        "raw completion copied into UI",
        "raw transcript copied into UI",
        "resolved credential copied into UI",
        "authorization header visible",
        "connector request body",
        "connector response body",
        "raw tool output rendered",
        "stack trace shown",
        "storage path leaked",
        "/Users/scott/artifact.json",
    ):
        with pytest.raises(ValueError):
            safe_test_bench_text(unsafe)


def test_suite_thresholds_are_normalized_and_safe() -> None:
    request = TestSuiteSaveRequest(
        name="Daily briefing release gate",
        target_type="workflow_draft",
        target_id="workflow-draft-qa033-daily-briefing",
        target_revision="workflow-draft-rev-qa033-current",
        default_safe_mode="mock_model_tools",
        pass_threshold=0.9,
        idempotency_key="suite-save",
    )

    assert request.pass_threshold == 0.9

    with pytest.raises(ValidationError):
        TestSuiteSaveRequest(
            name="Daily briefing release gate",
            target_type="workflow_draft",
            target_id="workflow-draft-qa033-daily-briefing",
            target_revision="workflow-draft-rev-qa033-current",
            default_safe_mode="mock_model_tools",
            pass_threshold=1.2,
            idempotency_key="suite-save",
        )


def test_run_launch_rejects_unsafe_mode_text() -> None:
    request = TestRunLaunchRequest(
        target_revision="workflow-draft-rev-qa033-current",
        safe_mode="mock_model_tools",
        idempotency_key="run-launch",
    )

    assert request.run_reason == "Release confidence"

    with pytest.raises(ValidationError):
        TestRunLaunchRequest(
            target_revision="workflow-draft-rev-qa033-current",
            safe_mode="raw transcript mode",
            idempotency_key="run-launch",
        )


def test_artifact_and_gate_payloads_are_reference_only() -> None:
    artifact = ArtifactReferenceSummary(
        artifact_reference_id="artifact-qa033-summary",
        label="Redacted run summary artifact",
        content_class="diagnostic_summary",
        checksum="sha256:qa033artifactsummary",
        size_label="18 KB",
        retention_state=TestBenchStatus.READY,
        redaction_class="safe-summary",
        access_status=TestBenchStatus.READY,
        safe_summary="Artifact metadata is available by governed reference only.",
        authorized_href="/admin/app/test-bench/artifacts/artifact-qa033-summary.json",
        audit_reference_id="audit-artifact-qa033-summary",
    )
    gate = PublishGateEvidence(
        gate_id="gate-qa033-passed",
        target_type="workflow_draft",
        target_label="Daily briefing draft",
        target_revision="workflow-draft-rev-qa033-current",
        required_suite_id="suite-qa033-daily-briefing",
        required_suite_label="Daily briefing release gate",
        evidence_status=TestBenchStatus.PASSED,
        latest_run_id="run-qa033-passing",
        latest_run_revision="workflow-draft-rev-qa033-current",
        latest_run_status=TestBenchStatus.PASSED,
        reason="Current target revision has passing evidence.",
        remediation="Publication can use this current evidence.",
        audit_reference_id="audit-gate-qa033-passed",
        artifact_references=(artifact,),
    )

    assert gate.artifact_references[0].authorized_href.endswith(".json")

    unavailable_artifact = ArtifactReferenceSummary(
        artifact_reference_id="artifact-qa043-unavailable",
        label="Unavailable redacted artifact metadata",
        content_class="diagnostic_summary",
        checksum="sha256:qa043unavailable",
        size_label="0 KB",
        retention_state=TestBenchStatus.ARTIFACT_UNAVAILABLE,
        redaction_class="safe-summary",
        access_status=TestBenchStatus.ARTIFACT_UNAVAILABLE,
        safe_summary="Artifact metadata is unavailable by governed reference.",
        authorized_href=None,
        audit_reference_id="audit-artifact-qa043-unavailable",
    )
    redaction_gate = PublishGateEvidence(
        gate_id="gate-qa043-redaction-unavailable",
        target_type="workflow_draft",
        target_label="Daily briefing draft",
        target_revision="workflow-draft-rev-qa033-current",
        required_suite_id="suite-qa033-daily-briefing",
        required_suite_label="Daily briefing release gate",
        evidence_status=TestBenchStatus.REDACTION_UNAVAILABLE,
        reason="Redaction evidence is unavailable.",
        remediation="Regenerate redaction evidence before publishing.",
        audit_reference_id="audit-gate-qa043-redaction",
        artifact_references=(unavailable_artifact,),
    )

    assert redaction_gate.evidence_status == "redaction_unavailable"
    assert redaction_gate.artifact_references[0].authorized_href is None

    with pytest.raises(ValidationError):
        ArtifactReferenceSummary(
            artifact_reference_id="artifact-unsafe",
            label="Artifact",
            content_class="diagnostic_summary",
            checksum="sha256:qa033artifactsummary",
            size_label="18 KB",
            retention_state=TestBenchStatus.READY,
            redaction_class="safe-summary",
            access_status=TestBenchStatus.READY,
            safe_summary="raw tool output rendered",
            authorized_href="/admin/app/test-bench/artifacts/artifact-unsafe.json",
            audit_reference_id="audit-artifact-qa033-summary",
        )


def test_assertion_definitions_are_backend_owned() -> None:
    assertion = AssertionDefinition(
        assertion_id="assertion-qa033-contract",
        label="Contract shape",
        kind="contract_shape",
        path_summary="response.summary.status",
        comparator="equals",
        expected_summary="Ready state summary",
        severity="blocking",
        threshold_weight=0.5,
        validation_status=TestBenchStatus.READY,
    )

    assert assertion.threshold_weight == 0.5

    with pytest.raises(ValidationError):
        AssertionDefinition(
            assertion_id="assertion-unsafe",
            label="Contract shape",
            kind="contract_shape",
            path_summary="response.summary.status",
            comparator="equals",
            expected_summary="raw completion copied into UI",
            severity="blocking",
            threshold_weight=0.5,
            validation_status=TestBenchStatus.READY,
        )
