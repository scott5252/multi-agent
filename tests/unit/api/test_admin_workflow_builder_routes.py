from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException

from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.routers import admin_react, admin_workflows
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupResponse,
    GraphPreviewResponse,
    PublishGateRequest,
    PublishGateResponse,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    CopyDraftRequest,
    DraftRevisionListResponse,
    RestoreRevisionRequest,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowRegistryItem,
    WorkflowScopeType,
    WorkflowVersionResponse,
    WorkflowVisibilityStatus,
)
from multi_agent_platform.auth.principal import PrincipalContext


class FakeBuilderAdminService:
    async def get_workflow_editor_lookups(self, **kwargs):
        return EditorLookupResponse()

    async def get_workflow_graph_preview(self, **kwargs):
        return GraphPreviewResponse()

    async def list_workflow_draft_revisions(self, **kwargs):
        return DraftRevisionListResponse(
            workflow_draft_id=kwargs["workflow_draft_id"],
            current_revision_number=1,
        )

    async def evaluate_workflow_publish_gate(self, **kwargs):
        workflow_draft_id = kwargs["workflow_draft_id"]
        return PublishGateResponse(
            publish_gate_id="gate",
            workflow_draft_id=str(workflow_draft_id),
            workflow_draft_revision_id=str(uuid4()),
            document_sha256="a" * 64,
            status="ready",
            required_test_summary=RequiredTestSummary(),
            digest="digest",
        )


class RaisingBuilderAdminService:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    async def get_workflow_editor_lookups(self, **kwargs):
        raise self.exc

    async def get_workflow_graph_preview(self, **kwargs):
        raise self.exc

    async def list_workflow_draft_revisions(self, **kwargs):
        raise self.exc

    async def restore_workflow_revision(self, **kwargs):
        raise self.exc

    async def copy_workflow_draft(self, **kwargs):
        raise self.exc

    async def evaluate_workflow_publish_gate(self, **kwargs):
        raise self.exc


class FakeReactWorkflowBuilderService:
    def __init__(
        self,
        *,
        draft: WorkflowDraftResponse | None,
        registry_items: list[WorkflowRegistryItem],
        version: WorkflowVersionResponse | None = None,
    ) -> None:
        self.draft = draft
        self.registry_items = registry_items
        self.version = version
        self.gate_calls = 0
        self.latest_version_calls = 0

    async def list_workflows(self, **kwargs):
        return self.registry_items

    async def get_workflow_version(self, **kwargs):
        if self.version is None:
            raise WorkflowNotFoundError("workflow version not found")
        return self.version

    async def get_workflow_draft(self, **kwargs):
        if self.draft is None:
            raise WorkflowNotFoundError("workflow draft not found")
        return self.draft

    async def get_workflow_editor_lookups(self, **kwargs):
        return EditorLookupResponse()

    async def get_workflow_graph_preview(self, **kwargs):
        return GraphPreviewResponse()

    async def list_workflow_draft_revisions(self, **kwargs):
        return DraftRevisionListResponse(
            workflow_draft_id=kwargs["workflow_draft_id"],
            current_revision_number=self.draft.current_revision_number
            if self.draft
            else 1,
        )

    async def evaluate_workflow_publish_gate(self, **kwargs):
        self.gate_calls += 1
        workflow_draft_id = kwargs["workflow_draft_id"]
        revision_id = (
            self.draft.latest_revision.workflow_draft_revision_id
            if self.draft
            else uuid4()
        )
        return PublishGateResponse(
            publish_gate_id="gate",
            workflow_draft_id=str(workflow_draft_id),
            workflow_draft_revision_id=str(revision_id),
            document_sha256="a" * 64,
            status="ready",
            required_test_summary=RequiredTestSummary(),
            digest="digest",
        )

    async def get_latest_published_workflow_version_for_lineage(self, **kwargs):
        self.latest_version_calls += 1
        return self.version


