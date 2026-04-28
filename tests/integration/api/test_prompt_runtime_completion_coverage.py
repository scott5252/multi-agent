from __future__ import annotations

import json
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.prompt_runtime_flow_helpers import (
    configure_prompt_runtime_env,
)

TENANT_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
BETA_HEADERS = {"X-Local-Principal": "tenant-admin-beta"}
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}


def _prompt_revision_payload(
    *,
    expected_revision_number: int,
    with_fixture: bool = True,
    template_content: str = "Hello {{name}}",
) -> dict[str, object]:
    fixture_sets: list[dict[str, object]] = []
    if with_fixture:
        fixture_sets = [
            {
                "fixture_set_id": "default",
                "label": "Default",
                "values_by_variable": {"name": "Ada"},
            }
        ]
    return {
        "expected_revision_number": expected_revision_number,
        "prompt_title": "QA Prompt",
        "purpose": "planner",
        "usage_notes": "Synthetic integration coverage",
        "template_content": template_content,
        "variables": [{"name": "name", "purpose": "Recipient", "required": True}],
        "fixture_sets": fixture_sets,
    }


def _create_prompt(
    client: TestClient,
    *,
    headers: dict[str, str],
    scope_type: str,
    tenant_id: UUID | None,
    slug: str,
) -> UUID:
    response = client.post(
        "/admin/prompt-runtime/api/prompts",
        headers=headers,
        json={
            "scope_type": scope_type,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "slug": slug,
            "display_name": slug.replace("-", " ").title(),
            "purpose": "planner",
        },
    )
    assert response.status_code == 201, response.text
    return UUID(response.json()["prompt_lineage_id"])


def _save_prompt_revision(
    client: TestClient,
    *,
    headers: dict[str, str],
    lineage_id: UUID,
    expected_revision_number: int,
    with_fixture: bool = True,
    template_content: str = "Hello {{name}}",
) -> int:
    response = client.put(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/draft",
        headers=headers,
        json=_prompt_revision_payload(
            expected_revision_number=expected_revision_number,
            with_fixture=with_fixture,
            template_content=template_content,
        ),
    )
    assert response.status_code == 200, response.text
    return int(response.json()["current_revision_number"])


