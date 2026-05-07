from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.api.routers.admin_skill_registry import (
    get_skill_registry_service,
    reset_skill_registry_service,
)
from tests.fixtures.skill_registry import valid_skill_manifest
from tests.integration.api.skill_registry_test_support import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    GLOBEX_HEADERS,
    PLATFORM_HEADERS,
    configure_skill_registry_env,
)


def test_platform_package_forms_execute_and_redirect_to_react(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_skill_registry_service()
    configure_skill_registry_env(monkeypatch, tmp_path)
    app = create_app()
    manifest = valid_skill_manifest()

    with TestClient(app) as client:
        created = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "description": "Safe calendar skill.",
                "owner_principal_id": "platform-admin",
            },
            follow_redirects=False,
        )
        duplicate = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "owner_principal_id": "platform-admin",
            },
        )
        invalid_create = client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={"slug": "", "display_name": ""},
        )
        candidate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={
                "manifest": json.dumps(manifest),
                "artifact_digest": "sha256:artifact",
                "approved_integration_refs": "tool:calendar:v1",
            },
            follow_redirects=False,
        )
        invalid_candidate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={"manifest": "", "artifact_digest": ""},
        )
        stale_validate = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/validate",
            headers=PLATFORM_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        service = get_skill_registry_service()
        candidate_token = service.candidates["calendar-assistant"].revision_token
        validated = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/validate",
            headers=PLATFORM_HEADERS,
            data={"revision_token": candidate_token},
            follow_redirects=False,
        )
        publish_token = service.candidates["calendar-assistant"].revision_token
        stale_publish = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/publish",
            headers=PLATFORM_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        published = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate/publish",
            headers=PLATFORM_HEADERS,
            data={"revision_token": publish_token},
            follow_redirects=False,
        )
        empty_grant = client.post(
            (
                "/admin/skill-registry/ui/packages/calendar-assistant/"
                "versions/1.2.3/grants"
            ),
            headers=PLATFORM_HEADERS,
            data={"tenant_ids": ""},
        )
        granted = client.post(
            (
                "/admin/skill-registry/ui/packages/calendar-assistant/"
                "versions/1.2.3/grants"
            ),
            headers=PLATFORM_HEADERS,
            data={"tenant_ids": ACME_TENANT_ID, "grant_reason": "QA"},
            follow_redirects=False,
        )

    assert created.status_code == 303
    assert created.headers["location"] == (
        "/admin/app/skills/packages/calendar-assistant"
    )
    assert duplicate.status_code == 422
    assert duplicate.json()["detail"]["category"] == "skill_package_form_invalid"
    assert invalid_create.status_code == 422
    assert invalid_create.json()["detail"]["errors"][0]["field"] == "slug"
    assert candidate.status_code == 303
    assert candidate.headers["location"] == (
        "/admin/app/skills/packages/calendar-assistant/candidate"
    )
    assert invalid_candidate.status_code == 422
    assert (
        invalid_candidate.json()["detail"]["category"] == "skill_candidate_form_invalid"
    )
    assert stale_validate.status_code == 303
    assert stale_validate.headers["location"].endswith("conflict=stale")
    assert validated.status_code == 303
    assert stale_publish.status_code == 303
    assert stale_publish.headers["location"].endswith("conflict=stale")
    assert published.status_code == 303
    assert published.headers["location"] == (
        "/admin/app/skills/packages/calendar-assistant/versions/1.2.3"
    )
    assert empty_grant.status_code == 422
    assert granted.status_code == 303
    assert granted.headers["location"].endswith("/versions/1.2.3/grants")
    assert (
        ACME_TENANT_ID
        in service.packages["calendar-assistant"].versions["1.2.3"].tenant_grants
    )
    assert "raw manifest" not in created.text.lower()


