from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    WorkflowRegistryService,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftCreateRequest,
    WorkflowDraftSaveRequest,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)


def build_service(session, settings) -> WorkflowRegistryService:
    return WorkflowRegistryService(
        repository=WorkflowRegistryRepository(session),
        audit_service=AuditService(AuditRepository(session)),
    )


async def test_create_and_save_workflow_draft(
    session, settings, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-1",
            request_id="req-1",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings)

    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="customer-intake",
            display_name="Customer Intake",
            document=sample_workflow_document,
        ),
    )

    saved = await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=created.current_revision_number,
            display_name="Customer Intake Updated",
            document=sample_workflow_document.model_copy(
                update={"display_name": "Customer Intake Updated"}
            ),
            change_summary="Refine display name",
        ),
    )

    assert created.current_revision_number == 1
    assert saved.current_revision_number == 2
    assert saved.display_name == "Customer Intake Updated"


async def test_save_rejects_stale_revision(
    session, settings, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-2",
            request_id="req-2",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="stale-draft",
            display_name="Stale Draft",
            document=sample_workflow_document.model_copy(
                update={"workflow_key": "stale-draft", "display_name": "Stale Draft"}
            ),
        ),
    )
    await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=1,
            display_name="Stale Draft Updated",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "stale-draft",
                    "display_name": "Stale Draft Updated",
                }
            ),
        ),
    )

    with pytest.raises(DraftConflictError):
        await service.save_draft(
            principal=principal,
            workflow_draft_id=created.workflow_draft_id,
            payload=WorkflowDraftSaveRequest(
                base_revision_number=1,
                display_name="Older Save",
                document=sample_workflow_document.model_copy(
                    update={"workflow_key": "stale-draft", "display_name": "Older Save"}
                ),
            ),
        )
