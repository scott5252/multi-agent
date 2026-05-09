#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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
QA066_DRAFT_ID = UUID("66666666-1111-4666-8666-000000000066")
QA066_LINEAGE_ID = UUID("66666666-2222-4666-8666-000000000066")
QA066_REVISION_ID = UUID("66666666-3333-4666-8666-000000000066")
QA066_VERSION_ID = UUID("66666666-4444-4666-8666-000000000066")
EVIDENCE_PATH = Path(".data/qa066-artifacts/evidence/qa066-agent-graph-seed.json")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        _upsert_tenant(session)
        publisher = _upsert_principal(session)
        lineage = _upsert_lineage(session, publisher)
        draft = _upsert_draft(session, lineage, publisher)
        revision = _upsert_revision(session, draft, publisher)
        version = _upsert_version(session, lineage, draft, revision, publisher)
        lineage.latest_published_version_id = version.workflow_version_bundle_id
        session.commit()

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "tenant_id": str(ACME_TENANT_ID),
                "workflow_draft_id": str(QA066_DRAFT_ID),
                "workflow_version_bundle_id": str(QA066_VERSION_ID),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA066 agent graph viewer workflow")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={QA066_DRAFT_ID}")
    print(f"workflow_version_bundle_id={QA066_VERSION_ID}")
    print(f"evidence_path={EVIDENCE_PATH}")
    return 0


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
            PrincipalIdentity.external_subject == "local|qa066-publisher"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa066-publisher",
        )
        session.add(principal)
    principal.display_name = "QA066 Publisher"
    principal.email = "qa066.publisher@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_lineage(session: Session, publisher: PrincipalIdentity) -> WorkflowLineage:
    lineage = session.get(WorkflowLineage, QA066_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA066_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa066-agent-graph-viewer",
            display_name="QA066 Agent Graph Viewer",
            description="Persisted workflow for QA066 graph viewer evidence.",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=publisher.principal_identity_id,
        )
        session.add(lineage)
    lineage.scope_type = "tenant"
    lineage.tenant_id = ACME_TENANT_ID
    lineage.slug = "qa066-agent-graph-viewer"
    lineage.display_name = "QA066 Agent Graph Viewer"
    lineage.description = "Persisted workflow for QA066 graph viewer evidence."
    lineage.workflow_kind = WorkflowKind.MAIN_WORKFLOW
    lineage.status = WorkflowLineageStatus.PUBLISHED
    lineage.created_by_principal_id = publisher.principal_identity_id
    session.flush()
    return lineage


def _upsert_draft(
    session: Session,
    lineage: WorkflowLineage,
    publisher: PrincipalIdentity,
) -> WorkflowDraft:
    draft = session.get(WorkflowDraft, QA066_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA066_DRAFT_ID,
            workflow_lineage_id=lineage.workflow_lineage_id,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=publisher.principal_identity_id,
            last_edited_by_principal_id=publisher.principal_identity_id,
        )
        session.add(draft)
    draft.workflow_lineage_id = lineage.workflow_lineage_id
    draft.scope_type = "tenant"
    draft.tenant_id = ACME_TENANT_ID
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1
    draft.created_by_principal_id = publisher.principal_identity_id
    draft.last_edited_by_principal_id = publisher.principal_identity_id
    session.flush()
    return draft


def _upsert_revision(
    session: Session,
    draft: WorkflowDraft,
    publisher: PrincipalIdentity,
) -> WorkflowDraftRevision:
    revision = session.get(WorkflowDraftRevision, QA066_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA066_REVISION_ID,
            workflow_draft_id=draft.workflow_draft_id,
            revision_number=1,
            authoring_document_json=_workflow_document(),
            document_sha256="6" * 64,
            change_summary="QA066 agent graph viewer seed revision.",
            created_by_principal_id=publisher.principal_identity_id,
        )
        session.add(revision)
    revision.workflow_draft_id = draft.workflow_draft_id
    revision.revision_number = 1
    revision.authoring_document_json = _workflow_document()
    revision.document_sha256 = "6" * 64
    revision.change_summary = "QA066 agent graph viewer seed revision."
    revision.created_by_principal_id = publisher.principal_identity_id
    session.flush()
    draft.latest_revision_id = revision.workflow_draft_revision_id
    return revision


