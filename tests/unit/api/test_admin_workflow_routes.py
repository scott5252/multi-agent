from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from multi_agent_platform.admin.workflow_registry.service import (
    ArtifactPersistenceError,
    DraftConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.routers import admin_workflows
from multi_agent_platform.api.schemas.workflow_registry import (
    PublishDraftRequest,
    RegistrySharingGrantCreateRequest,
    WorkflowDraftCreateRequest,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowDraftSaveRequest,
    WorkflowRegistryItem,
    WorkflowScopeType,
    WorkflowVersionResponse,
    WorkflowVisibilityStatus,
)
from multi_agent_platform.auth.principal import PrincipalContext


def build_draft_response(sample_workflow_document) -> WorkflowDraftResponse:
    revision_id = uuid4()
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    return WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        scope_type=WorkflowScopeType.TENANT,
        workflow_kind="main_workflow",
        status="active",
        current_revision_number=1,
        latest_revision=WorkflowDraftRevisionResponse(
            workflow_draft_revision_id=revision_id,
            revision_number=1,
            document_sha256="abc123",
            created_at=now,
        ),
        document=sample_workflow_document,
        updated_at=now,
    )


def build_version_response() -> WorkflowVersionResponse:
    now = __import__("datetime").datetime.now(__import__("datetime").UTC)
    return WorkflowVersionResponse(
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


class FakeAdminService:
    def __init__(self, *, result=None, exc: Exception | None = None) -> None:
        self.result = result
        self.exc = exc

    async def list_workflows(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def create_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def get_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def save_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def validate_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def publish_workflow_draft(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def get_workflow_version(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result

    async def create_workflow_sharing_grant(self, **kwargs):
        if self.exc is not None:
            raise self.exc
        return self.result


@pytest.mark.asyncio
async def test_admin_workflow_json_routes_map_service_results(
    monkeypatch, sample_workflow_document
):
    principal = PrincipalContext(principal_id="tenant-admin")
    draft = build_draft_response(sample_workflow_document)
    version = build_version_response()
    registry_item = WorkflowRegistryItem(
        workflow_lineage_id=uuid4(),
        workflow_draft_id=draft.workflow_draft_id,
        slug="customer-intake",
        display_name="Customer Intake",
        workflow_kind="main_workflow",
        scope_type=WorkflowScopeType.TENANT,
        visibility_status=WorkflowVisibilityStatus.DRAFT,
        current_revision_number=1,
        updated_at=draft.updated_at,
    )
    validation = SimpleNamespace(
        validation_result_id=uuid4(),
        status="passed",
        blocking_issue_count=0,
        advisory_issue_count=0,
        findings=[],
    )
    grant = SimpleNamespace(
        registry_sharing_grant_id=uuid4(),
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        grantee_tenant_id=uuid4(),
        status="active",
        created_at=version.published_at,
    )

    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(result=[registry_item]),
    )
    listed = await admin_workflows.list_workflows(
        principal=principal,
        session=object(),
        container=object(),
    )
    assert listed.items[0].slug == "customer-intake"

    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(result=draft),
    )
    created = await admin_workflows.create_workflow_draft(
        payload=WorkflowDraftCreateRequest(
            scope_type="tenant",
            workflow_kind="main_workflow",
            slug="customer-intake",
            display_name="Customer Intake",
            document=sample_workflow_document,
        ),
        principal=principal,
        session=object(),
        container=object(),
    )
    fetched = await admin_workflows.get_workflow_draft(
        workflow_draft_id=draft.workflow_draft_id,
        principal=principal,
        session=object(),
        container=object(),
    )
    saved = await admin_workflows.save_workflow_draft(
        workflow_draft_id=draft.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=1,
            display_name="Customer Intake",
            document=sample_workflow_document,
        ),
        principal=principal,
        session=object(),
        container=object(),
    )
    assert created.workflow_draft_id == draft.workflow_draft_id
    assert fetched.workflow_draft_id == draft.workflow_draft_id
    assert saved.workflow_draft_id == draft.workflow_draft_id

    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(result=validation),
    )
    validated = await admin_workflows.validate_workflow_draft(
        workflow_draft_id=draft.workflow_draft_id,
        principal=principal,
        session=object(),
        container=object(),
    )
    assert validated.status == "passed"

    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(result=version),
    )
    published = await admin_workflows.publish_workflow_draft(
        workflow_draft_id=draft.workflow_draft_id,
        payload=PublishDraftRequest(validation_result_id=uuid4()),
        principal=principal,
        session=object(),
        container=object(),
    )
    version_detail = await admin_workflows.get_workflow_version(
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        principal=principal,
        session=object(),
        container=object(),
    )
    assert published.display_version == "v1"
    assert version_detail.display_version == "v1"

    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(result=grant),
    )
    shared = await admin_workflows.create_workflow_sharing_grant(
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        payload=RegistrySharingGrantCreateRequest(grantee_tenant_id=uuid4()),
        principal=principal,
        session=object(),
        container=object(),
    )
    assert shared.status == "active"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("func_name", "kwargs", "exc", "status_code"),
    [
        ("list_workflows", {}, WorkflowAccessError("forbidden"), 403),
        (
            "create_workflow_draft",
            {
                "payload": lambda doc: WorkflowDraftCreateRequest(
                    scope_type="tenant",
                    workflow_kind="main_workflow",
                    slug="customer-intake",
                    display_name="Customer Intake",
                    document=doc,
                )
            },
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "create_workflow_draft",
            {
                "payload": lambda doc: WorkflowDraftCreateRequest(
                    scope_type="tenant",
                    workflow_kind="main_workflow",
                    slug="customer-intake",
                    display_name="Customer Intake",
                    document=doc,
                )
            },
            RuntimeError("conflict"),
            409,
        ),
        (
            "get_workflow_draft",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowNotFoundError("missing"),
            404,
        ),
        (
            "save_workflow_draft",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda doc: WorkflowDraftSaveRequest(
                    base_revision_number=1,
                    display_name="Customer Intake",
                    document=doc,
                ),
            },
            DraftConflictError("stale"),
            409,
        ),
        (
            "validate_workflow_draft",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "publish_workflow_draft",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda _doc: PublishDraftRequest(
                    validation_result_id=uuid4()
                ),
            },
            ArtifactPersistenceError("artifact"),
            503,
        ),
        (
            "get_workflow_version",
            {"workflow_version_bundle_id": lambda: uuid4()},
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "create_workflow_sharing_grant",
            {
                "workflow_version_bundle_id": lambda: uuid4(),
                "payload": lambda _doc: RegistrySharingGrantCreateRequest(
                    grantee_tenant_id=uuid4()
                ),
            },
            WorkflowNotFoundError("missing"),
            404,
        ),
    ],
)
async def test_admin_workflow_json_routes_translate_exceptions(
    monkeypatch,
    sample_workflow_document,
    func_name,
    kwargs,
    exc,
    status_code,
) -> None:
    principal = PrincipalContext(principal_id="tenant-admin")
    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeAdminService(exc=exc),
    )
    params = {
        key: value(sample_workflow_document) if key == "payload" else value()
        for key, value in kwargs.items()
    }
    with pytest.raises(HTTPException) as raised:
        await getattr(admin_workflows, func_name)(
            principal=principal,
            session=object(),
            container=object(),
            **params,
        )

    assert raised.value.status_code == status_code
