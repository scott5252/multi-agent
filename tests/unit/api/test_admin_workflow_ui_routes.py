from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from multi_agent_platform.admin.workflow_registry.service import (
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.routers import admin_workflow_ui
from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowScopeType,
    WorkflowVersionResponse,
)
from multi_agent_platform.api.ui.admin_console import (
    AdminScope,
    build_admin_shell_context,
)
from multi_agent_platform.auth.principal import PrincipalContext


def build_request(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
        }
    )


def build_container() -> SimpleNamespace:
    templates_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "multi_agent_platform"
        / "web_admin"
        / "templates"
    )
    return SimpleNamespace(
        workflow_ui_templates=Jinja2Templates(directory=str(templates_dir))
    )


class FakeUIService:
    def __init__(
        self, *, draft=None, version=None, items=None, exc: Exception | None = None
    ):
        self.draft = draft
        self.version = version
        self.items = items or []
        self.exc = exc

    async def list_workflows(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.items

    async def get_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.draft

    async def get_workflow_version(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.version

    def workflow_registry_service(self):
        return SimpleNamespace(
            get_editor_metadata=lambda: WorkflowEditorMetadataResponse()
        )


class FakeSavedFilterRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def list_filters(self, **kwargs) -> list[object]:
        return []


async def fake_resolve_scope_for_request(**kwargs) -> AdminScope:
    return AdminScope.platform()


async def fake_build_shell_for_request(**kwargs):
    principal = PrincipalContext(
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    request = kwargs["request"]
    title = kwargs["title"]
    return build_admin_shell_context(
        principal=principal,
        active_scope=AdminScope.platform(),
        current_path=request.url.path,
        title=title,
    )


@pytest.mark.asyncio
async def test_admin_workflow_ui_routes_render_templates(
    monkeypatch, sample_workflow_document
) -> None:
    now = datetime.now(UTC)
    draft = WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        scope_type=WorkflowScopeType.TENANT,
        workflow_kind="main_workflow",
        status="active",
        current_revision_number=1,
        latest_revision=WorkflowDraftRevisionResponse(
            workflow_draft_revision_id=uuid4(),
            revision_number=1,
            document_sha256="abc123",
            created_at=now,
        ),
        document=sample_workflow_document,
        updated_at=now,
    )
    version = WorkflowVersionResponse(
        workflow_version_bundle_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        display_version="v1",
        scope_type=WorkflowScopeType.PLATFORM,
        status="published",
        compiled_bundle_digest="digest-123",
        compiler_version="workflow-registry-0.1",
        published_from_draft_id=uuid4(),
        published_from_revision_id=uuid4(),
        published_at=now,
    )
    principal = PrincipalContext(principal_id="tenant-admin")
    container = build_container()

    monkeypatch.setattr(
        admin_workflow_ui,
        "_build_admin_service",
        lambda session, container: FakeUIService(items=[]),
    )
    monkeypatch.setattr(
        admin_workflow_ui,
        "AdminSavedFilterRepository",
        FakeSavedFilterRepository,
    )
    monkeypatch.setattr(
        admin_workflow_ui,
        "resolve_scope_for_request",
        fake_resolve_scope_for_request,
    )
    monkeypatch.setattr(
        admin_workflow_ui,
        "build_shell_for_request",
        fake_build_shell_for_request,
    )
    registry = await admin_workflow_ui.workflow_registry_page(
        request=build_request("/admin/workflows/ui"),
        principal=principal,
        session=object(),
        container=container,
    )
    assert registry.status_code == 200

    monkeypatch.setattr(
        admin_workflow_ui,
        "_build_admin_service",
        lambda session, container: FakeUIService(draft=draft),
    )
    editor = await admin_workflow_ui.workflow_draft_editor_page(
        workflow_draft_id=draft.workflow_draft_id,
        request=build_request("/admin/workflows/drafts/editor"),
        principal=principal,
        session=object(),
        container=container,
    )
    assert editor.status_code == 200

    monkeypatch.setattr(
        admin_workflow_ui,
        "_build_admin_service",
        lambda session, container: FakeUIService(version=version),
    )
    detail = await admin_workflow_ui.workflow_version_detail_page(
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        request=build_request("/admin/workflows/versions/detail"),
        principal=principal,
        session=object(),
        container=container,
    )
    assert detail.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc,status_code",
    [(WorkflowNotFoundError("missing"), 404), (WorkflowAccessError("forbidden"), 403)],
)
async def test_admin_workflow_ui_routes_translate_service_errors(
    monkeypatch, exc, status_code
) -> None:
    principal = PrincipalContext(principal_id="tenant-admin")
    container = build_container()
    monkeypatch.setattr(
        admin_workflow_ui,
        "_build_admin_service",
        lambda session, container: FakeUIService(exc=exc),
    )

    with pytest.raises(HTTPException) as editor_error:
        await admin_workflow_ui.workflow_draft_editor_page(
            workflow_draft_id=uuid4(),
            request=build_request("/admin/workflows/drafts/editor"),
            principal=principal,
            session=object(),
            container=container,
        )
    with pytest.raises(HTTPException) as version_error:
        await admin_workflow_ui.workflow_version_detail_page(
            workflow_version_bundle_id=uuid4(),
            request=build_request("/admin/workflows/versions/detail"),
            principal=principal,
            session=object(),
            container=container,
        )

    assert editor_error.value.status_code == status_code
    assert version_error.value.status_code == status_code