def test_tenant_installation_forms_execute_and_redirect_to_react(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_skill_registry_service()
    configure_skill_registry_env(monkeypatch, tmp_path)
    app = create_app()
    _publish_and_grant_calendar_skill()
    service = get_skill_registry_service()

    with TestClient(app) as client:
        invalid_install = client.post(
            "/admin/skill-registry/ui/installations",
            headers=ACME_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
        )
        installed = client.post(
            "/admin/skill-registry/ui/installations",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "slug": "calendar-assistant",
                "semantic_version": "1.2.3",
            },
            follow_redirects=False,
        )
        installation_id = installed.headers["location"].rsplit("/", 1)[-1]
        revision_token = service.installations[installation_id].revision_token
        invalid_credentials = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/credentials",
            headers=ACME_HEADERS,
            data={"revision_token": ""},
        )
        configured = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/credentials",
            headers=ACME_HEADERS,
            data={
                "revision_token": revision_token,
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "reference_id": "delegated-calendar-acme",
                "delegated_scope": "calendar.readonly",
            },
            follow_redirects=False,
        )
        stale_credentials = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/credentials",
            headers=ACME_HEADERS,
            data={
                "revision_token": revision_token,
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "reference_id": "",
            },
            follow_redirects=False,
        )
        smoke_token = service.installations[installation_id].revision_token
        stale_smoke = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/smoke-tests",
            headers=ACME_HEADERS,
            data={"revision_token": "stale"},
            follow_redirects=False,
        )
        smoke = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/smoke-tests",
            headers=ACME_HEADERS,
            data={"revision_token": smoke_token},
            follow_redirects=False,
        )
        eligibility_token = service.installations[installation_id].revision_token
        eligibility = client.post(
            (
                f"/admin/skill-registry/ui/installations/{installation_id}/"
                "eligibility-preview"
            ),
            headers=ACME_HEADERS,
            data={
                "revision_token": eligibility_token,
                "context_type": "profile",
                "context_id": "qa-profile",
            },
            follow_redirects=False,
        )
        stale_eligibility = client.post(
            (
                f"/admin/skill-registry/ui/installations/{installation_id}/"
                "eligibility-preview"
            ),
            headers=ACME_HEADERS,
            data={
                "revision_token": "stale",
                "context_type": "profile",
                "context_id": "qa-profile",
            },
            follow_redirects=False,
        )
        denied_credentials = client.post(
            f"/admin/skill-registry/ui/installations/{installation_id}/credentials",
            headers=GLOBEX_HEADERS,
            data={
                "revision_token": eligibility_token,
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "reference_id": "delegated-calendar-globex",
            },
            follow_redirects=False,
        )

    assert invalid_install.status_code == 422
    assert installed.status_code == 303
    assert installed.headers["location"] == (
        f"/admin/app/skills/installations/{installation_id}"
    )
    assert invalid_credentials.status_code == 422
    assert configured.status_code == 303
    assert configured.headers["location"] == (
        f"/admin/app/skills/installations/{installation_id}"
    )
    assert service.installations[installation_id].readiness is not None
    assert service.installations[installation_id].readiness.credential_status == "ready"
    assert stale_credentials.status_code == 303
    assert stale_credentials.headers["location"].endswith("conflict=stale")
    assert stale_smoke.status_code == 303
    assert stale_smoke.headers["location"].endswith("conflict=stale")
    assert smoke.status_code == 303
    assert eligibility.status_code == 303
    assert "eligibility=allowed" in eligibility.headers["location"]
    assert "qa-profile" in eligibility.headers["location"]
    assert stale_eligibility.status_code == 303
    assert stale_eligibility.headers["location"].endswith("conflict=stale")
    assert denied_credentials.status_code == 403
    assert "Globex" not in denied_credentials.text


def test_candidate_upload_takes_precedence_and_never_renders_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_skill_registry_service()
    configure_skill_registry_env(monkeypatch, tmp_path)
    app = create_app()
    manifest = valid_skill_manifest()

    with TestClient(app) as client:
        client.post(
            "/admin/skill-registry/ui/packages",
            headers=PLATFORM_HEADERS,
            data={
                "slug": "calendar-assistant",
                "display_name": "Calendar Assistant",
                "description": "Safe calendar skill.",
                "owner_principal_id": "platform-admin",
            },
            follow_redirects=False,
        )
        form = client.get(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        uploaded = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={
                "manifest": "raw manifest text that should lose precedence",
                "artifact_digest": "sha256:uploaded-artifact",
                "approved_integration_refs": "tool:calendar:v1",
            },
            files={
                "manifest_file": (
                    "manifest.json",
                    json.dumps(manifest).encode(),
                    "application/json",
                )
            },
            follow_redirects=False,
        )
        service = get_skill_registry_service()
        uploaded_digest = service.candidates["calendar-assistant"].artifact_digest
        pasted = client.post(
            "/admin/skill-registry/ui/packages/calendar-assistant/candidate",
            headers=PLATFORM_HEADERS,
            data={
                "manifest": json.dumps(manifest),
                "artifact_digest": "sha256:pasted-artifact",
                "approved_integration_refs": "tool:calendar:v1",
            },
            files={"manifest_file": ("", b"", "application/octet-stream")},
            follow_redirects=False,
        )

    assert form.status_code == 303
    assert form.headers["location"] == (
        "/admin/app/skills/packages/calendar-assistant/candidate"
    )
    assert uploaded.status_code == 303
    assert uploaded_digest == "sha256:uploaded-artifact"
    assert service.candidates["calendar-assistant"].artifact_digest == (
        "sha256:pasted-artifact"
    )
    assert pasted.status_code == 303
    assert "textarea" not in uploaded.text.lower()
    assert "raw manifest" not in uploaded.text.lower()


def _publish_and_grant_calendar_skill() -> None:
    service = get_skill_registry_service()
    service.create_package(
        slug="calendar-assistant",
        display_name="Calendar Assistant",
        description="Safe calendar skill.",
        owner_principal_id="platform-admin",
        actor_principal_id="platform-admin",
    )
    version = service.publish_version(
        slug="calendar-assistant",
        manifest_payload=valid_skill_manifest(),
        artifact_digest="sha256:artifact",
        actor_principal_id="platform-admin",
        approved_integration_refs={"tool:calendar:v1"},
    )
    service.grant_tenant_availability(
        slug=version.slug,
        semantic_version=version.semantic_version,
        tenant_id=ACME_TENANT_ID,
        actor_principal_id="platform-admin",
    )
