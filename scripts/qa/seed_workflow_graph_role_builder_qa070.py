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
QA070_LINEAGE_ID = UUID("70707070-1111-4670-8670-000000000070")
QA070_DRAFT_ID = UUID("70707070-6669-4670-8670-000000000070")
QA070_REVISION_ID = UUID("70707070-3333-4670-8670-000000000070")
SAVE_PAYLOAD_PATH = Path(".data/qa070-artifacts/workflow-graph-role-save.json")


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
                "idempotency_key": "qa070-workflow-graph-role-save",
                "name": "QA070 Graph Role Builder Updated",
                "description": "Saved through deterministic QA070 graph UI.",
                "change_summary": "QA070 graph role builder save",
                "client_context": {
                    "active_section": "workflow-graph-role-builder",
                    "form_version": "workflow-graph-role-builder.v1",
                },
                "selected_prompt_ref": None,
                "selected_profile_ref": None,
                "join_policy": "evidence-join",
                "force_stale": False,
                "document": {
                    **document,
                    "display_name": "QA070 Graph Role Builder Updated",
                    "description": "Saved through deterministic QA070 graph UI.",
                    "editor_annotations": {
                        **document["editor_annotations"],
                        "section_notes": {
                            "roles": "QA070 graph role builder save payload."
                        },
                    },
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA070 workflow graph role builder draft")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={QA070_DRAFT_ID}")
    print(f"save_payload={SAVE_PAYLOAD_PATH}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if value is None:
        value = _env_file_value("DATABASE_URL")
    if value is None:
        raise RuntimeError("DATABASE_URL is required for QA070 seed")
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
            PrincipalIdentity.external_subject == "local|qa070-builder"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa070-builder",
        )
        session.add(principal)
    principal.display_name = "QA070 Builder"
    principal.email = "qa070.builder@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_workflow(
    session: Session,
    principal: PrincipalIdentity,
    document: dict[str, object],
) -> None:
    lineage = session.get(WorkflowLineage, QA070_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA070_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa070-graph-role-builder",
            display_name="QA070 Graph Role Builder",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.DRAFTING
    lineage.description = "Seed draft for graph and role builder QA."

    draft = session.get(WorkflowDraft, QA070_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA070_DRAFT_ID,
            workflow_lineage_id=QA070_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=principal.principal_identity_id,
            last_edited_by_principal_id=principal.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1

    revision = session.get(WorkflowDraftRevision, QA070_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA070_REVISION_ID,
            workflow_draft_id=QA070_DRAFT_ID,
            revision_number=1,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = document
    revision.document_sha256 = _digest(document)
    revision.change_summary = "QA070 seed workflow graph document."
    revision.created_at = datetime.now(UTC)
    session.flush()
    draft.latest_revision_id = QA070_REVISION_ID


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa070-graph-role-builder",
        "display_name": "QA070 Graph Role Builder",
        "description": "Seed draft for graph and role builder QA.",
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
            {
                "contract_key": "approval-decision",
                "contract_kind": "approval_decision",
                "display_name": "Approval decision",
                "json_schema": {"type": "object"},
            },
        ],
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "purpose": "Coordinate deterministic QA070 workflow setup.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["start"],
            },
            {
                "role_key": "research",
                "display_name": "Research agent",
                "purpose": "Gather safe research context.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["research"],
            },
            {
                "role_key": "review",
                "display_name": "Review agent",
                "purpose": "Review branch output before the join.",
                "input_contract_key": "request",
                "output_contract_key": "result",
                "graph_node_keys": ["review"],
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
                "node_key": "research",
                "node_type": "role",
                "display_name": "Research agent",
                "role_key": "research",
            },
            {
                "node_key": "review",
                "node_type": "role",
                "display_name": "Review agent",
                "role_key": "review",
            },
            {
                "node_key": "join",
                "node_type": "join",
                "display_name": "Evidence join",
                "join_policy_key": "evidence-join",
            },
            {
                "node_key": "approval",
                "node_type": "approval",
                "display_name": "Manager approval",
                "approval_gate_key": "manager-approval",
            },
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "edge-start-research",
                "source_node_key": "start",
                "target_node_key": "research",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-start-review",
                "source_node_key": "start",
                "target_node_key": "review",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-research-join",
                "source_node_key": "research",
                "target_node_key": "join",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-review-join",
                "source_node_key": "review",
                "target_node_key": "join",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-join-approval",
                "source_node_key": "join",
                "target_node_key": "approval",
                "edge_type": "success",
            },
            {
                "edge_key": "edge-approval-done",
                "source_node_key": "approval",
                "target_node_key": "done",
                "edge_type": "success",
            },
        ],
        "join_policies": [
            {
                "join_policy_key": "evidence-join",
                "strategy": "quorum",
                "inbound_edge_keys": ["edge-research-join", "edge-review-join"],
                "required_branches": ["research", "review"],
                "quorum_count": 2,
                "timeout_seconds": 300,
                "failure_behavior": "block",
                "output_merge_contract_key": "result",
            }
        ],
        "approval_gates": [
            {
                "approval_gate_key": "manager-approval",
                "display_name": "Manager approval",
                "approver_scope": "tenant_admin",
                "decision_contract_key": "approval-decision",
                "resume_behavior": "continue",
            }
        ],
        "subworkflow_refs": [],
        "test_requirements": [],
        "editor_annotations": {
            "section_notes": {},
            "graph_layout": {
                "approval": {"x": 720, "y": 80},
                "done": {"x": 960, "y": 80},
                "join": {"x": 500, "y": 80},
                "research": {"x": 240, "y": 0},
                "review": {"x": 240, "y": 160},
                "start": {"x": 0, "y": 80},
            },
            "collapsed_sections": [],
        },
    }


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
