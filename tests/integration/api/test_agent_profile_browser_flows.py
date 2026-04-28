from __future__ import annotations

import json
import re
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.prompt_runtime_flow_helpers import (
    configure_prompt_runtime_env,
)

TENANT_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}


def _location_uuid(response, pattern: str) -> UUID:
    match = re.search(pattern, response.headers["location"])
    assert match is not None, response.headers["location"]
    return UUID(match.group(1))


def _create_prompt_version(
    client: TestClient,
    *,
    headers: dict[str, str],
    tenant_id: UUID | None,
    scope_type: str,
    slug: str,
) -> UUID:
    created = client.post(
        "/admin/prompt-runtime/api/prompts",
        headers=headers,
        json={
            "scope_type": scope_type,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "slug": slug,
            "display_name": slug.replace("-", " ").title(),
            "purpose": "Profile reference prompt",
        },
    )
    assert created.status_code == 201, created.text
    lineage_id = UUID(created.json()["prompt_lineage_id"])
    saved = client.put(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/draft",
        headers=headers,
        json={
            "expected_revision_number": 0,
            "prompt_title": slug,
            "purpose": "planner",
            "usage_notes": "",
            "template_content": "Plan for {{name}}",
            "variables": [{"name": "name", "purpose": "Recipient"}],
            "fixture_sets": [
                {
                    "fixture_set_id": "default",
                    "label": "Default",
                    "values_by_variable": {"name": "Ada"},
                }
            ],
        },
    )
    assert saved.status_code == 200, saved.text
    validated = client.post(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/validate",
        headers=headers,
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "passed"
    published = client.post(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/publish",
        headers=headers,
        json={"reason": "Profile browser flow setup"},
    )
    assert published.status_code == 201, published.text
    return UUID(published.json()["prompt_version_id"])


def _profile_form_data(
    *,
    tenant_id: UUID | None,
    scope_type: str,
    prompt_version_id: UUID,
    expected_revision_number: int,
    action: str,
    profile_id: UUID | None = None,
) -> dict[str, str]:
    data = {
        "_action": action,
        "scope_type": scope_type,
        "tenant_id": str(tenant_id) if tenant_id else "",
        "agent_key": "planner",
        "agent_kind": "agent",
        "display_name": "Planner",
        "purpose": "Plan work",
        "prompt_references_json": json.dumps(
            [
                {
                    "purpose": "planner",
                    "required_purpose": "planner",
                    "prompt_version_id": str(prompt_version_id),
                    "required": True,
                }
            ]
        ),
        "model_routing_hints_json": json.dumps(
            {"provider": "openai", "model": "gpt-4.1-mini"}
        ),
        "memory_scope_policy_json": json.dumps(
            {"scope_mode": "read_only", "retention_mode": "run"}
        ),
        "skill_requirements_json": json.dumps([{"skill": "planning"}]),
        "tool_policy_expectations_json": json.dumps([{"category": "read"}]),
        "output_contract_expectations_json": json.dumps({"type": "object"}),
        "test_suite_requirements_json": json.dumps([{"suite": "planner-smoke"}]),
        "expected_revision_number": str(expected_revision_number),
        "reason": "Browser profile approval",
    }
    if profile_id is not None:
        data["agent_runtime_profile_id"] = str(profile_id)
    return data


def _current_profile_revision(
    client: TestClient,
    headers: dict[str, str],
    profile_id: UUID,
) -> int:
    listed = client.get(
        "/admin/prompt-runtime/api/profiles",
        headers=headers,
        params={"agent_key": "planner"},
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert any(item["agent_runtime_profile_id"] == str(profile_id) for item in items)
    edit_page = client.get(
        f"/admin/prompt-runtime/profiles/{profile_id}/edit",
        headers=headers,
    )
    assert edit_page.status_code == 200, edit_page.text
    match = re.search(
        r'name="expected_revision_number" value="([0-9]+)"',
        edit_page.text,
    )
    assert match is not None
    return int(match.group(1))


def test_profile_browser_forms_submit_validate_activate_grant_resolve_and_retire(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_prompt_runtime_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        platform_prompt_version_id = _create_prompt_version(
            client,
            headers=PLATFORM_HEADERS,
            tenant_id=None,
            scope_type="platform",
            slug="platform-planner",
        )
        new_page = client.get(
            "/admin/prompt-runtime/profiles/new",
            headers=PLATFORM_HEADERS,
        )
        assert new_page.status_code == 200
        assert 'name="_action" value="save"' in new_page.text

        saved = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=PLATFORM_HEADERS,
            data=_profile_form_data(
                tenant_id=None,
                scope_type="platform",
                prompt_version_id=platform_prompt_version_id,
                expected_revision_number=0,
                action="save",
            ),
            follow_redirects=False,
        )
        assert saved.status_code == 303, saved.text
        profile_id = _location_uuid(saved, r"/profiles/([^/]+)/edit")

        revision_number = _current_profile_revision(
            client,
            PLATFORM_HEADERS,
            profile_id,
        )
        validated = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=PLATFORM_HEADERS,
            data=_profile_form_data(
                tenant_id=None,
                scope_type="platform",
                prompt_version_id=platform_prompt_version_id,
                expected_revision_number=revision_number,
                action="validate",
                profile_id=profile_id,
            ),
            follow_redirects=False,
        )
        assert validated.status_code == 303, validated.text
        edit_page = client.get(validated.headers["location"], headers=PLATFORM_HEADERS)
        assert "Status: passed" in edit_page.text

        activated = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=PLATFORM_HEADERS,
            data={
                "_action": "activate",
                "agent_runtime_profile_id": str(profile_id),
                "reason": "Browser flow activation",
            },
            follow_redirects=False,
        )
        assert activated.status_code == 303, activated.text
        profile_version_id = _location_uuid(activated, r"/versions/([^?]+)")

        granted = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=PLATFORM_HEADERS,
            data={
                "_action": "grant",
                "agent_profile_version_id": str(profile_version_id),
                "grant_tenant_ids": str(tenant_id),
                "reason": "Tenant fallback approved",
            },
            follow_redirects=False,
        )
        assert granted.status_code == 303, granted.text
        granted_page = client.get(granted.headers["location"], headers=PLATFORM_HEADERS)
        assert str(tenant_id) in granted_page.text

        resolved = client.get(
            "/admin/prompt-runtime/profiles/resolve",
            headers=TENANT_HEADERS,
            params={
                "tenant_id": str(tenant_id),
                "agent_key": "planner",
                "agent_kind": "agent",
            },
        )
        assert resolved.status_code == 200
        assert f"Resolved to {profile_version_id}" in resolved.text

        retired = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=PLATFORM_HEADERS,
            data={
                "_action": "retire",
                "agent_profile_version_id": str(profile_version_id),
                "reason": "Superseded profile",
            },
            follow_redirects=False,
        )
        assert retired.status_code == 303, retired.text
        retired_page = client.get(retired.headers["location"], headers=PLATFORM_HEADERS)
        assert "Status</dt><dd>retired</dd>" in retired_page.text

        denied = client.post(
            "/admin/prompt-runtime/api/profiles",
            headers=TENANT_HEADERS,
            json={
                "scope_type": "tenant",
                "tenant_id": str(other_tenant_id),
                "agent_key": "denied",
                "agent_kind": "agent",
                "display_name": "Denied",
                "purpose": "Cross tenant",
            },
        )
        assert denied.status_code == 403
