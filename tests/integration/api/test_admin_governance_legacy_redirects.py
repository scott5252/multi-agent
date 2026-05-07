from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.prompt_runtime_flow_helpers import (
    configure_prompt_runtime_env,
)

TENANT_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}


def _client(tmp_path, monkeypatch) -> tuple[TestClient, str]:
    tenant_uuid = uuid4()
    other_tenant_id = uuid4()
    configure_prompt_runtime_env(
        monkeypatch,
        tmp_path,
        tenant_id=tenant_uuid,
        other_tenant_id=other_tenant_id,
    )
    return TestClient(create_app()), str(tenant_uuid)


def _assert_redirect(response, expected_prefix: str) -> None:
    assert response.status_code == 303, response.text
    assert response.headers["location"].startswith(expected_prefix)
    assert "<html" not in response.text.lower()


def test_provider_prompt_profile_and_model_skill_legacy_routes_redirect_to_react(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id = _client(tmp_path, monkeypatch)
    provider_id = uuid4()
    prompt_lineage_id = uuid4()
    prompt_version_id = uuid4()
    profile_id = uuid4()
    profile_version_id = uuid4()
    run_id = uuid4()

    with client:
        provider_routes = {
            f"/admin/model-providers?tenant_id={tenant_id}&q=openai": (
                "/admin/app/governance/providers"
            ),
            "/admin/model-providers/new": "/admin/app/governance/providers/new",
            "/admin/model-providers/catalog": "/admin/app/governance/providers",
            f"/admin/model-providers/{provider_id}": (
                f"/admin/app/governance/providers/{provider_id}"
            ),
            f"/admin/model-providers/{provider_id}/edit": (
                f"/admin/app/governance/providers/{provider_id}/edit"
            ),
        }
        for path, expected in provider_routes.items():
            response = client.get(
                path,
                headers=PLATFORM_HEADERS,
                follow_redirects=False,
            )
            _assert_redirect(response, expected)

        prompt_routes = {
            "/admin/prompt-runtime/prompts": "/admin/app/governance/prompts",
            "/admin/prompt-runtime/prompts/new": "/admin/app/governance/prompts/new",
            f"/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit": (
                f"/admin/app/governance/prompts/{prompt_lineage_id}/edit"
            ),
            f"/admin/prompt-runtime/prompts/versions/{prompt_version_id}": (
                f"/admin/app/governance/prompts/versions/{prompt_version_id}"
            ),
            f"/admin/prompt-runtime/prompts/{prompt_lineage_id}/history": (
                f"/admin/app/governance/prompts/{prompt_lineage_id}/history"
            ),
            f"/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview": (
                f"/admin/app/governance/prompts/{prompt_lineage_id}/preview"
            ),
        }
        for path, expected in prompt_routes.items():
            response = client.get(
                path,
                headers=TENANT_HEADERS,
                follow_redirects=False,
            )
            _assert_redirect(response, expected)

        profile_routes = {
            "/admin/prompt-runtime/profiles": "/admin/app/governance/profiles",
            "/admin/prompt-runtime/profiles/new": "/admin/app/governance/profiles/new",
            f"/admin/prompt-runtime/profiles/{profile_id}/edit": (
                f"/admin/app/governance/profiles/{profile_id}/edit"
            ),
            f"/admin/prompt-runtime/profiles/versions/{profile_version_id}": (
                f"/admin/app/governance/profiles/versions/{profile_version_id}"
            ),
            f"/admin/prompt-runtime/profiles/{profile_id}/history": (
                f"/admin/app/governance/profiles/{profile_id}/history"
            ),
            (
                "/admin/prompt-runtime/profiles/resolve"
                f"?tenant_id={tenant_id}&agent_key=planner&agent_kind=agent"
            ): "/admin/app/governance/profiles/resolve",
        }
        for path, expected in profile_routes.items():
            response = client.get(
                path,
                headers=TENANT_HEADERS,
                follow_redirects=False,
            )
            _assert_redirect(response, expected)

        model_skill_routes = {
            f"/admin/config/ui?tenant_id={tenant_id}": (
                "/admin/app/governance/routing"
            ),
            f"/admin/config/ui/history?tenant_id={tenant_id}": (
                "/admin/app/governance/history"
            ),
            f"/admin/config/ui/runs/{run_id}/provenance?tenant_id={tenant_id}": (
                f"/admin/app/governance/provenance/{run_id}"
            ),
        }
        for path, expected in model_skill_routes.items():
            response = client.get(
                path,
                headers=TENANT_HEADERS,
                follow_redirects=False,
            )
            _assert_redirect(response, expected)
