from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException

from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.routers import admin_workflows
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
