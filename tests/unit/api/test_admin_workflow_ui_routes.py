from __future__ import annotations

from uuid import uuid4

import pytest
from starlette.requests import Request

from multi_agent_platform.api.routers import admin_workflow_ui
from multi_agent_platform.auth.principal import PrincipalContext


def build_request(path: str, query_string: bytes = b"") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": query_string,
        }
    )


@pytest.mark.asyncio
async def test_admin_workflow_ui_get_routes_redirect_to_react() -> None:
    principal = PrincipalContext(principal_id="tenant-admin")
    session = object()
    draft_id = uuid4()
    version_id = uuid4()

    registry = await admin_workflow_ui.workflow_registry_page(
        request=build_request(
            "/admin/workflows/ui",
            b"tenant_id=11111111-1111-1111-1111-111111111111&status=draft&q=UI",
        ),
        principal=principal,
        session=session,
    )
    create = await admin_workflow_ui.workflow_draft_create_page(
        request=build_request("/admin/workflows/new"),
        principal=principal,
        session=session,
    )
    editor = await admin_workflow_ui.workflow_draft_editor_page(
        workflow_draft_id=draft_id,
        request=build_request(
            "/admin/workflows/drafts/editor",
            b"conflict=stale-save",
        ),
        principal=principal,
        session=session,
    )
    revisions = await admin_workflow_ui.workflow_draft_revision_history_page(
        workflow_draft_id=draft_id,
        request=build_request("/admin/workflows/drafts/revisions"),
        principal=principal,
        session=session,
    )
    publish_gate = await admin_workflow_ui.workflow_publish_gate_page(
        workflow_draft_id=draft_id,
        request=build_request("/admin/workflows/drafts/publish-gate"),
        principal=principal,
        session=session,
    )
    detail = await admin_workflow_ui.workflow_version_detail_page(
        workflow_version_bundle_id=version_id,
        request=build_request("/admin/workflows/versions/detail"),
        principal=principal,
        session=session,
    )

    assert registry.status_code == 303
    assert registry.headers["location"] == (
        "/admin/app/workflows?"
        "tenant_id=11111111-1111-1111-1111-111111111111&status=draft&q=UI"
    )
    assert create.headers["location"] == "/admin/app/workflows/new"
    assert editor.headers["location"] == (
        f"/admin/app/workflows/drafts/{draft_id}?conflict=stale-save"
    )
    assert revisions.headers["location"] == (
        f"/admin/app/workflows/drafts/{draft_id}/revisions"
    )
    assert publish_gate.headers["location"] == (
        f"/admin/app/workflows/drafts/{draft_id}/publish-gate"
    )
    assert detail.headers["location"] == f"/admin/app/workflows/versions/{version_id}"


def test_react_workflow_redirect_filters_unsafe_query() -> None:
    response = admin_workflow_ui._react_workflow_redirect(
        build_request(
            "/admin/workflows/ui",
            b"q=briefing&next=https%3A%2F%2Fexample.com&debug=/Users/example",
        )
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/app/workflows?q=briefing"
