from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument
from multi_agent_platform.config.settings import Settings


def make_settings(tmp_path: Path) -> Settings:
    database_path = tmp_path / "platform.db"
    tenant_id = uuid4()
    return Settings(
        _env_file=None,
        app_env="test",
        auth_mode="local_principal",
        local_principal_catalog_json={
            "tenant-user-acme": {
                "catalog_key": "tenant-user-acme",
                "display_name": "Tenant User",
                "tenant_id": str(tenant_id),
                "org_id": "org-acme",
                "role_codes": ["tenant_user"],
                "permission_codes": ["tenant:read"],
            },
            "tenant-admin-acme": {
                "catalog_key": "tenant-admin-acme",
                "display_name": "Tenant Admin",
                "tenant_id": str(tenant_id),
                "org_id": "org-acme",
                "role_codes": ["tenant_user", "tenant_admin"],
                "permission_codes": [
                    "tenant:read",
                    "tenant:admin",
                    "admin:role-grants:write",
                    "admin:support-overrides:write",
                    "admin:support-overrides:approve",
                ],
            },
            "platform-admin": {
                "catalog_key": "platform-admin",
                "display_name": "Platform Admin",
                "role_codes": ["platform_admin"],
                "permission_codes": [
                    "admin:role-grants:write",
                    "admin:support-overrides:write",
                    "admin:support-overrides:approve",
                ],
            },
        },
        database_url=f"sqlite+aiosqlite:///{database_path}",
        filesystem_storage_root=tmp_path / "artifacts",
        static_secrets_json={"example/api-key": "fixture-secret"},
    )


@pytest.fixture
def settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    resolved = make_settings(tmp_path)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", resolved.database_url)
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(resolved.filesystem_storage_root))
    monkeypatch.setenv("STATIC_SECRETS_JSON", '{"example/api-key":"fixture-secret"}')
    monkeypatch.setenv("SECRET_PROVIDER", "static")
    monkeypatch.setenv("STORAGE_PROVIDER", "filesystem")
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                key: value.model_dump(mode="json")
                for key, value in resolved.local_principal_catalog_json.items()
            }
        ),
    )
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    monkeypatch.setenv("COMMIT_SHA", "test-sha")
    monkeypatch.setenv("BUILD_TIME", "2026-04-22T00:00:00+00:00")
    return Settings(_env_file=None)


@pytest.fixture
def sample_workflow_document() -> WorkflowDraftDocument:
    return WorkflowDraftDocument(
        workflow_key="customer-intake",
        display_name="Customer Intake",
        description="Collect incoming work and route it to the next step.",
        workflow_kind="main_workflow",
        entry_node_key="triage-node",
        roles=[
            {
                "role_key": "triage-role",
                "display_name": "Triage Role",
                "purpose": "Assess the incoming payload.",
                "input_contract_key": "intake-request",
                "output_contract_key": "triage-result",
                "skill_bindings": [
                    {
                        "binding_key": "triage-skill",
                        "skill_slug": "triage-agent",
                        "skill_version": "2026.04.1",
                        "purpose": "Perform triage.",
                    }
                ],
            }
        ],
        contracts=[
            {
                "contract_key": "intake-request",
                "json_schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            {
                "contract_key": "triage-result",
                "json_schema": {
                    "type": "object",
                    "properties": {"decision": {"type": "string"}},
                },
            },
        ],
        nodes=[
            {
                "node_key": "triage-node",
                "node_type": "role",
                "display_name": "Triage",
                "role_key": "triage-role",
            }
        ],
        edges=[],
        join_policies=[],
        approval_gates=[],
        subworkflow_refs=[],
    )
