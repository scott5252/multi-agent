#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
)
from multi_agent_platform.db.models.agent_tests import (
    AgentTestAssertion,
    AgentTestAssertionKind,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestRunStep,
    AgentTestSafeMode,
    AgentTestStatus,
    AgentTestSuite,
    AgentTestTargetType,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.workflow_registry import (
    ValidationResult,
    ValidationResultStatus,
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowKind,
    WorkflowLineage,
    WorkflowLineageStatus,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA072_LINEAGE_ID = UUID("72727272-1111-4672-8672-000000000072")
QA072_DRAFT_ID = UUID("72727272-6669-4672-8672-000000000072")
QA072_REVISION_ID = UUID("72727272-3333-4672-8672-000000000072")
QA072_VALIDATION_ID = UUID("72727272-3334-4672-8672-000000000072")

QA072_SUITE_CURRENT_ID = UUID("72727272-4000-4672-8672-000000000072")
QA072_CASE_CURRENT_ID = UUID("72727272-4001-4672-8672-000000000072")
QA072_ASSERTION_CURRENT_ID = UUID("72727272-4002-4672-8672-000000000072")
QA072_RUN_CURRENT_ID = UUID("72727272-4003-4672-8672-000000000072")
QA072_REQUIREMENT_CURRENT_ID = UUID("72727272-4004-4672-8672-000000000072")
QA072_STEP_CURRENT_ID = UUID("72727272-4005-4672-8672-000000000072")

QA072_SUITE_STALE_ID = UUID("72727272-4100-4672-8672-000000000072")
QA072_CASE_STALE_ID = UUID("72727272-4101-4672-8672-000000000072")
QA072_ASSERTION_STALE_ID = UUID("72727272-4102-4672-8672-000000000072")
QA072_RUN_STALE_ID = UUID("72727272-4103-4672-8672-000000000072")
QA072_REQUIREMENT_STALE_ID = UUID("72727272-4104-4672-8672-000000000072")
QA072_STEP_STALE_ID = UUID("72727272-4105-4672-8672-000000000072")

QA072_SUITE_FAILED_ID = UUID("72727272-4200-4672-8672-000000000072")
QA072_CASE_FAILED_ID = UUID("72727272-4201-4672-8672-000000000072")
QA072_ASSERTION_FAILED_ID = UUID("72727272-4202-4672-8672-000000000072")
QA072_RUN_FAILED_ID = UUID("72727272-4203-4672-8672-000000000072")
QA072_REQUIREMENT_FAILED_ID = UUID("72727272-4204-4672-8672-000000000072")
QA072_STEP_FAILED_ID = UUID("72727272-4205-4672-8672-000000000072")

SAVE_PAYLOAD_PATH = Path(".data/qa072-artifacts/workflow-test-evidence-save.json")


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime.now(UTC)
    document = _workflow_document()
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        principal = _upsert_principal(session)
        actor_id = str(principal.principal_identity_id)
        _upsert_workflow(session, principal, document, now=now)
        _upsert_validation(session, principal, now=now)
        _upsert_suite_bundle(
            session,
            actor_id=actor_id,
            suite_id=QA072_SUITE_CURRENT_ID,
            case_id=QA072_CASE_CURRENT_ID,
            assertion_id=QA072_ASSERTION_CURRENT_ID,
            run_id=QA072_RUN_CURRENT_ID,
            requirement_id=QA072_REQUIREMENT_CURRENT_ID,
            step_id=QA072_STEP_CURRENT_ID,
            name="QA072 Current Required Evidence",
            case_name="Current revision smoke",
            run_status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            target_version=str(QA072_REVISION_ID),
            now=now,
        )
        _upsert_suite_bundle(
            session,
            actor_id=actor_id,
            suite_id=QA072_SUITE_STALE_ID,
            case_id=QA072_CASE_STALE_ID,
            assertion_id=QA072_ASSERTION_STALE_ID,
            run_id=QA072_RUN_STALE_ID,
            requirement_id=QA072_REQUIREMENT_STALE_ID,
            step_id=QA072_STEP_STALE_ID,
            name="QA072 Stale Evidence",
            case_name="Older revision smoke",
            run_status=AgentTestRunStatus.PASSED,
            pass_status="passed",
            target_version="qa072-older-revision",
            now=now - timedelta(minutes=5),
        )
        _upsert_suite_bundle(
            session,
            actor_id=actor_id,
            suite_id=QA072_SUITE_FAILED_ID,
            case_id=QA072_CASE_FAILED_ID,
            assertion_id=QA072_ASSERTION_FAILED_ID,
            run_id=QA072_RUN_FAILED_ID,
            requirement_id=QA072_REQUIREMENT_FAILED_ID,
            step_id=QA072_STEP_FAILED_ID,
            name="QA072 Failed Evidence",
            case_name="Failed revision smoke",
            run_status=AgentTestRunStatus.FAILED,
            pass_status="failed",
            target_version=str(QA072_REVISION_ID),
            now=now - timedelta(minutes=2),
        )
        session.commit()

    _write_save_payload(document)
    print("Seeded QA072 workflow test evidence and publish setup")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={QA072_DRAFT_ID}")
    print(f"workflow_revision_id={QA072_REVISION_ID}")
    print(f"current_suite_id={QA072_SUITE_CURRENT_ID}")
    print(f"current_run_id={QA072_RUN_CURRENT_ID}")
    print(f"stale_suite_id={QA072_SUITE_STALE_ID}")
    print(f"failed_suite_id={QA072_SUITE_FAILED_ID}")
    print(f"save_payload={SAVE_PAYLOAD_PATH}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if value is None:
        value = _env_file_value("DATABASE_URL")
    if value is None:
        raise RuntimeError("DATABASE_URL is required for QA072 seed")
    return value.replace("sqlite+aiosqlite://", "sqlite://", 1)


def _env_file_value(key: str) -> str | None:
    env_path = Path(".env")
    if not env_path.exists():
        return None
    prefix = f"{key}="
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _upsert_tenant(
    session: Session,
    tenant_id: UUID,
    slug: str,
    display_name: str,
) -> None:
    tenant = session.get(Tenant, tenant_id)
    if tenant is None:
        tenant = Tenant(tenant_id=tenant_id)
        session.add(tenant)
    tenant.slug = slug
    tenant.display_name = display_name
    tenant.status = TenantStatus.ACTIVE


def _upsert_principal(session: Session) -> PrincipalIdentity:
    principal = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == "local|qa072-evidence"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa072-evidence",
        )
        session.add(principal)
    principal.display_name = "QA072 Evidence Admin"
    principal.email = "qa072.evidence@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_workflow(
    session: Session,
    principal: PrincipalIdentity,
    document: dict[str, object],
    *,
    now: datetime,
) -> None:
    lineage = session.get(WorkflowLineage, QA072_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA072_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa072-workflow-test-evidence",
            display_name="QA072 Workflow Test Evidence",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.DRAFTING
    lineage.description = "Seed draft for workflow test evidence QA."

    draft = session.get(WorkflowDraft, QA072_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA072_DRAFT_ID,
            workflow_lineage_id=QA072_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=principal.principal_identity_id,
            last_edited_by_principal_id=principal.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1
    draft.last_edited_by_principal_id = principal.principal_identity_id

    revision = session.get(WorkflowDraftRevision, QA072_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA072_REVISION_ID,
            workflow_draft_id=QA072_DRAFT_ID,
            revision_number=1,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = document
    revision.document_sha256 = _digest(document)
    revision.change_summary = "QA072 seed workflow with current required evidence."
    revision.react_save_idempotency_key = None
    revision.react_save_scope_hash = None
    revision.react_save_payload_hash = None
    revision.created_at = now
    session.flush()
    draft.latest_revision_id = QA072_REVISION_ID


def _upsert_validation(
    session: Session,
    principal: PrincipalIdentity,
    *,
    now: datetime,
) -> None:
    validation = session.get(ValidationResult, QA072_VALIDATION_ID)
    if validation is None:
        validation = ValidationResult(validation_result_id=QA072_VALIDATION_ID)
        session.add(validation)
    validation.workflow_draft_revision_id = QA072_REVISION_ID
    validation.rule_set_version = "qa072-seed-validation"
    validation.status = ValidationResultStatus.PASSED
    validation.blocking_issue_count = 0
    validation.advisory_issue_count = 0
    validation.findings_json = {
        "findings": [],
        "graph_summary": {"nodes": 4, "edges": 3, "status": "ready"},
        "publish_blocking": False,
        "reference_readiness": [
            {
                "reference_type": "test_suite",
                "reference_key": "daily-briefing-required-suite",
                "status": "passed",
                "blocking": False,
                "safe_summary": (
                    "Required test evidence is passing for the current "
                    "workflow revision."
                ),
                "pin_payload": {
                    "suite_id": str(QA072_SUITE_CURRENT_ID),
                    "run_id": str(QA072_RUN_CURRENT_ID),
                    "target_type": "workflow_draft",
                    "target_id": str(QA072_DRAFT_ID),
                    "target_version": str(QA072_REVISION_ID),
                },
            }
        ],
        "required_test_summary": {
            "required_count": 1,
            "passing_count": 1,
            "failing_count": 0,
            "missing_count": 0,
            "stale_count": 0,
        },
        "rule_set_version": "qa072-seed-validation",
    }
    validation.report_artifact_id = None
    validation.executed_by_principal_id = principal.principal_identity_id
    validation.executed_at = now


def _upsert_suite_bundle(
    session: Session,
    *,
    actor_id: str,
    suite_id: UUID,
    case_id: UUID,
    assertion_id: UUID,
    run_id: UUID,
    requirement_id: UUID,
    step_id: UUID,
    name: str,
    case_name: str,
    run_status: AgentTestRunStatus,
    pass_status: str,
    target_version: str,
    now: datetime,
) -> None:
    suite = session.get(AgentTestSuite, suite_id)
    if suite is None:
        suite = AgentTestSuite(agent_test_suite_id=suite_id)
        session.add(suite)
    suite.tenant_id = ACME_TENANT_ID
    suite.name = name
    suite.description = "Repository-backed workflow publish evidence."
    suite.target_type = AgentTestTargetType.WORKFLOW_DRAFT
    suite.target_id = str(QA072_DRAFT_ID)
    suite.target_version = target_version
    suite.default_safe_mode = AgentTestSafeMode.MOCK_MODEL
    suite.model_mode = "mock"
    suite.tool_mode = "mock"
    suite.pass_threshold = 1.0
    suite.is_required_for_publish = True
    suite.status = AgentTestStatus.ACTIVE
    suite.revision = 1
    suite.created_by_principal_id = actor_id
    suite.archived_at = None

    test_case = session.get(AgentTestCase, case_id)
    if test_case is None:
        test_case = AgentTestCase(agent_test_case_id=case_id)
        session.add(test_case)
    test_case.agent_test_suite_id = suite_id
    test_case.tenant_id = ACME_TENANT_ID
    test_case.name = case_name
    test_case.description = "Safe deterministic workflow case."
    test_case.fixture_summary = {
        "fixture": "safe workflow input",
        "tenant": "acme",
    }
    test_case.expected_contract_shape = {"status": "passed"}
    test_case.model_mode = "inherit"
    test_case.tool_mode = "inherit"
    test_case.evaluator_prompt_ref = None
    test_case.pass_threshold = 1.0
    test_case.case_order = 0
    test_case.status = AgentTestStatus.ACTIVE
    test_case.revision = 1
    test_case.archived_at = None

    assertion = session.get(AgentTestAssertion, assertion_id)
    if assertion is None:
        assertion = AgentTestAssertion(agent_test_assertion_id=assertion_id)
        session.add(assertion)
    assertion.agent_test_case_id = case_id
    assertion.tenant_id = ACME_TENANT_ID
    assertion.kind = AgentTestAssertionKind.DETERMINISTIC
    assertion.path = "status"
    assertion.comparator = "equals"
    assertion.expected_value = "passed"
    assertion.expected_schema = {}
    assertion.threshold = None
    assertion.severity = "blocking"
    assertion.weight = 1.0
    assertion.description = "Workflow output status must pass."

    run = session.get(AgentTestRun, run_id)
    if run is None:
        run = AgentTestRun(agent_test_run_id=run_id)
        session.add(run)
    run.tenant_id = ACME_TENANT_ID
    run.agent_test_suite_id = suite_id
    run.target_type = AgentTestTargetType.WORKFLOW_DRAFT
    run.target_id = str(QA072_DRAFT_ID)
    run.target_version = target_version
    run.safe_mode = AgentTestSafeMode.MOCK_MODEL
    run.status = run_status
    run.pass_status = pass_status
    run.triggered_by_principal_id = actor_id
    run.idempotency_key = f"qa072-{suite_id}-run"
    run.trace_id = f"qa072-trace-{run_id.hex[:8]}"
    run.started_at = now
    run.completed_at = now + timedelta(seconds=2)
    run.usage_summary = {"mode": "mock_model", "token_count": 0}
    run.latency_ms = 24
    run.redaction_summary = {
        "redacted_fields": [],
        "classification": "safe_summary_only",
    }
    run.artifact_summary = {"artifact_count": 0, "storage": "metadata-only"}
    run.blocked_side_effect_count = 0
    run.failure_summary = (
        "Safe deterministic assertion did not pass."
        if run_status is AgentTestRunStatus.FAILED
        else None
    )
    run.created_at = now

    step = session.get(AgentTestRunStep, step_id)
    if step is None:
        step = AgentTestRunStep(agent_test_run_step_id=step_id)
        session.add(step)
    step.agent_test_run_id = run_id
    step.tenant_id = ACME_TENANT_ID
    step.agent_test_case_id = case_id
    step.step_name = case_name
    step.status = run_status
    step.sequence = 1
    step.model_provider = "mock"
    step.model_id = "mock-model"
    step.prompt_version_id = None
    step.profile_version_id = None
    step.skill_version_refs = []
    step.workflow_version_ref = target_version
    step.latency_ms = 24
    step.token_usage = {"total_tokens": 0}
    step.contract_validation = {"status": pass_status}
    step.assertion_results = [
        {
            "assertion_id": str(assertion_id),
            "status": pass_status,
            "safe_summary": "Deterministic assertion evaluated safely.",
        }
    ]
    step.blocked_side_effects = []
    step.redacted_transcript = {"summary": "Safe deterministic run summary."}
    step.artifact_refs = []
    step.failure_reason = run.failure_summary
    step.created_at = now

    requirement = session.get(AgentTestPublicationRequirement, requirement_id)
    if requirement is None:
        requirement = AgentTestPublicationRequirement(
            agent_test_publication_requirement_id=requirement_id
        )
        session.add(requirement)
    requirement.tenant_id = ACME_TENANT_ID
    requirement.target_type = AgentTestTargetType.WORKFLOW_DRAFT
    requirement.target_id = str(QA072_DRAFT_ID)
    requirement.agent_test_suite_id = suite_id
    requirement.required = True
    requirement.minimum_pass_status = "passed"
    requirement.created_by_principal_id = actor_id
    requirement.archived_at = None


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa072-workflow-test-evidence",
        "display_name": "QA072 Workflow Test Evidence",
        "description": "Seed draft for workflow evidence setup QA.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "start",
        "contracts": [
            {
                "contract_key": "request",
                "contract_kind": "workflow_input",
                "display_name": "Request",
                "json_schema": {"type": "object"},
            },
            {
                "contract_key": "result",
                "contract_kind": "workflow_output",
                "display_name": "Result",
                "json_schema": {"type": "object"},
            },
        ],
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "purpose": "Coordinate deterministic QA072 workflow evidence.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["start"],
                "prompt_reference_keys": [],
                "profile_reference_key": None,
            },
            {
                "role_key": "evidence",
                "display_name": "Evidence runner",
                "purpose": "Prepare safe deterministic test evidence.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["evidence"],
                "prompt_reference_keys": [],
                "profile_reference_key": None,
            },
        ],
        "prompt_profile_references": [],
        "skill_installations": [],
        "nodes": [
            {
                "node_key": "start",
                "node_type": "role",
                "display_name": "Coordinator",
                "role_key": "coordinator",
            },
            {
                "node_key": "evidence",
                "node_type": "role",
                "display_name": "Evidence runner",
                "role_key": "evidence",
            },
            {
                "node_key": "review",
                "node_type": "approval",
                "display_name": "Evidence review",
                "approval_gate_key": "evidence-review",
            },
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "edge-start-evidence",
                "source_node_key": "start",
                "target_node_key": "evidence",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-evidence-review",
                "source_node_key": "evidence",
                "target_node_key": "review",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-review-done",
                "source_node_key": "review",
                "target_node_key": "done",
                "edge_type": "approved",
            },
        ],
        "join_policies": [],
        "approval_gates": [
            {
                "approval_gate_key": "evidence-review",
                "display_name": "Evidence review",
                "approver_scope": "tenant",
                "approver_role_code": "tenant_admin",
                "reason": "Review safe evidence summaries before publish.",
            }
        ],
        "subworkflow_refs": [],
        "test_requirements": [
            {
                "requirement_key": "daily-briefing-required-suite",
                "suite_id": str(QA072_SUITE_CURRENT_ID),
                "target_type": "workflow_draft",
                "freshness_policy": "latest_revision",
                "latest_result_id": str(QA072_RUN_CURRENT_ID),
                "latest_result_status": "passed",
                "executed_at": "2026-05-09T19:30:00Z",
                "safe_summary": (
                    "Required deterministic evidence is passing for the "
                    "current workflow revision."
                ),
            }
        ],
        "editor_annotations": {
            "section_notes": {
                "test-evidence": "QA072 current, stale, and failed evidence seeded."
            },
            "graph_layout": {
                "start": {"x": 0, "y": 120},
                "evidence": {"x": 260, "y": 120},
                "review": {"x": 520, "y": 120},
                "done": {"x": 780, "y": 120},
            },
            "collapsed_sections": [],
        },
    }


def _write_save_payload(document: dict[str, object]) -> None:
    SAVE_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PAYLOAD_PATH.write_text(
        json.dumps(
            {
                "revision": "1",
                "idempotency_key": "qa072-workflow-test-evidence-save",
                "name": "QA072 Workflow Test Evidence",
                "description": "Saved through deterministic QA072 evidence UI.",
                "change_summary": "QA072 evidence save",
                "client_context": {
                    "active_section": "workflow-test-evidence",
                    "form_version": "workflow-test-evidence.v1",
                },
                "selected_prompt_ref": None,
                "selected_profile_ref": None,
                "join_policy": "wait_for_required_branches",
                "force_stale": False,
                "document": document,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