class RaisingReactWorkflowBuilderService(FakeReactWorkflowBuilderService):
    def __init__(self, exc: Exception) -> None:
        self.exc = exc
        super().__init__(draft=None, registry_items=[])

    async def get_workflow_draft(self, **kwargs):
        raise self.exc


def _react_draft(sample_workflow_document, *, status: str) -> WorkflowDraftResponse:
    now = datetime.now(UTC)
    tenant_id = uuid4()
    return WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        scope_type=WorkflowScopeType.TENANT,
        tenant_id=tenant_id,
        workflow_kind="main_workflow",
        status=status,
        current_revision_number=1,
        latest_revision=WorkflowDraftRevisionResponse(
            workflow_draft_revision_id=uuid4(),
            revision_number=1,
            document_sha256="a" * 64,
            created_at=now,
        ),
        document=sample_workflow_document,
        updated_at=now,
    )


def _react_version(
    *,
    draft: WorkflowDraftResponse,
    published_from_revision_id,
) -> WorkflowVersionResponse:
    now = datetime.now(UTC)
    return WorkflowVersionResponse(
        workflow_version_bundle_id=uuid4(),
        workflow_lineage_id=draft.workflow_lineage_id,
        slug=draft.slug,
        display_name=draft.display_name,
        display_version="v1",
        scope_type=draft.scope_type,
        tenant_id=draft.tenant_id,
        status="published",
        compiled_bundle_digest="b" * 64,
        compiler_version="workflow-registry-test",
        published_from_draft_id=draft.workflow_draft_id,
        published_from_revision_id=published_from_revision_id,
        published_at=now,
    )


def _react_registry_draft_item(draft: WorkflowDraftResponse) -> WorkflowRegistryItem:
    return WorkflowRegistryItem(
        workflow_lineage_id=draft.workflow_lineage_id,
        workflow_draft_id=draft.workflow_draft_id,
        slug=draft.slug,
        display_name=draft.display_name,
        workflow_kind=draft.workflow_kind,
        scope_type=draft.scope_type,
        tenant_id=draft.tenant_id,
        visibility_status=WorkflowVisibilityStatus.DRAFT,
        current_revision_number=draft.current_revision_number,
        latest_validation_status="passed",
        publish_readiness_status="ready",
        updated_at=draft.updated_at,
    )


def _react_registry_version_item(
    *,
    draft: WorkflowDraftResponse,
    version: WorkflowVersionResponse,
) -> WorkflowRegistryItem:
    return WorkflowRegistryItem(
        workflow_lineage_id=draft.workflow_lineage_id,
        workflow_version_bundle_id=version.workflow_version_bundle_id,
        slug=draft.slug,
        display_name=draft.display_name,
        workflow_kind=draft.workflow_kind,
        scope_type=draft.scope_type,
        tenant_id=draft.tenant_id,
        visibility_status=WorkflowVisibilityStatus.PUBLISHED,
        display_version=version.display_version,
        publish_readiness_status="published",
        updated_at=version.published_at,
    )


def test_builder_payload_size_guard_rejects_large_payloads(monkeypatch) -> None:
    admin_workflows._ensure_payload_size(object())

    class OversizedPayload:
        def model_dump_json(self) -> str:
            return "too-large"

    monkeypatch.setattr(admin_workflows, "MAX_BUILDER_PAYLOAD_BYTES", 1)

    with pytest.raises(HTTPException) as raised:
        admin_workflows._ensure_payload_size(OversizedPayload())

    assert raised.value.status_code == 413


@pytest.mark.asyncio
async def test_react_builder_payload_returns_empty_without_registry_records() -> None:
    service = FakeReactWorkflowBuilderService(draft=None, registry_items=[])

    payload = await admin_react._workflow_builder_payload(
        scope=ReactAdminScope(scope_type="tenant", tenant_id=uuid4(), label="Acme"),
        principal=PrincipalContext(principal_id="tenant-admin-acme"),
        service=service,
    )

    assert payload.draft is None
    assert payload.state is not None
    assert payload.state.state == "empty"
    assert service.gate_calls == 0
    assert service.latest_version_calls == 0


