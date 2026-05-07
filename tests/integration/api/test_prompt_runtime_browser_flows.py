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


def _prompt_form_data(
    *,
    tenant_id: UUID | None,
    scope_type: str,
    slug: str,
    display_name: str,
    expected_revision_number: int,
    action: str,
    lineage_id: UUID | None = None,
) -> dict[str, str]:
    data = {
        "_action": action,
        "scope_type": scope_type,
        "tenant_id": str(tenant_id) if tenant_id else "",
        "display_name": display_name,
        "slug": slug,
        "purpose": "Summarize intake",
        "usage_notes": "Used by runtime smoke tests",
        "template_content": "Hello {{name}}",
        "variables_json": json.dumps(
            [{"name": "name", "purpose": "Recipient", "required": True}]
        ),
        "fixture_values_json": json.dumps({"name": "Ada"}),
        "expected_revision_number": str(expected_revision_number),
        "reason": "Browser flow approval",
    }
    if lineage_id is not None:
        data["prompt_lineage_id"] = str(lineage_id)
    return data


def _current_prompt_revision(
    client: TestClient,
    headers: dict[str, str],
    lineage_id: UUID,
) -> int:
    response = client.get(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/draft",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return int(response.json()["current_revision_number"])


def _publish_prompt_from_form(
    client: TestClient,
    *,
    headers: dict[str, str],
    tenant_id: UUID | None,
    scope_type: str,
    slug: str,
    display_name: str,
) -> tuple[UUID, UUID]:
    saved = client.post(
        "/admin/prompt-runtime/prompts/form",
        headers=headers,
        data=_prompt_form_data(
            tenant_id=tenant_id,
            scope_type=scope_type,
            slug=slug,
            display_name=display_name,
            expected_revision_number=0,
            action="save",
        ),
        follow_redirects=False,
    )
    assert saved.status_code == 303, saved.text
    lineage_id = _location_uuid(saved, r"/prompts/([^/]+)/edit")

    revision_number = _current_prompt_revision(client, headers, lineage_id)
    validated = client.post(
        "/admin/prompt-runtime/prompts/form",
        headers=headers,
        data=_prompt_form_data(
            tenant_id=tenant_id,
            scope_type=scope_type,
            slug=slug,
            display_name=display_name,
            expected_revision_number=revision_number,
            action="validate",
            lineage_id=lineage_id,
        ),
        follow_redirects=False,
    )
    assert validated.status_code == 303, validated.text
    assert validated.headers["location"].startswith(
        f"/admin/app/governance/prompts/{lineage_id}/edit"
    )
    assert "flash=prompt-validated" in validated.headers["location"]

    revision_number = _current_prompt_revision(client, headers, lineage_id)
    preview = client.post(
        "/admin/prompt-runtime/prompts/form",
        headers=headers,
        data=_prompt_form_data(
            tenant_id=tenant_id,
            scope_type=scope_type,
            slug=slug,
            display_name=display_name,
            expected_revision_number=revision_number,
            action="preview",
            lineage_id=lineage_id,
        ),
        follow_redirects=False,
    )
    assert preview.status_code == 303, preview.text
    assert preview.headers["location"].startswith(
        f"/admin/app/governance/prompts/{lineage_id}/preview"
    )
    assert "fixture_set_id=default" in preview.headers["location"]

    revision_number = _current_prompt_revision(client, headers, lineage_id)
    revalidated = client.post(
        "/admin/prompt-runtime/prompts/form",
        headers=headers,
        data=_prompt_form_data(
            tenant_id=tenant_id,
            scope_type=scope_type,
            slug=slug,
            display_name=display_name,
            expected_revision_number=revision_number,
            action="validate",
            lineage_id=lineage_id,
        ),
        follow_redirects=False,
    )
    assert revalidated.status_code == 303, revalidated.text
    assert revalidated.headers["location"].startswith(
        f"/admin/app/governance/prompts/{lineage_id}/edit"
    )

    published = client.post(
        "/admin/prompt-runtime/prompts/form",
        headers=headers,
        data={
            "_action": "publish",
            "prompt_lineage_id": str(lineage_id),
            "reason": "Browser flow publication",
        },
        follow_redirects=False,
    )
    assert published.status_code == 303, published.text
    version_id = _location_uuid(published, r"/versions/([^?]+)")
    assert published.headers["location"].startswith(
        f"/admin/app/governance/prompts/versions/{version_id}"
    )
    return lineage_id, version_id


def test_prompt_browser_forms_submit_save_validate_preview_publish_retire_and_grant(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_prompt_runtime_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        new_page = client.get(
            "/admin/prompt-runtime/prompts/new",
            headers=TENANT_HEADERS,
            follow_redirects=False,
        )
        assert new_page.status_code == 303
        assert new_page.headers["location"] == "/admin/app/governance/prompts/new"

        lineage_id, version_id = _publish_prompt_from_form(
            client,
            headers=TENANT_HEADERS,
            tenant_id=tenant_id,
            scope_type="tenant",
            slug="tenant-triage",
            display_name="Tenant Triage",
        )

        retired = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "retire",
                "prompt_version_id": str(version_id),
                "reason": "Superseded by QA",
            },
            follow_redirects=False,
        )
        assert retired.status_code == 303, retired.text
        assert retired.headers["location"].startswith(
            f"/admin/app/governance/prompts/versions/{version_id}"
        )
        assert "flash=prompt-retired" in retired.headers["location"]

        _, platform_version_id = _publish_prompt_from_form(
            client,
            headers=PLATFORM_HEADERS,
            tenant_id=None,
            scope_type="platform",
            slug="platform-triage",
            display_name="Platform Triage",
        )
        granted = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=PLATFORM_HEADERS,
            data={
                "_action": "grant",
                "prompt_version_id": str(platform_version_id),
                "grant_tenant_ids": str(tenant_id),
                "reason": "Approved tenant fallback",
            },
            follow_redirects=False,
        )
        assert granted.status_code == 303, granted.text
        assert granted.headers["location"].startswith(
            f"/admin/app/governance/prompts/versions/{platform_version_id}"
        )
        assert "flash=prompt-granted" in granted.headers["location"]

        denied = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=TENANT_HEADERS,
            data=_prompt_form_data(
                tenant_id=other_tenant_id,
                scope_type="tenant",
                slug="cross-tenant",
                display_name="Cross Tenant",
                expected_revision_number=0,
                action="save",
            ),
        )
        assert denied.status_code == 403
