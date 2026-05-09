#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
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
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA069_LINEAGE_ID = UUID("69696969-1111-4669-8669-000000000069")
QA069_DRAFT_ID = UUID("69696969-6669-4669-8669-000000000069")
QA069_REVISION_ID = UUID("69696969-3333-4669-8669-000000000069")
SAVE_PAYLOAD_PATH = Path(".data/qa069-artifacts/workflow-document-save.json")


def main() -> int:
    engine = create_engine(_database_url())
    document = _workflow_document()
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        principal = _upsert_principal(session)
        _upsert_workflow(session, principal, document)
        session.commit()

    SAVE_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PAYLOAD_PATH.write_text(
        json.dumps(
            {
                "revision": "1",
                "idempotency_key": "qa069-workflow-document-save",
                "name": "QA069 Workflow Document Updated",
                "description": "Saved through deterministic QA069 full document API.",
                "change_summary": "QA069 full document save",
                "client_context": {"active_section": "metadata"},
                "selected_prompt_ref": None,
                "selected_profile_ref": None,
                "join_policy": "wait_for_required_branches",
                "force_stale": False,
                "document": {
                    **document,
                    "display_name": "QA069 Workflow Document Updated",
                    "description": (
                        "Saved through deterministic QA069 full document API."
                    ),
                    "editor_annotations": {
                        **document["editor_annotations"],
                        "section_notes": {
                            "metadata": "QA069 full document save payload."
                        },
                    },
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA069 workflow document authoring draft")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={QA069_DRAFT_ID}")
    print(f"save_payload={SAVE_PAYLOAD_PATH}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if value is None:
        value = _env_file_value("DATABASE_URL")
    if value is None:
        raise RuntimeError("DATABASE_URL is required for QA069 seed")
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
            PrincipalIdentity.external_subject == "local|qa069-publisher"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa069-publisher",
        )
        session.add(principal)
    principal.display_name = "QA069 Publisher"
    principal.email = "qa069.publisher@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_workflow(
    session: Session,
    principal: PrincipalIdentity,
    document: dict[str, object],
) -> None:
    lineage = session.get(WorkflowLineage, QA069_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA069_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa069-workflow-document-authoring",
            display_name="QA069 Workflow Document Authoring",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.DRAFTING
    lineage.description = "Seed draft for full workflow document authoring QA."

    draft = session.get(WorkflowDraft, QA069_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA069_DRAFT_ID,
            workflow_lineage_id=QA069_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=principal.principal_identity_id,
            last_edited_by_principal_id=principal.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1

    revision = session.get(WorkflowDraftRevision, QA069_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA069_REVISION_ID,
            workflow_draft_id=QA069_DRAFT_ID,
            revision_number=1,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = document
    revision.document_sha256 = _digest(document)
    revision.change_summary = "QA069 seed workflow document."
    revision.created_at = datetime.now(UTC)
    session.flush()
    draft.latest_revision_id = QA069_REVISION_ID


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa069-workflow-document-authoring",
        "display_name": "QA069 Workflow Document Authoring",
        "description": "Seed draft for full workflow document authoring QA.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "start",
        "contracts": [
            {"contract_key": "request", "json_schema": {"type": "object"}},
            {"contract_key": "result", "json_schema": {"type": "object"}},
        ],
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "purpose": "Coordinate deterministic QA069 workflow setup.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["start"],
                "skill_bindings": [
                    {
                        "binding_key": "coordinator-review",
                        "skill_slug": "coordinator-review",
                        "skill_version": "2026.05.0",
                        "purpose": "Review full document save behavior.",
                    }
                ],
            }
        ],
        "prompt_profile_references": [],
        "skill_installations": [],
        "nodes": [
            {
                "node_key": "start",
                "node_type": "role",
                "display_name": "Start",
                "role_key": "coordinator",
            },
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "edge-start-done",
                "source_node_key": "start",
                "target_node_key": "done",
                "edge_type": "success",
            }
        ],
        "join_policies": [],
        "approval_gates": [],
        "subworkflow_refs": [],
        "test_requirements": [],
        "editor_annotations": {
            "section_notes": {},
            "graph_layout": {},
            "collapsed_sections": [],
        },
    }


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