def _upsert_version(
    session: Session,
    lineage: WorkflowLineage,
    draft: WorkflowDraft,
    revision: WorkflowDraftRevision,
    publisher: PrincipalIdentity,
) -> WorkflowVersionBundle:
    version = session.get(WorkflowVersionBundle, QA066_VERSION_ID)
    if version is None:
        version = WorkflowVersionBundle(
            workflow_version_bundle_id=QA066_VERSION_ID,
            workflow_lineage_id=lineage.workflow_lineage_id,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            version_sequence=1,
            display_version="qa066-v1",
            status=WorkflowVersionStatus.PUBLISHED,
            published_from_draft_id=draft.workflow_draft_id,
            published_from_revision_id=revision.workflow_draft_revision_id,
            compiled_bundle_digest="6" * 64,
            compiler_version="qa066",
            published_by_principal_id=publisher.principal_identity_id,
        )
        session.add(version)
    version.workflow_lineage_id = lineage.workflow_lineage_id
    version.scope_type = "tenant"
    version.tenant_id = ACME_TENANT_ID
    version.version_sequence = 1
    version.display_version = "qa066-v1"
    version.status = WorkflowVersionStatus.PUBLISHED
    version.published_from_draft_id = draft.workflow_draft_id
    version.published_from_revision_id = revision.workflow_draft_revision_id
    version.compiled_bundle_digest = "6" * 64
    version.compiler_version = "qa066"
    version.summary_json = {"document": _workflow_document()}
    version.published_by_principal_id = publisher.principal_identity_id
    session.flush()
    return version


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa066-agent-graph-viewer",
        "display_name": "QA066 Agent Graph Viewer",
        "description": "Workflow with representative agent graph categories.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "coordinator",
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "role_kind": "agent",
                "purpose": "Coordinate specialist work.",
                "input_contract_key": "request",
                "output_contract_key": "brief",
                "skill_bindings": [
                    {
                        "binding_key": "coordinator-tool",
                        "skill_slug": "coordinator-tool",
                        "skill_version": "2026.05.0",
                        "purpose": "Prepare safe context.",
                    }
                ],
                "graph_node_keys": ["coordinator"],
            },
            {
                "role_key": "specialist",
                "display_name": "Specialist",
                "role_kind": "subagent",
                "purpose": "Review the request.",
                "input_contract_key": "brief",
                "output_contract_key": "result",
                "graph_node_keys": ["specialist"],
            },
            {
                "role_key": "handoff",
                "display_name": "Handoff",
                "purpose": "Prepare development handoff.",
                "input_contract_key": "handoff",
                "output_contract_key": "handoff",
                "graph_node_keys": ["handoff"],
            },
        ],
        "contracts": [
            {"contract_key": "request", "json_schema": {"type": "object"}},
            {"contract_key": "brief", "json_schema": {"type": "object"}},
            {"contract_key": "result", "json_schema": {"type": "object"}},
            {
                "contract_key": "handoff",
                "contract_kind": "handoff",
                "json_schema": {"type": "object"},
            },
        ],
        "nodes": [
            {
                "node_key": "coordinator",
                "node_type": "role",
                "display_name": "Coordinator",
                "role_key": "coordinator",
            },
            {
                "node_key": "specialist",
                "node_type": "role",
                "display_name": "Specialist",
                "role_key": "specialist",
            },
            {"node_key": "join", "node_type": "join", "display_name": "Join"},
            {
                "node_key": "approval",
                "node_type": "approval",
                "display_name": "Approval",
                "approval_gate_key": "manager",
            },
            {
                "node_key": "handoff",
                "node_type": "role",
                "display_name": "Development handoff",
                "role_key": "handoff",
            },
            {"node_key": "done", "node_type": "terminal", "display_name": "Done"},
        ],
        "edges": [
            {
                "edge_key": "edge-coordinator-specialist",
                "source_node_key": "coordinator",
                "target_node_key": "specialist",
                "contract_key": "brief",
            },
            {
                "edge_key": "edge-specialist-join",
                "source_node_key": "specialist",
                "target_node_key": "join",
                "contract_key": "result",
            },
            {
                "edge_key": "edge-join-approval",
                "source_node_key": "join",
                "target_node_key": "approval",
            },
            {
                "edge_key": "edge-approval-handoff",
                "source_node_key": "approval",
                "target_node_key": "handoff",
                "contract_key": "handoff",
            },
            {
                "edge_key": "edge-handoff-done",
                "source_node_key": "handoff",
                "target_node_key": "done",
                "contract_key": "handoff",
            },
        ],
        "join_policies": [
            {
                "join_policy_key": "join-all",
                "strategy": "all_success",
                "inbound_edge_keys": ["edge-specialist-join"],
            }
        ],
        "approval_gates": [
            {
                "approval_gate_key": "manager",
                "display_name": "Manager approval",
                "approver_scope": "tenant_admin",
                "resume_behavior": "resume_origin",
            }
        ],
        "subworkflow_refs": [],
    }


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