def _publish_prompt_version(
    client: TestClient,
    *,
    headers: dict[str, str],
    scope_type: str,
    tenant_id: UUID | None,
    slug: str,
) -> tuple[UUID, UUID]:
    lineage_id = _create_prompt(
        client,
        headers=headers,
        scope_type=scope_type,
        tenant_id=tenant_id,
        slug=slug,
    )
    revision_number = _save_prompt_revision(
        client,
        headers=headers,
        lineage_id=lineage_id,
        expected_revision_number=0,
    )
    assert revision_number == 1
    validated = client.post(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/validate",
        headers=headers,
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "passed"
    published = client.post(
        f"/admin/prompt-runtime/api/prompts/{lineage_id}/publish",
        headers=headers,
        json={"reason": "Completion coverage publication"},
    )
    assert published.status_code == 201, published.text
    return lineage_id, UUID(published.json()["prompt_version_id"])


def _profile_revision_payload(
    *,
    prompt_version_id: UUID,
    expected_revision_number: int,
    include_all_sections: bool = True,
) -> dict[str, object]:
    if not include_all_sections:
        return {
            "expected_revision_number": expected_revision_number,
            "purpose": "Incomplete profile",
            "prompt_references": [],
            "model_routing_hints": {},
            "memory_scope_policy": {},
            "skill_requirements": [],
            "tool_policy_expectations": [],
            "output_contract_expectations": {},
            "test_suite_requirements": [],
        }
    return {
        "expected_revision_number": expected_revision_number,
        "purpose": "Plan work",
        "prompt_references": [
            {
                "purpose": "planner",
                "required_purpose": "planner",
                "prompt_version_id": str(prompt_version_id),
                "required": True,
            }
        ],
        "model_routing_hints": {"provider": "openai", "model": "gpt-4.1-mini"},
        "memory_scope_policy": {"scope_mode": "read_only", "retention_mode": "run"},
        "skill_requirements": [{"skill": "planning"}],
        "tool_policy_expectations": [{"category": "read"}],
        "output_contract_expectations": {"type": "object"},
        "test_suite_requirements": [{"suite": "planner-smoke"}],
    }


def _create_profile(
    client: TestClient,
    *,
    headers: dict[str, str],
    scope_type: str,
    tenant_id: UUID | None,
    agent_key: str,
) -> UUID:
    response = client.post(
        "/admin/prompt-runtime/api/profiles",
        headers=headers,
        json={
            "scope_type": scope_type,
            "tenant_id": str(tenant_id) if tenant_id else None,
            "agent_key": agent_key,
            "agent_kind": "agent",
            "display_name": agent_key.title(),
            "purpose": "Plan work",
        },
    )
    assert response.status_code == 201, response.text
    return UUID(response.json()["agent_runtime_profile_id"])


def _save_profile_revision(
    client: TestClient,
    *,
    headers: dict[str, str],
    profile_id: UUID,
    prompt_version_id: UUID,
    expected_revision_number: int,
    include_all_sections: bool = True,
) -> int:
    response = client.put(
        f"/admin/prompt-runtime/api/profiles/{profile_id}/draft",
        headers=headers,
        json=_profile_revision_payload(
            prompt_version_id=prompt_version_id,
            expected_revision_number=expected_revision_number,
            include_all_sections=include_all_sections,
        ),
    )
    assert response.status_code == 200, response.text
    return int(response.json()["current_revision_number"])


def _activate_profile_version(
    client: TestClient,
    *,
    headers: dict[str, str],
    scope_type: str,
    tenant_id: UUID | None,
    agent_key: str,
    prompt_version_id: UUID,
) -> tuple[UUID, UUID]:
    profile_id = _create_profile(
        client,
        headers=headers,
        scope_type=scope_type,
        tenant_id=tenant_id,
        agent_key=agent_key,
    )
    revision_number = _save_profile_revision(
        client,
        headers=headers,
        profile_id=profile_id,
        prompt_version_id=prompt_version_id,
        expected_revision_number=0,
    )
    assert revision_number == 1
    validated = client.post(
        f"/admin/prompt-runtime/api/profiles/{profile_id}/validate",
        headers=headers,
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["status"] == "passed"
    activated = client.post(
        f"/admin/prompt-runtime/api/profiles/{profile_id}/activate",
        headers=headers,
        json={"reason": "Completion coverage activation"},
    )
    assert activated.status_code == 201, activated.text
    return profile_id, UUID(activated.json()["agent_profile_version_id"])


def _setup_client(tmp_path, monkeypatch) -> tuple[TestClient, UUID, UUID]:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_prompt_runtime_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    return TestClient(create_app()), tenant_id, other_tenant_id


def test_prompt_api_completion_paths_cover_filters_history_and_failures(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id, other_tenant_id = _setup_client(tmp_path, monkeypatch)
    with client:
        denied = client.get(
            "/admin/prompt-runtime/api/prompts",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(other_tenant_id)},
        )
        assert denied.status_code == 403

        tenant_lineage_id = _create_prompt(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            slug="coverage-tenant-prompt",
        )
        draft = client.get(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/draft",
            headers=TENANT_HEADERS,
        )
        assert draft.status_code == 200
        assert draft.json()["current_revision_number"] == 0

        missing_revision = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert missing_revision.status_code == 422

        missing_validation = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/publish",
            headers=TENANT_HEADERS,
            json={"reason": "Too early"},
        )
        assert missing_validation.status_code == 409

        _save_prompt_revision(
            client,
            headers=TENANT_HEADERS,
            lineage_id=tenant_lineage_id,
            expected_revision_number=0,
            with_fixture=False,
        )
        stale = client.put(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/draft",
            headers=TENANT_HEADERS,
            json=_prompt_revision_payload(expected_revision_number=0),
        )
        assert stale.status_code == 409

        failed_validation = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert failed_validation.status_code == 200
        assert failed_validation.json()["status"] == "failed"

        blocked_publish = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/publish",
            headers=TENANT_HEADERS,
            json={"reason": "Validation failed"},
        )
        assert blocked_publish.status_code == 409

        missing_fixture_set = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/preview",
            headers=TENANT_HEADERS,
            json={"fixture_set_id": "default"},
        )
        assert missing_fixture_set.status_code == 422

        revision_number = _save_prompt_revision(
            client,
            headers=TENANT_HEADERS,
            lineage_id=tenant_lineage_id,
            expected_revision_number=1,
        )
        missing_named_fixture = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/preview",
            headers=TENANT_HEADERS,
            json={"fixture_set_id": "missing"},
        )
        assert missing_named_fixture.status_code == 422

        preview = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/preview",
            headers=TENANT_HEADERS,
            json={"fixture_set_id": "default"},
        )
        assert preview.status_code == 200
        assert preview.json()["rendered_preview"] == "Hello Ada"

        passed_validation = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert passed_validation.status_code == 200
        assert passed_validation.json()["status"] == "passed"
        assert revision_number == 2

        published = client.post(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/publish",
            headers=TENANT_HEADERS,
            json={"reason": "Ready"},
        )
        assert published.status_code == 201
        tenant_version_id = UUID(published.json()["prompt_version_id"])

        no_active_draft = client.get(
            f"/admin/prompt-runtime/api/prompts/{tenant_lineage_id}/draft",
            headers=TENANT_HEADERS,
        )
        assert no_active_draft.status_code == 404

        tenant_grant = client.post(
            f"/admin/prompt-runtime/api/prompts/versions/{tenant_version_id}/grants",
            headers=TENANT_HEADERS,
            json={"tenant_ids": [str(tenant_id)], "reason": "Not platform"},
        )
        assert tenant_grant.status_code == 409

        platform_lineage_id, platform_version_id = _publish_prompt_version(
            client,
            headers=PLATFORM_HEADERS,
            scope_type="platform",
            tenant_id=None,
            slug="coverage-platform-prompt",
        )
        granted = client.post(
            f"/admin/prompt-runtime/api/prompts/versions/{platform_version_id}/grants",
            headers=PLATFORM_HEADERS,
            json={"tenant_ids": [str(tenant_id)], "reason": "Tenant use"},
        )
        assert granted.status_code == 200
        assert granted.json()["granted_tenant_ids"] == [str(tenant_id)]

        listed = client.get(
            "/admin/prompt-runtime/api/prompts",
            headers=TENANT_HEADERS,
            params={"q": "coverage", "scope_type": "platform"},
        )
        assert listed.status_code == 200
        assert any(
            item["prompt_lineage_id"] == str(platform_lineage_id)
            for item in listed.json()["items"]
        )

        platform_filtered = client.get(
            "/admin/prompt-runtime/api/prompts",
            headers=PLATFORM_HEADERS,
            params={
                "tenant_id": str(tenant_id),
                "q": "coverage",
                "status": "active",
            },
        )
        assert platform_filtered.status_code == 200

        retired = client.post(
            f"/admin/prompt-runtime/api/prompts/versions/{tenant_version_id}/retire",
            headers=TENANT_HEADERS,
            json={"reason": "Superseded"},
        )
        assert retired.status_code == 200
        assert retired.json()["status"] == "retired"

        missing_version = uuid4()
        assert (
            client.post(
                f"/admin/prompt-runtime/api/prompts/versions/{missing_version}/retire",
                headers=TENANT_HEADERS,
                json={"reason": "Missing"},
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/admin/prompt-runtime/api/prompts/versions/{missing_version}/grants",
                headers=PLATFORM_HEADERS,
                json={"tenant_ids": [str(tenant_id)], "reason": "Missing"},
            ).status_code
            == 404
        )

        history = client.get(
            "/admin/prompt-runtime/api/history",
            headers=PLATFORM_HEADERS,
            params={"resource_kind": "prompt", "resource_id": str(tenant_lineage_id)},
        )
        assert history.status_code == 200
        assert {"save_draft", "validate", "publish", "retire"}.issubset(
            {item["action"] for item in history.json()["items"]}
        )


