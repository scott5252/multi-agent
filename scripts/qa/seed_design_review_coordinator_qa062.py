from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowKind,
    WorkflowLineage,
    WorkflowLineageStatus,
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {
    "Content-Type": "application/json",
    "X-Local-Principal": "tenant-admin-acme",
}
EVIDENCE_PATH = Path(
    ".data/qa062-artifacts/evidence/qa062-design-review-coordinator-seed.json"
)


def main() -> int:
    workflow_version_bundle_id = _upsert_workflow_bundle()
    session_payload = _post_json(
        "/admin/design-reviews/sessions",
        {
            "tenant_id": str(ACME_TENANT_ID),
            "request_summary": "QA062 coordinator seeded design review.",
            "quorum_policy_key": "four_of_five_no_blockers",
            "workflow_version_bundle_id": str(workflow_version_bundle_id),
            "idempotency_key": "qa062-seeded-session",
        },
    )
    session_id = session_payload["design_review_session_id"]
    launch_payload = _post_json(
        f"/admin/design-reviews/sessions/{session_id}/coordinator/launch-round",
        {
            "tenant_id": str(ACME_TENANT_ID),
            "workflow_version_bundle_id": str(workflow_version_bundle_id),
            "reviewers": _reviewers(),
            "idempotency_key": "qa062-seeded-launch",
        },
    )
    round_id = launch_payload["round"]["design_review_round_id"]
    complete_payload = _post_json(
        f"/admin/design-reviews/rounds/{round_id}/coordinator/complete",
        {
            "tenant_id": str(ACME_TENANT_ID),
            "verdicts": _verdicts(),
            "safe_synthesis_summary": "QA062 council approves implementation handoff.",
            "idempotency_key": "qa062-seeded-complete",
        },
    )
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "qa_id": "qa062",
                "tenant_id": str(ACME_TENANT_ID),
                "workflow_version_bundle_id": str(workflow_version_bundle_id),
                "design_review_session_id": session_id,
                "design_review_round_id": round_id,
                "workflow_run_id": launch_payload["workflow_run_id"],
                "quorum_status": complete_payload["quorum_decision"]["status"],
                "handoff_state": complete_payload["handoff"]["state"]["kind"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA062 design review coordinator loop")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"design_review_session_id={session_id}")
    print(f"design_review_round_id={round_id}")
    print(f"evidence_path={EVIDENCE_PATH}")
    return 0


def _upsert_workflow_bundle() -> UUID:
    engine = create_engine(_database_url())
    workflow_version_bundle_id = UUID("62626262-6262-6262-6262-626262626262")
    with Session(engine) as session:
        _upsert_tenant(session)
        publisher = _upsert_principal(session)
        lineage = _upsert_lineage(session, publisher)
        draft = _upsert_draft(session, lineage, publisher)
        revision = _upsert_revision(session, draft, publisher)
        existing = session.scalar(
            select(WorkflowVersionBundle).where(
                WorkflowVersionBundle.workflow_version_bundle_id
                == workflow_version_bundle_id
            )
        )
        if existing is None:
            existing = WorkflowVersionBundle(
                workflow_version_bundle_id=workflow_version_bundle_id,
                workflow_lineage_id=lineage.workflow_lineage_id,
                scope_type="tenant",
                tenant_id=ACME_TENANT_ID,
                version_sequence=1,
                display_version="qa062-v1",
                status=WorkflowVersionStatus.PUBLISHED,
                published_from_draft_id=draft.workflow_draft_id,
                published_from_revision_id=revision.workflow_draft_revision_id,
                compiled_bundle_digest="6" * 64,
                compiler_version="qa062",
                published_by_principal_id=publisher.principal_identity_id,
            )
            session.add(existing)
        existing.workflow_lineage_id = lineage.workflow_lineage_id
        existing.scope_type = "tenant"
        existing.tenant_id = ACME_TENANT_ID
        existing.version_sequence = 1
        existing.display_version = "qa062-v1"
        existing.status = WorkflowVersionStatus.PUBLISHED
        existing.published_from_draft_id = draft.workflow_draft_id
        existing.published_from_revision_id = revision.workflow_draft_revision_id
        existing.compiled_bundle_digest = "6" * 64
        existing.compiler_version = "qa062"
        existing.published_by_principal_id = publisher.principal_identity_id
        existing.summary_json = {"document": _workflow_document()}
        session.flush()
        lineage.latest_published_version_id = existing.workflow_version_bundle_id
        session.commit()
    return workflow_version_bundle_id


def _upsert_tenant(session: Session) -> None:
    tenant = session.get(Tenant, ACME_TENANT_ID)
    if tenant is None:
        tenant = Tenant(tenant_id=ACME_TENANT_ID)
        session.add(tenant)
    tenant.slug = "acme"
    tenant.display_name = "Acme"
    tenant.status = TenantStatus.ACTIVE


def _upsert_principal(session: Session) -> PrincipalIdentity:
    principal = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == "local|qa062-publisher"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa062-publisher",
        )
        session.add(principal)
    principal.display_name = "QA062 Publisher"
    principal.email = "qa062.publisher@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_lineage(session: Session, publisher: PrincipalIdentity) -> WorkflowLineage:
    lineage = session.scalar(
        select(WorkflowLineage).where(
            WorkflowLineage.tenant_id == ACME_TENANT_ID,
            WorkflowLineage.slug == "qa062-design-review-coordinator",
        )
    )
    if lineage is None:
        lineage = WorkflowLineage(
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa062-design-review-coordinator",
            display_name="QA062 Design Review Coordinator",
            description="Persisted workflow bundle for QA062 coordinator evidence.",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=publisher.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.PUBLISHED
    session.flush()
    return lineage


def _upsert_draft(
    session: Session,
    lineage: WorkflowLineage,
    publisher: PrincipalIdentity,
) -> WorkflowDraft:
    draft = session.scalar(
        select(WorkflowDraft).where(
            WorkflowDraft.workflow_lineage_id == lineage.workflow_lineage_id
        )
    )
    if draft is None:
        draft = WorkflowDraft(
            workflow_lineage_id=lineage.workflow_lineage_id,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=publisher.principal_identity_id,
            last_edited_by_principal_id=publisher.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.PUBLISHED_SOURCE
    draft.current_revision_number = 1
    draft.last_edited_by_principal_id = publisher.principal_identity_id
    session.flush()
    return draft


def _upsert_revision(
    session: Session,
    draft: WorkflowDraft,
    publisher: PrincipalIdentity,
) -> WorkflowDraftRevision:
    revision = session.scalar(
        select(WorkflowDraftRevision).where(
            WorkflowDraftRevision.workflow_draft_id == draft.workflow_draft_id,
            WorkflowDraftRevision.revision_number == 1,
        )
    )
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_id=draft.workflow_draft_id,
            revision_number=1,
            authoring_document_json=_workflow_document(),
            document_sha256="6" * 64,
            change_summary="QA062 coordinator seed workflow revision.",
            created_by_principal_id=publisher.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = _workflow_document()
    revision.document_sha256 = "6" * 64
    revision.change_summary = "QA062 coordinator seed workflow revision."
    revision.created_by_principal_id = publisher.principal_identity_id
    session.flush()
    draft.latest_revision_id = revision.workflow_draft_revision_id
    return revision


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa062-design-review-council",
        "workflow_kind": "main_workflow",
        "entry_node_key": "lead",
        "roles": [
            {
                "role_key": "lead-role",
                "role_kind": "agent",
                "profile_reference_key": "qa062-profile-lead",
                "graph_node_keys": ["lead"],
            },
            {
                "role_key": "reviewer-role",
                "role_kind": "agent",
                "profile_reference_key": "qa062-profile-reviewer",
                "graph_node_keys": ["reviewer"],
            },
        ],
        "contracts": [
            {
                "contract_key": "handoff",
                "semantic_version": "1.0.0",
                "json_schema": {"type": "object"},
            }
        ],
        "nodes": [
            {
                "node_key": "lead",
                "node_type": "role",
                "display_name": "Lead",
                "role_key": "lead-role",
            },
            {
                "node_key": "reviewer",
                "node_type": "role",
                "display_name": "Reviewer",
                "role_key": "reviewer-role",
            },
            {
                "node_key": "terminal",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "lead-reviewer",
                "source_node_key": "lead",
                "target_node_key": "reviewer",
                "contract_key": "handoff",
            },
            {
                "edge_key": "reviewer-terminal",
                "source_node_key": "reviewer",
                "target_node_key": "terminal",
                "contract_key": "handoff",
            },
        ],
    }


def _reviewers() -> list[dict[str, object]]:
    return [
        {
            "reviewer_key": f"reviewer-{index}",
            "role_key": f"reviewer-role-{index}",
            "enabled": True,
        }
        for index in range(5)
    ]


def _verdicts() -> list[dict[str, object]]:
    return [
        {
            "reviewer_key": f"reviewer-{index}",
            "verdict": "approved" if index < 4 else "changes_requested",
            "score": 5 if index < 4 else 3,
            "blocking_issue_count": 0,
            "safe_feedback_summary": f"QA062 safe reviewer {index} feedback.",
            "output_digest": f"sha256-qa062-reviewer-{index}",
        }
        for index in range(5)
    ]


def _post_json(path: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
