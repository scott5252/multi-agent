from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.prompt_runtime_flow_helpers import (
    configure_prompt_runtime_env,
)

TENANT_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}


def _setup_client(tmp_path, monkeypatch) -> tuple[TestClient, UUID, UUID]:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_prompt_runtime_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    return TestClient(create_app()), tenant_id, other_tenant_id


def test_admin_model_skill_config_routes_submit_ui_and_api_flows(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id, _ = _setup_client(tmp_path, monkeypatch)
    tenant_scope = {"tenant_id": str(tenant_id)}
    workflow_scope = {
        "tenant_id": str(tenant_id),
        "workflow_lineage_id": str(uuid4()),
    }

    with client:
        for path in (
            "/admin/config/ui",
            "/admin/config/ui/history",
            f"/admin/config/ui/runs/{uuid4()}/provenance",
        ):
            response = client.get(path, headers=TENANT_HEADERS)
            assert response.status_code == 200, response.text
            assert "<html" in response.text

        model_routing = client.post(
            "/admin/config/model-routing",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "provider_key": "openai",
                "model_id": "gpt-5.4",
                "activate": True,
                "reason": "Set tenant default model",
            },
        )
        assert model_routing.status_code == 201, model_routing.text
        model_routing_version_id = model_routing.json()["version_id"]

        prompt_reference = client.post(
            "/admin/config/prompt-references",
            headers=TENANT_HEADERS,
            json={
                "scope": workflow_scope,
                "prompt_id": str(uuid4()),
                "prompt_version_id": str(uuid4()),
                "prompt_digest": "digest",
                "activate": True,
                "reason": "Bind workflow prompt",
            },
        )
        assert prompt_reference.status_code == 201, prompt_reference.text

        skill_binding = client.post(
            "/admin/config/skill-bindings",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "skill_slug": "planning",
                "skill_version": "1.0.0",
                "allowed_contexts": ["runtime_step"],
                "activate": True,
                "reason": "Allow planner skill",
            },
        )
        assert skill_binding.status_code == 201, skill_binding.text

        tool_policy = client.post(
            "/admin/config/tool-policies",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "skill_slug": "planning",
                "tool_id": "http.fetch",
                "allowed_action_categories": ["read"],
                "activate": True,
                "reason": "Allow read tool use",
            },
        )
        assert tool_policy.status_code == 201, tool_policy.text

        outbound_policy = client.post(
            "/admin/config/outbound-domain-policies",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "tool_id": "http.fetch",
                "action_category": "read",
                "allowed_domain_patterns": ["example.com"],
                "allowed_schemes": ["https"],
                "allowed_ports": [443],
                "activate": True,
                "reason": "Allow example.com fetches",
            },
        )
        assert outbound_policy.status_code == 201, outbound_policy.text

        secret_reference = client.post(
            "/admin/config/secret-references",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "secret_reference_id": "example-api-key",
                "provider_key": "static",
                "external_reference": "example/api-key",
                "allowed_scopes": {"host": "example.com"},
                "activate": True,
                "reason": "Use managed secret reference",
            },
        )
        assert secret_reference.status_code == 201, secret_reference.text

        credential_requirement = client.post(
            "/admin/config/credential-requirements",
            headers=TENANT_HEADERS,
            json={
                "scope": tenant_scope,
                "tool_id": "http.fetch",
                "action_category": "read",
                "credential_kind": "secret_reference",
                "secret_reference_version_id": secret_reference.json()["version_id"],
                "activate": True,
                "reason": "Require managed credential",
            },
        )
        assert credential_requirement.status_code == 201, credential_requirement.text

        model_preview = client.post(
            "/admin/config/preview/model",
            headers=TENANT_HEADERS,
            json=workflow_scope,
        )
        assert model_preview.status_code == 200, model_preview.text
        assert model_preview.json()["model_id"] == "gpt-5.4"

        tool_preview = client.post(
            "/admin/config/preview/tool",
            headers=TENANT_HEADERS,
            json={
                **tenant_scope,
                "skill_slug": "planning",
                "skill_version": "1.0.0",
                "tool_id": "http.fetch",
                "action_category": "read",
                "destination_url": "https://example.com:443/resource",
            },
        )
        assert tool_preview.status_code == 200, tool_preview.text
        assert tool_preview.json()["evaluated_version_ids"]

        history = client.get(
            "/admin/config/history",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(tenant_id), "limit": 10},
        )
        assert history.status_code == 200, history.text
        assert history.json()["items"]

        provenance = client.get(
            f"/admin/config/runs/{uuid4()}/provenance",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(tenant_id)},
        )
        assert provenance.status_code == 200, provenance.text
        assert provenance.json()["decisions"] == []

        activated = client.post(
            f"/admin/config/model-routing/{model_routing_version_id}/activate",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(tenant_id)},
            json={"reason": "Re-activate reviewed default"},
        )
        assert activated.status_code == 200, activated.text

        rolled_back = client.post(
            f"/admin/config/model_routing/{model_routing_version_id}/rollback",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(tenant_id)},
            json={
                "target_version_id": model_routing_version_id,
                "reason": "Confirm rollback flow",
            },
        )
        assert rolled_back.status_code == 200, rolled_back.text
        assert rolled_back.json()["active_version_id"] == model_routing_version_id