def test_prompt_form_completion_paths_cover_json_and_action_errors(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id, _ = _setup_client(tmp_path, monkeypatch)
    with client:
        invalid_json = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "save",
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "display_name": "Broken JSON",
                "slug": "broken-json",
                "purpose": "planner",
                "template_content": "Hello {{name}}",
                "variables_json": "[",
                "fixture_values_json": "{}",
                "expected_revision_number": "0",
            },
        )
        assert invalid_json.status_code == 422
        assert invalid_json.json()["detail"]["code"] == "invalid_json"

        invalid_type = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "save",
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "display_name": "Broken Type",
                "slug": "broken-type",
                "purpose": "planner",
                "template_content": "Hello {{name}}",
                "variables_json": "{}",
                "fixture_values_json": "{}",
                "expected_revision_number": "0",
            },
        )
        assert invalid_type.status_code == 422
        assert invalid_type.json()["detail"]["code"] == "invalid_json_type"

        assert (
            client.post(
                "/admin/prompt-runtime/prompts/form",
                headers=TENANT_HEADERS,
                data={"_action": "publish"},
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/admin/prompt-runtime/prompts/form",
                headers=TENANT_HEADERS,
                data={"_action": "retire"},
            ).status_code
            == 422
        )

        lineage_id = _create_prompt(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            slug="form-preview",
        )
        saved = client.post(
            "/admin/prompt-runtime/prompts/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "preview",
                "prompt_lineage_id": str(lineage_id),
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "display_name": "Form Preview",
                "slug": "form-preview",
                "purpose": "planner",
                "template_content": "Hello {{name}}",
                "variables_json": json.dumps(
                    [{"name": "name", "purpose": "Recipient", "required": True}]
                ),
                "fixture_values_json": json.dumps({"name": "Ada"}),
                "expected_revision_number": "0",
                "reason": "Preview",
            },
            follow_redirects=False,
        )
        assert saved.status_code == 303
        assert "/preview?fixture_set_id=default" in saved.headers["location"]


