from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant


def prepare_database(database_path: Path, tenant_id, other_tenant_id) -> None:
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(text("DELETE FROM alembic_version"))
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0003_workflow_registry')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"),
                Tenant(tenant_id=other_tenant_id, slug="globex", display_name="Globex"),
            ]
        )
        session.commit()


def configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id) -> None:
    database_path = tmp_path / "agent-graph-api.db"
    prepare_database(database_path, tenant_id, other_tenant_id)
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "tenant-user-acme": {
                    "catalog_key": "tenant-user-acme",
                    "display_name": "Tenant User",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user"],
                    "permission_codes": ["tenant:read"],
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Admin",
                    "tenant_id": str(other_tenant_id),
                    "org_id": "org-globex",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["tenant:admin"],
                },
            }
        ),
    )


def sample_document() -> dict[str, object]:
    return {
        "workflow_key": "agent-review",
        "display_name": "Agent Review",
        "description": "Coordinate specialist review and handoff.",
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
            {
                "node_key": "join",
                "node_type": "join",
                "display_name": "Join",
                "join_policy_key": "join-all",
            },
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
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
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


def test_draft_and_published_agent_graph_routes(tmp_path, monkeypatch) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers=headers,
            json={
                "scope_type": "tenant",
                "workflow_kind": "main_workflow",
                "slug": "agent-review",
                "display_name": "Agent Review",
                "document": sample_document(),
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        draft_graph = client.get(
            f"/admin/workflows/drafts/{draft_id}/agent-graph",
            headers=headers,
        )
        validated = client.post(
            f"/admin/workflows/drafts/{draft_id}/validate",
            headers=headers,
        )
        published = client.post(
            f"/admin/workflows/drafts/{draft_id}/publish",
            headers=headers,
            json={"validation_result_id": validated.json()["validation_result_id"]},
        )
        version_id = published.json()["workflow_version_bundle_id"]
        version_graph = client.get(
            f"/admin/workflows/versions/{version_id}/agent-graph",
            headers=headers,
        )

    assert draft_graph.status_code == 200
    draft_payload = draft_graph.json()
    assert draft_payload["source"] == "draft"
    assert draft_payload["state"] == "ready"
    assert {node["category"] for node in draft_payload["nodes"]} >= {
        "coordinator_agent",
        "sub_agent",
        "tool",
        "join",
        "approval",
        "handoff",
        "terminal",
    }
    assert "delegates_to" in {edge["category"] for edge in draft_payload["edges"]}
    assert "hands_off_to" in {edge["category"] for edge in draft_payload["edges"]}
    assert draft_payload["accessibility"]["node_summaries"]
    assert "raw prompt" not in json.dumps(draft_payload).lower()
    assert validated.status_code == 200
    assert published.status_code == 201
    assert version_graph.status_code == 200
    assert version_graph.json()["source"] == "published_version"
    assert version_graph.json()["partial"] is False
    assert version_graph.json()["nodes"]


def test_agent_graph_routes_fail_closed_and_handle_empty_graph(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    with TestClient(app) as client:
        created = client.post(
            "/admin/workflows",
            headers=headers,
            json={
                "scope_type": "tenant",
                "workflow_kind": "main_workflow",
                "slug": "empty-agent-graph",
                "display_name": "Empty Agent Graph",
                "document": {
                    "workflow_key": "empty-agent-graph",
                    "display_name": "Empty Agent Graph",
                    "workflow_kind": "main_workflow",
                    "entry_node_key": "not-yet-created",
                    "roles": [],
                    "contracts": [],
                    "nodes": [],
                    "edges": [],
                    "join_policies": [],
                    "approval_gates": [],
                    "subworkflow_refs": [],
                },
            },
        )
        draft_id = created.json()["workflow_draft_id"]
        empty_graph = client.get(
            f"/admin/workflows/drafts/{draft_id}/agent-graph",
            headers=headers,
        )
        missing = client.get(
            f"/admin/workflows/drafts/{uuid4()}/agent-graph",
            headers=headers,
        )
        missing_auth = client.get(
            f"/admin/workflows/drafts/{draft_id}/agent-graph",
        )
        denied_role = client.get(
            f"/admin/workflows/drafts/{draft_id}/agent-graph",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/workflows/drafts/{draft_id}/agent-graph",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )

    assert empty_graph.status_code == 200
    assert empty_graph.json()["state"] == "empty"
    assert empty_graph.json()["nodes"] == []
    assert missing.status_code == 404
    assert missing_auth.status_code == 401
    assert denied_role.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Acme" not in cross_tenant.text