@pytest.mark.asyncio
async def test_react_builder_payload_uses_active_draft_and_latest_version(
    sample_workflow_document,
) -> None:
    draft = _react_draft(sample_workflow_document, status="active")
    version = _react_version(
        draft=draft,
        published_from_revision_id=uuid4(),
    )
    service = FakeReactWorkflowBuilderService(
        draft=draft,
        registry_items=[_react_registry_draft_item(draft)],
        version=version,
    )

    payload = await admin_react._workflow_builder_payload(
        scope=ReactAdminScope(
            scope_type="tenant",
            tenant_id=draft.tenant_id,
            label="Acme",
        ),
        principal=PrincipalContext(
            principal_id="tenant-admin-acme",
            tenant_id=draft.tenant_id,
        ),
        service=service,
    )

    assert payload.draft is not None
    assert payload.draft.workflow_draft_id == str(draft.workflow_draft_id)
    assert payload.version_detail is not None
    assert payload.version_detail.workflow_version_bundle_id == str(
        version.workflow_version_bundle_id
    )
    assert payload.publish_readiness is not None
    assert payload.publish_readiness.decision == "confirmation_required"
    assert service.gate_calls == 1
    assert service.latest_version_calls == 1


@pytest.mark.asyncio
async def test_react_builder_payload_uses_explicit_draft_id(
    sample_workflow_document,
) -> None:
    draft = _react_draft(sample_workflow_document, status="active")
    service = FakeReactWorkflowBuilderService(
        draft=draft,
        registry_items=[],
        version=None,
    )

    payload = await admin_react._workflow_builder_payload(
        scope=ReactAdminScope(
            scope_type="tenant",
            tenant_id=draft.tenant_id,
            label="Acme",
        ),
        principal=PrincipalContext(
            principal_id="tenant-admin-acme",
            tenant_id=draft.tenant_id,
        ),
        service=service,
        workflow_draft_id=draft.workflow_draft_id,
    )

    assert payload.draft is not None
    assert payload.draft.workflow_draft_id == str(draft.workflow_draft_id)
    assert service.gate_calls == 1


@pytest.mark.asyncio
async def test_react_builder_payload_selects_published_source_without_gate(
    sample_workflow_document,
) -> None:
    draft = _react_draft(sample_workflow_document, status="published_source")
    version = _react_version(
        draft=draft,
        published_from_revision_id=draft.latest_revision.workflow_draft_revision_id,
    )
    service = FakeReactWorkflowBuilderService(
        draft=draft,
        registry_items=[_react_registry_version_item(draft=draft, version=version)],
        version=version,
    )

    payload = await admin_react._workflow_builder_payload(
        scope=ReactAdminScope(
            scope_type="tenant",
            tenant_id=draft.tenant_id,
            label="Acme",
        ),
        principal=PrincipalContext(
            principal_id="tenant-admin-acme",
            tenant_id=draft.tenant_id,
        ),
        service=service,
    )

    assert payload.draft is not None
    assert payload.draft.workflow_draft_id == str(draft.workflow_draft_id)
    assert payload.version_detail is not None
    assert payload.version_detail.workflow_version_bundle_id == str(
        version.workflow_version_bundle_id
    )
    assert payload.publish_readiness is not None
    assert payload.publish_readiness.decision == "accepted"
    assert payload.publish_readiness.published_bundle_summary is not None
    assert service.gate_calls == 0
    assert service.latest_version_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "status_code"),
    [
        (WorkflowNotFoundError("missing"), 404),
        (WorkflowAccessError("forbidden"), 403),
        (DraftConflictError("stale"), 409),
    ],
)
async def test_react_builder_payload_translates_service_errors(
    exc, status_code
) -> None:
    with pytest.raises(HTTPException) as raised:
        await admin_react._workflow_builder_payload(
            scope=ReactAdminScope(scope_type="tenant", tenant_id=uuid4(), label="Acme"),
            principal=PrincipalContext(principal_id="tenant-admin-acme"),
            service=RaisingReactWorkflowBuilderService(exc),
            workflow_draft_id=uuid4(),
        )

    assert raised.value.status_code == status_code


