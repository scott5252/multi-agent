from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_test_bench import (
    ArtifactReferenceSummary,
    AssertionDefinition,
    PublishGateEvidence,
    SafeExecutionModeOption,
    TargetRevisionBinding,
    safe_test_bench_text,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestBenchMutationResult as BenchMutationResult,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestBenchStatus as BenchStatus,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestCaseSaveRequest as CaseSaveRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestRunLaunchRequest as RunLaunchRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestRunSummary as RunSummary,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    TestSuiteSaveRequest as SuiteSaveRequest,
)


def test_test_bench_text_rejects_unsafe_markers() -> None:
    assert safe_test_bench_text("Safe run summary") == "Safe run summary"

    with pytest.raises(ValueError, match="local paths"):
        safe_test_bench_text("/tmp/unsafe-summary")

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
    request = SuiteSaveRequest(
        name="Daily briefing release gate",
        description=None,
        target_type="workflow_draft",
        target_id="workflow-draft-qa033-daily-briefing",
        target_revision="workflow-draft-rev-qa033-current",
        default_safe_mode="mock_model_tools",
        pass_threshold=0.9,
        revision=None,
        idempotency_key="suite-save",
    )

    assert request.pass_threshold == 0.9

    with pytest.raises(ValidationError):
        SuiteSaveRequest(
            name="Daily briefing release gate",
            target_type="workflow_draft",
            target_id="workflow-draft-qa033-daily-briefing",
            target_revision="workflow-draft-rev-qa033-current",
            default_safe_mode="mock_model_tools",
            pass_threshold=1.2,
            idempotency_key="suite-save",
        )


def test_run_launch_rejects_unsafe_mode_text() -> None:
    request = RunLaunchRequest(
        target_revision="workflow-draft-rev-qa033-current",
        safe_mode="mock_model_tools",
        idempotency_key="run-launch",
    )

    assert request.run_reason == "Release confidence"

    with pytest.raises(ValidationError):
        RunLaunchRequest(
            target_revision="workflow-draft-rev-qa033-current",
            safe_mode="raw transcript mode",
            idempotency_key="run-launch",
        )


def test_optional_schema_fields_accept_absent_live_metadata() -> None:
    target = TargetRevisionBinding(
        target_type="workflow_draft",
        target_id="workflow-draft-qa053",
        target_label="Workflow Draft Qa053",
        current_revision="workflow-draft-rev-current",
        selected_revision="workflow-draft-rev-current",
        revision_status=BenchStatus.READY,
        stale_reason=None,
        remediation="Rerun before publishing.",
    )
    mode = SafeExecutionModeOption(
        mode_id="mock_model",
        label="Mock model",
        side_effect_posture="No external side effects",
        model_behavior="Deterministic model response",
        tool_behavior="No tool calls",
        credential_behavior="No credential resolution",
        allowed_status=BenchStatus.READY,
        policy_reason="Local QA mode.",
        approval_reference_id=None,
        audit_reference_id=None,
    )
    run = RunSummary(
        run_id="run-qa053",
        suite_id="suite-qa053",
        suite_name="QA053 suite",
        target_revision="workflow-draft-rev-current",
        safe_mode="mock_model",
        status=BenchStatus.PASSED,
        pass_rate=1.0,
        failure_category=None,
        started_label="2026-05-07 16:00 UTC",
        finished_label=None,
        actor_label="tenant-admin",
        case_total=1,
        case_passed=1,
        case_failed=0,
        usage_summary="0 total tokens",
        latency_summary="0 ms total",
        audit_reference_id="audit-run-qa053",
    )
    mutation = BenchMutationResult(
        status="accepted",
        summary="Accepted",
        revision=None,
        audit_reference_id=None,
    )
    case = CaseSaveRequest(
        name="QA053 case",
        fixture_summary="Safe fixture summary.",
        expected_contract_summary="Safe expected summary.",
        evaluator_reference_id=None,
        revision=None,
        idempotency_key="case-qa053",
    )

    assert target.stale_reason is None
    assert mode.approval_reference_id is None
    assert run.finished_label is None
    assert mutation.revision is None
    assert case.revision is None


def test_artifact_and_gate_payloads_are_reference_only() -> None:
    artifact = ArtifactReferenceSummary(
        artifact_reference_id="artifact-qa033-summary",
        label="Redacted run summary artifact",
        content_class="diagnostic_summary",
        checksum="sha256:qa033artifactsummary",
        size_label="18 KB",
        retention_state=BenchStatus.READY,
        redaction_class="safe-summary",
        access_status=BenchStatus.READY,
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
        evidence_status=BenchStatus.PASSED,
        latest_run_id="run-qa033-passing",
        latest_run_revision="workflow-draft-rev-qa033-current",
        latest_run_status=BenchStatus.PASSED,
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
        retention_state=BenchStatus.ARTIFACT_UNAVAILABLE,
        redaction_class="safe-summary",
        access_status=BenchStatus.ARTIFACT_UNAVAILABLE,
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
        evidence_status=BenchStatus.REDACTION_UNAVAILABLE,
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
            retention_state=BenchStatus.READY,
            redaction_class="safe-summary",
            access_status=BenchStatus.READY,
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
        validation_status=BenchStatus.READY,
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
            validation_status=BenchStatus.READY,
        )
