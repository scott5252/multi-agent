from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    PublishConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
    WorkflowRegistryService,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    PublishDraftRequest,
    RegistrySharingGrantCreateRequest,
    WorkflowDraftCreateRequest,
    WorkflowDraftSaveRequest,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)


def build_service(
    session, settings, filesystem_storage_provider
) -> WorkflowRegistryService:
    return WorkflowRegistryService(
        repository=WorkflowRegistryRepository(session),
        artifact_repository=ArtifactRepository(session),
        audit_service=AuditService(AuditRepository(session)),
        storage_provider=filesystem_storage_provider,
        artifact_prefix=settings.workflow_registry_artifact_prefix,
    )


async def test_create_and_save_workflow_draft(
    session, settings, filesystem_storage_provider, sample_workflow_document
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
    service = build_service(session, settings, filesystem_storage_provider)

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
    session, settings, filesystem_storage_provider, sample_workflow_document
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
    service = build_service(session, settings, filesystem_storage_provider)
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


async def test_validate_supersedes_previous_result_for_same_revision(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-3",
            request_id="req-3",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="validated-draft",
            display_name="Validated Draft",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "validated-draft",
                    "display_name": "Validated Draft",
                }
            ),
        ),
    )

    first = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    second = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    fetched = await service.get_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )

    assert first.validation_result_id != second.validation_result_id
    assert second.status == "passed"
    assert fetched.latest_validation is not None
    assert fetched.latest_validation.validation_result_id == second.validation_result_id


async def test_publish_requires_current_validation_and_creates_successor_seed(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-4",
            request_id="req-4",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="publishable-flow",
            display_name="Publishable Flow",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "publishable-flow",
                    "display_name": "Publishable Flow",
                }
            ),
        ),
    )
    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )

    published = await service.publish_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id
        ),
    )
    successor = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="publishable-flow",
            display_name="Publishable Flow",
            created_from_version_id=published.workflow_version_bundle_id,
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "publishable-flow",
                    "display_name": "Publishable Flow",
                }
            ),
        ),
    )

    assert published.display_version == "v1"
    assert published.compiled_bundle_digest is not None
    assert successor.created_from_version_id == published.workflow_version_bundle_id
    assert successor.workflow_lineage_id == created.workflow_lineage_id


async def test_publish_rejects_superseded_validation_results(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-5",
            request_id="req-5",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="stale-validation",
            display_name="Stale Validation",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "stale-validation",
                    "display_name": "Stale Validation",
                }
            ),
        ),
    )
    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=1,
            display_name="Stale Validation Updated",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "stale-validation",
                    "display_name": "Stale Validation Updated",
                }
            ),
            change_summary="Invalidate earlier validation",
        ),
    )

    with pytest.raises(PublishConflictError):
        await service.publish_draft(
            principal=principal,
            workflow_draft_id=created.workflow_draft_id,
            payload=PublishDraftRequest(
                validation_result_id=validation.validation_result_id
            ),
        )


async def test_create_platform_sharing_grant_requires_platform_version(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-6",
            request_id="req-6",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="shareable-flow",
            display_name="Shareable Flow",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "shareable-flow",
                    "display_name": "Shareable Flow",
                }
            ),
        ),
    )
    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    published = await service.publish_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id
        ),
    )

    grant = await service.create_sharing_grant(
        principal=principal,
        workflow_version_bundle_id=published.workflow_version_bundle_id,
        payload=RegistrySharingGrantCreateRequest(
            grantee_tenant_id=settings.local_principal_catalog_json[
                "tenant-admin-acme"
            ].tenant_id
        ),
    )

    assert grant.workflow_version_bundle_id == published.workflow_version_bundle_id
    assert grant.status == "active"


async def test_get_version_blocks_tenant_without_sharing_grant(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    platform_principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-7",
            request_id="req-7",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    tenant_principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "tenant-admin-acme",
            trace_id="trace-8",
            request_id="req-8",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=platform_principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="restricted-version",
            display_name="Restricted Version",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "restricted-version",
                    "display_name": "Restricted Version",
                }
            ),
        ),
    )
    validation = await service.validate_draft(
        principal=platform_principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    published = await service.publish_draft(
        principal=platform_principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id
        ),
    )

    with pytest.raises(WorkflowAccessError):
        await service.get_version(
            principal=tenant_principal,
            workflow_version_bundle_id=published.workflow_version_bundle_id,
        )


async def test_create_draft_from_missing_version_raises_not_found(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-9",
            request_id="req-9",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)

    with pytest.raises(WorkflowNotFoundError):
        await service.create_draft(
            principal=principal,
            payload=WorkflowDraftCreateRequest(
                scope_type="platform",
                workflow_kind="main_workflow",
                slug="missing-source",
                display_name="Missing Source",
                created_from_version_id=uuid4(),
                document=sample_workflow_document.model_copy(
                    update={
                        "workflow_key": "missing-source",
                        "display_name": "Missing Source",
                    }
                ),
            ),
        )


async def test_publish_rejects_missing_validation_result(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-10",
            request_id="req-10",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="missing-validation-result",
            display_name="Missing Validation Result",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "missing-validation-result",
                    "display_name": "Missing Validation Result",
                }
            ),
        ),
    )

    with pytest.raises(PublishConflictError):
        await service.publish_draft(
            principal=principal,
            workflow_draft_id=created.workflow_draft_id,
            payload=PublishDraftRequest(validation_result_id=uuid4()),
        )


async def test_create_sharing_grant_is_idempotent_for_same_tenant(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
    sample_workflow_document,
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-11",
            request_id="req-11",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="idempotent-share",
            display_name="Idempotent Share",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "idempotent-share",
                    "display_name": "Idempotent Share",
                }
            ),
        ),
    )
    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    published = await service.publish_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id
        ),
    )

    first = await service.create_sharing_grant(
        principal=principal,
        workflow_version_bundle_id=published.workflow_version_bundle_id,
        payload=RegistrySharingGrantCreateRequest(
            grantee_tenant_id=seeded_tenant.tenant_id
        ),
    )
    second = await service.create_sharing_grant(
        principal=principal,
        workflow_version_bundle_id=published.workflow_version_bundle_id,
        payload=RegistrySharingGrantCreateRequest(
            grantee_tenant_id=seeded_tenant.tenant_id
        ),
    )

    assert first.registry_sharing_grant_id == second.registry_sharing_grant_id