@pytest.mark.asyncio
async def test_workflow_builder_json_routes_map_service_results(monkeypatch) -> None:
    draft_id = uuid4()
    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: FakeBuilderAdminService(),
    )
    principal = PrincipalContext(principal_id="platform-admin")

    lookups = await admin_workflows.get_editor_lookups(
        principal=principal,
        session=object(),
        container=object(),
        workflow_draft_id=draft_id,
    )
    preview = await admin_workflows.get_workflow_graph_preview(
        workflow_draft_id=draft_id,
        principal=principal,
        session=object(),
        container=object(),
    )
    revisions = await admin_workflows.list_workflow_draft_revisions(
        workflow_draft_id=draft_id,
        principal=principal,
        session=object(),
        container=object(),
    )
    gate = await admin_workflows.evaluate_workflow_publish_gate(
        workflow_draft_id=draft_id,
        principal=principal,
        session=object(),
        container=object(),
        payload=PublishGateRequest(),
    )

    assert lookups.groups == []
    assert preview.summary.node_count == 0
    assert revisions.current_revision_number == 1
    assert gate.status == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("func_name", "kwargs", "exc", "status_code"),
    [
        (
            "get_editor_lookups",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowNotFoundError("missing"),
            404,
        ),
        (
            "get_editor_lookups",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "get_workflow_graph_preview",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowNotFoundError("missing"),
            404,
        ),
        (
            "get_workflow_graph_preview",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "list_workflow_draft_revisions",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowNotFoundError("missing"),
            404,
        ),
        (
            "list_workflow_draft_revisions",
            {"workflow_draft_id": lambda: uuid4()},
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "restore_workflow_revision",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda: RestoreRevisionRequest(
                    revision_number=1,
                    base_revision_number=2,
                ),
            },
            DraftConflictError("stale"),
            409,
        ),
        (
            "restore_workflow_revision",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda: RestoreRevisionRequest(
                    revision_number=1,
                    base_revision_number=2,
                ),
            },
            WorkflowAccessError("forbidden"),
            403,
        ),
        (
            "copy_workflow_draft",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda: CopyDraftRequest(
                    new_slug="customer-intake-copy",
                    display_name="Customer Intake Copy",
                ),
            },
            RuntimeError("conflict"),
            409,
        ),
        (
            "copy_workflow_draft",
            {
                "workflow_draft_id": lambda: uuid4(),
                "payload": lambda: CopyDraftRequest(
                    new_slug="customer-intake-copy",
                    display_name="Customer Intake Copy",
                ),
            },
            WorkflowNotFoundError("missing"),
            404,
        ),
        (
            "evaluate_workflow_publish_gate",
            {"workflow_draft_id": lambda: uuid4(), "payload": lambda: None},
            DraftConflictError("stale"),
            409,
        ),
        (
            "evaluate_workflow_publish_gate",
            {"workflow_draft_id": lambda: uuid4(), "payload": lambda: None},
            WorkflowAccessError("forbidden"),
            403,
        ),
    ],
)
async def test_workflow_builder_json_routes_translate_exceptions(
    monkeypatch,
    func_name,
    kwargs,
    exc,
    status_code,
) -> None:
    monkeypatch.setattr(
        admin_workflows,
        "_build_admin_service",
        lambda session, container: RaisingBuilderAdminService(exc),
    )
    params = {key: value() for key, value in kwargs.items()}

    with pytest.raises(HTTPException) as raised:
        await getattr(admin_workflows, func_name)(
            principal=PrincipalContext(principal_id="platform-admin"),
            session=object(),
            container=object(),
            **params,
        )

    assert raised.value.status_code == status_code
