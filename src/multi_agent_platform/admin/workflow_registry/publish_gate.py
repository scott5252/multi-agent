from __future__ import annotations

import json
from collections.abc import Iterable
from hashlib import sha256

from multi_agent_platform.admin.skill_registry.eligibility import (
    InstalledSkillEvidence,
    evaluate_binding_eligibility,
)
from multi_agent_platform.admin.workflow_registry.reference_validation import (
    pin_summary_from_snapshots,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    BuilderValidationFinding,
    PublishGateResponse,
    ReferenceReadinessSnapshot,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import ValidationResultResponse
from multi_agent_platform.testing.agent_bench.models import SuiteEvidenceSummary

PUBLISH_GATE_READY = "ready"
PUBLISH_GATE_BLOCKED = "blocked"
PUBLISH_GATE_STALE = "stale"
PUBLISH_GATE_UNAUTHORIZED = "unauthorized"
PUBLISH_GATE_RULE_SET_VERSION = "workflow-builder-publish-gate-0.1"


def required_test_summary_from_agent_bench(
    evidence: SuiteEvidenceSummary,
) -> RequiredTestSummary:
    return RequiredTestSummary(
        required_count=evidence.required_count,
        passing_count=evidence.passing_count,
        failing_count=evidence.failing_count,
        missing_count=evidence.missing_count,
        stale_count=evidence.stale_count,
    )


def validate_installed_skill_references(
    references: Iterable[InstalledSkillEvidence],
) -> list[BuilderValidationFinding]:
    findings: list[BuilderValidationFinding] = []
    for reference in references:
        decision = evaluate_binding_eligibility(reference)
        if not decision.allowed:
            findings.append(
                _gate_finding(
                    code="publish_gate.skill_registry.not_eligible",
                    message=(
                        "Installed skill reference is not eligible for workflow "
                        f"publish: {', '.join(decision.reason_codes)}."
                    ),
                )
            )
    return findings


def evaluate_publish_gate(
    *,
    workflow_draft_id: str,
    workflow_draft_revision_id: str,
    document_sha256: str,
    validation: ValidationResultResponse | None,
    reference_readiness: Iterable[ReferenceReadinessSnapshot],
    required_test_summary: RequiredTestSummary,
    current_validation_result_id: str | None = None,
    requested_validation_result_id: str | None = None,
    authorized: bool = True,
) -> PublishGateResponse:
    snapshots = list(reference_readiness)
    findings: list[BuilderValidationFinding] = []
    status = PUBLISH_GATE_READY
    validation_result_id = (
        requested_validation_result_id or str(validation.validation_result_id)
        if validation is not None
        else None
    )

    if not authorized:
        status = PUBLISH_GATE_UNAUTHORIZED
        findings.append(
            _gate_finding(
                code="publish_gate.unauthorized",
                message="Principal is not authorized to publish this workflow draft.",
            )
        )
    elif validation is None:
        status = PUBLISH_GATE_BLOCKED
        findings.append(
            _gate_finding(
                code="publish_gate.validation.missing",
                message="A current passing validation result is required.",
            )
        )
    elif (
        current_validation_result_id is not None
        and str(validation.validation_result_id) != current_validation_result_id
    ) or (
        requested_validation_result_id is not None
        and str(validation.validation_result_id) != requested_validation_result_id
    ):
        status = PUBLISH_GATE_STALE
        findings.append(
            _gate_finding(
                code="publish_gate.validation.stale",
                message="Validation result is stale for the current draft revision.",
            )
        )
    elif validation.status != "passed" or validation.blocking_issue_count > 0:
        status = PUBLISH_GATE_BLOCKED
        findings.extend(
            BuilderValidationFinding.model_validate(finding.model_dump(mode="json"))
            for finding in validation.findings
            if finding.blocking or finding.severity == "blocking"
        )
        findings.append(
            _gate_finding(
                code="publish_gate.validation.failed",
                message="Validation must pass before publication.",
            )
        )

    for snapshot in snapshots:
        if snapshot.blocking or snapshot.status not in {"ready", "active", "passed"}:
            status = PUBLISH_GATE_BLOCKED if status == PUBLISH_GATE_READY else status
            findings.append(
                BuilderValidationFinding(
                    category=snapshot.reference_type,
                    severity="blocking",
                    message=f"{snapshot.reference_type} reference is not ready.",
                    code=f"publish_gate.{snapshot.reference_type}.not_ready",
                    blocking=True,
                    reference_type=snapshot.reference_type,
                    reference_id=snapshot.reference_key,
                    remediation=(
                        "Resolve the reference readiness issue and rerun validation."
                    ),
                    safe_links=[snapshot.detail_url] if snapshot.detail_url else [],
                )
            )

    if (
        required_test_summary.required_count
        and required_test_summary.passing_count < required_test_summary.required_count
    ):
        status = PUBLISH_GATE_BLOCKED if status == PUBLISH_GATE_READY else status
        findings.append(
            _gate_finding(
                code="publish_gate.tests.not_passing",
                message=(
                    "Required workflow test evidence is missing, stale, or failing."
                ),
            )
        )

    pin_summary = pin_summary_from_snapshots(snapshots)
    digest = publish_gate_digest(
        workflow_draft_id=workflow_draft_id,
        workflow_draft_revision_id=workflow_draft_revision_id,
        document_sha256=document_sha256,
        validation_result_id=validation_result_id,
        status=status,
        pin_summary=pin_summary,
        required_test_summary=required_test_summary.model_dump(mode="json"),
    )
    gate_id = publish_gate_id(
        workflow_draft_id=workflow_draft_id,
        workflow_draft_revision_id=workflow_draft_revision_id,
        validation_result_id=validation_result_id,
        digest=digest,
    )
    blocking_count = sum(1 for finding in findings if finding.blocking)
    advisory_count = len(findings) - blocking_count
    return PublishGateResponse(
        publish_gate_id=gate_id,
        workflow_draft_id=workflow_draft_id,
        workflow_draft_revision_id=workflow_draft_revision_id,
        document_sha256=document_sha256,
        validation_result_id=validation_result_id,
        status=status,
        blocking_issue_count=blocking_count,
        advisory_issue_count=advisory_count,
        findings=findings,
        reference_readiness=snapshots,
        pin_summary=pin_summary,
        required_test_summary=required_test_summary,
        digest=digest,
    )


def publish_gate_digest(
    *,
    workflow_draft_id: str,
    workflow_draft_revision_id: str,
    document_sha256: str,
    validation_result_id: str | None,
    status: str,
    pin_summary: dict[str, object],
    required_test_summary: dict[str, object],
) -> str:
    payload = {
        "document_sha256": document_sha256,
        "pin_summary": pin_summary,
        "required_test_summary": required_test_summary,
        "rule_set_version": PUBLISH_GATE_RULE_SET_VERSION,
        "status": status,
        "validation_result_id": validation_result_id,
        "workflow_draft_id": workflow_draft_id,
        "workflow_draft_revision_id": workflow_draft_revision_id,
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def publish_gate_id(
    *,
    workflow_draft_id: str,
    workflow_draft_revision_id: str,
    validation_result_id: str | None,
    digest: str,
) -> str:
    raw = (
        f"{workflow_draft_id}:{workflow_draft_revision_id}:"
        f"{validation_result_id or 'none'}:{digest}"
    )
    return sha256(raw.encode("utf-8")).hexdigest()[:32]


def _gate_finding(*, code: str, message: str) -> BuilderValidationFinding:
    return BuilderValidationFinding(
        category="publish_gate",
        severity="blocking",
        message=message,
        field_path="validation",
        section_key="validation_publish",
        code=code,
        remediation="Rerun validation and resolve blocking readiness findings.",
        blocking=True,
    )