def test_profile_api_completion_paths_cover_resolution_history_and_failures(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id, other_tenant_id = _setup_client(tmp_path, monkeypatch)
    with client:
        _, tenant_prompt_version_id = _publish_prompt_version(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            slug="coverage-profile-tenant-prompt",
        )
        _, platform_prompt_version_id = _publish_prompt_version(
            client,
            headers=PLATFORM_HEADERS,
            scope_type="platform",
            tenant_id=None,
            slug="coverage-profile-platform-prompt",
        )
        prompt_grant = client.post(
            f"/admin/prompt-runtime/api/prompts/versions/{platform_prompt_version_id}/grants",
            headers=PLATFORM_HEADERS,
            json={"tenant_ids": [str(tenant_id)], "reason": "Profile reference"},
        )
        assert prompt_grant.status_code == 200

        denied = client.get(
            "/admin/prompt-runtime/api/profiles",
            headers=TENANT_HEADERS,
            params={"tenant_id": str(other_tenant_id)},
        )
        assert denied.status_code == 403

        missing_resolution = client.post(
            "/admin/prompt-runtime/api/resolve-profile",
            headers=TENANT_HEADERS,
            json={
                "tenant_id": str(tenant_id),
                "agent_key": "not-created",
                "agent_kind": "agent",
            },
        )
        assert missing_resolution.status_code == 200
        assert missing_resolution.json()["resolved"] is False

        profile_id = _create_profile(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            agent_key="coverage-planner",
        )
        missing_revision = client.post(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert missing_revision.status_code == 422

        revision_number = _save_profile_revision(
            client,
            headers=TENANT_HEADERS,
            profile_id=profile_id,
            prompt_version_id=tenant_prompt_version_id,
            expected_revision_number=0,
            include_all_sections=False,
        )
        failed = client.post(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert failed.status_code == 200
        assert failed.json()["status"] == "failed"

        blocked_activation = client.post(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/activate",
            headers=TENANT_HEADERS,
            json={"reason": "Validation failed"},
        )
        assert blocked_activation.status_code == 409

        stale = client.put(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/draft",
            headers=TENANT_HEADERS,
            json=_profile_revision_payload(
                prompt_version_id=tenant_prompt_version_id,
                expected_revision_number=0,
            ),
        )
        assert stale.status_code == 409

        revision_number = _save_profile_revision(
            client,
            headers=TENANT_HEADERS,
            profile_id=profile_id,
            prompt_version_id=tenant_prompt_version_id,
            expected_revision_number=revision_number,
        )
        assert revision_number == 2
        passed = client.post(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/validate",
            headers=TENANT_HEADERS,
        )
        assert passed.status_code == 200
        assert passed.json()["status"] == "passed"

        activated = client.post(
            f"/admin/prompt-runtime/api/profiles/{profile_id}/activate",
            headers=TENANT_HEADERS,
            json={"reason": "Tenant active"},
        )
        assert activated.status_code == 201
        tenant_profile_version_id = UUID(activated.json()["agent_profile_version_id"])

        tenant_profile_grant = client.post(
            "/admin/prompt-runtime/api/profiles/versions/"
            f"{tenant_profile_version_id}/grants",
            headers=TENANT_HEADERS,
            json={"tenant_ids": [str(tenant_id)], "reason": "Not platform"},
        )
        assert tenant_profile_grant.status_code == 409

        platform_profile_id, platform_profile_version_id = _activate_profile_version(
            client,
            headers=PLATFORM_HEADERS,
            scope_type="platform",
            tenant_id=None,
            agent_key="coverage-platform-planner",
            prompt_version_id=platform_prompt_version_id,
        )
        profile_grant = client.post(
            "/admin/prompt-runtime/api/profiles/versions/"
            f"{platform_profile_version_id}/grants",
            headers=PLATFORM_HEADERS,
            json={"tenant_ids": [str(tenant_id)], "reason": "Fallback"},
        )
        assert profile_grant.status_code == 200
        assert profile_grant.json()["granted_tenant_ids"] == [str(tenant_id)]

        listed = client.get(
            "/admin/prompt-runtime/api/profiles",
            headers=TENANT_HEADERS,
            params={"agent_key": "coverage-platform-planner", "agent_kind": "agent"},
        )
        assert listed.status_code == 200
        assert any(
            item["agent_runtime_profile_id"] == str(platform_profile_id)
            for item in listed.json()["items"]
        )

        resolved = client.post(
            "/admin/prompt-runtime/api/resolve-profile",
            headers=TENANT_HEADERS,
            json={
                "tenant_id": str(tenant_id),
                "agent_key": "coverage-platform-planner",
                "agent_kind": "agent",
            },
        )
        assert resolved.status_code == 200
        assert resolved.json()["resolved"] is True
        assert resolved.json()["source_scope"] == "platform"

        resolved_ui = client.get(
            "/admin/prompt-runtime/profiles/resolve",
            headers=TENANT_HEADERS,
            params={
                "tenant_id": str(tenant_id),
                "agent_key": "coverage-platform-planner",
                "agent_kind": "agent",
            },
        )
        assert resolved_ui.status_code == 200
        assert f"Resolved to {platform_profile_version_id}" in resolved_ui.text

        retired = client.post(
            "/admin/prompt-runtime/api/profiles/versions/"
            f"{tenant_profile_version_id}/retire",
            headers=TENANT_HEADERS,
            json={"reason": "Superseded"},
        )
        assert retired.status_code == 200
        assert retired.json()["status"] == "retired"

        missing_version = uuid4()
        assert (
            client.post(
                f"/admin/prompt-runtime/api/profiles/versions/{missing_version}/retire",
                headers=TENANT_HEADERS,
                json={"reason": "Missing"},
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/admin/prompt-runtime/api/profiles/versions/{missing_version}/grants",
                headers=PLATFORM_HEADERS,
                json={"tenant_ids": [str(tenant_id)], "reason": "Missing"},
            ).status_code
            == 404
        )

        history = client.get(
            "/admin/prompt-runtime/api/history",
            headers=PLATFORM_HEADERS,
            params={"resource_kind": "profile", "resource_id": str(profile_id)},
        )
        assert history.status_code == 200
        assert {"save_draft", "validate", "activate", "retire"}.issubset(
            {item["action"] for item in history.json()["items"]}
        )

        combined_history = client.get(
            "/admin/prompt-runtime/api/history",
            headers=PLATFORM_HEADERS,
        )
        assert combined_history.status_code == 200
        assert combined_history.json()["items"]


def test_profile_form_completion_paths_cover_json_and_action_errors(
    tmp_path,
    monkeypatch,
) -> None:
    client, tenant_id, _ = _setup_client(tmp_path, monkeypatch)
    with client:
        invalid_json = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "save",
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "agent_key": "broken",
                "agent_kind": "agent",
                "display_name": "Broken",
                "purpose": "Plan",
                "prompt_references_json": "[",
                "model_routing_hints_json": "{}",
                "memory_scope_policy_json": "{}",
                "skill_requirements_json": "[]",
                "tool_policy_expectations_json": "[]",
                "output_contract_expectations_json": "{}",
                "test_suite_requirements_json": "[]",
                "expected_revision_number": "0",
            },
        )
        assert invalid_json.status_code == 422
        assert invalid_json.json()["detail"]["code"] == "invalid_json"

        invalid_type = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "save",
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "agent_key": "broken-type",
                "agent_kind": "agent",
                "display_name": "Broken Type",
                "purpose": "Plan",
                "prompt_references_json": "{}",
                "model_routing_hints_json": "{}",
                "memory_scope_policy_json": "{}",
                "skill_requirements_json": "[]",
                "tool_policy_expectations_json": "[]",
                "output_contract_expectations_json": "{}",
                "test_suite_requirements_json": "[]",
                "expected_revision_number": "0",
            },
        )
        assert invalid_type.status_code == 422
        assert invalid_type.json()["detail"]["code"] == "invalid_json_type"

        assert (
            client.post(
                "/admin/prompt-runtime/profiles/form",
                headers=TENANT_HEADERS,
                data={"_action": "activate"},
            ).status_code
            == 422
        )
        assert (
            client.post(
                "/admin/prompt-runtime/profiles/form",
                headers=TENANT_HEADERS,
                data={"_action": "retire"},
            ).status_code
            == 422
        )

        _, prompt_version_id = _publish_prompt_version(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            slug="form-profile-prompt",
        )
        profile_id = _create_profile(
            client,
            headers=TENANT_HEADERS,
            scope_type="tenant",
            tenant_id=tenant_id,
            agent_key="form-profile",
        )
        saved = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "validate",
                "agent_runtime_profile_id": str(profile_id),
                "scope_type": "tenant",
                "tenant_id": str(tenant_id),
                "agent_key": "form-profile",
                "agent_kind": "agent",
                "display_name": "Form Profile",
                "purpose": "Plan",
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
                "test_suite_requirements_json": json.dumps(
                    [{"suite": "planner-smoke"}]
                ),
                "expected_revision_number": "0",
                "reason": "Validate",
            },
            follow_redirects=False,
        )
        assert saved.status_code == 303
        assert "flash=profile-validated" in saved.headers["location"]

        activated = client.post(
            "/admin/prompt-runtime/profiles/form",
            headers=TENANT_HEADERS,
            data={
                "_action": "activate",
                "agent_runtime_profile_id": str(profile_id),
                "reason": "Activate",
            },
            follow_redirects=False,
        )
        assert activated.status_code == 303
        assert "flash=profile-activated" in activated.headers["location"]
