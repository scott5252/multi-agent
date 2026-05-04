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
from multi_agent_platform.api.schemas.workflow_editor import PublishGateRequest
from multi_agent_platform.api.schemas.workflow_registry import (
    CopyDraftRequest,
    PublishDraftRequest,
    RegistrySharingGrantCreateRequest,
    RestoreRevisionRequest,
    WorkflowDraftCreateRequest,
    WorkflowDraftSaveRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    TestSuiteRequirement as BuilderTestSuiteRequirement,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)
from multi_agent_platform.testing.agent_bench.service import AgentTestBenchService


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


def _principal(settings, catalog_key: str):
    return (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            catalog_key,
            trace_id=f"trace-{catalog_key}",
            request_id=f"req-{catalog_key}",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )


async def _create_required_suite(
    session,
    *,
    tenant_id,
    target_id: str,
    actor_principal_id: str,
    target_version: str | None = None,
    name: str = "QA024 Required Suite",
):
    service = AgentTestBenchService(AgentTestRepository(session))
    suite = await service.create_suite(
        tenant_id=tenant_id,
        name=name,
        description="Repository-backed workflow publish evidence.",
        target_type="workflow_draft",
        target_id=target_id,
        target_version=target_version,
        actor_principal_id=actor_principal_id,
        required_for_publish=False,
    )
    await service.create_case(
        suite_id=suite.agent_test_suite_id,
        tenant_id=tenant_id,
        name="Current revision smoke",
        actor_principal_id=actor_principal_id,
        fixture={"request": "qa024"},
    )
    return service, suite


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


async def test_builder_service_flows_cover_lookups_revisions_gate_and_copy(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-builder",
            request_id="req-builder",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    document = sample_workflow_document.model_copy(
        update={
            "workflow_key": "builder-service-flow",
            "display_name": "Builder Service Flow",
        }
    )
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="builder-service-flow",
            display_name="Builder Service Flow",
            document=document,
        ),
    )
    saved = await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=created.current_revision_number,
            display_name="Builder Service Flow Updated",
            document=document.model_copy(update={"display_name": "Updated"}),
        ),
    )

    lookups = await service.get_editor_lookups(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        lookup_kind="contracts",
        search="intake",
    )
    preview = await service.get_graph_preview(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    revisions = await service.list_draft_revisions(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    restored = await service.restore_revision(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=RestoreRevisionRequest(
            revision_number=1,
            base_revision_number=saved.current_revision_number,
        ),
    )
    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    gate = await service.evaluate_publish_gate(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishGateRequest(
            validation_result_id=str(validation.validation_result_id)
        ),
    )
    published = await service.publish_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id,
            publish_gate_id=gate.publish_gate_id,
        ),
    )
    copied = await service.copy_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=CopyDraftRequest(
            new_slug="builder-service-flow-copy",
            display_name="Builder Service Flow Copy",
        ),
    )

    assert lookups.groups[0].options[0].value == "intake-request"
    assert preview.summary.entry_node_id == "node:triage-node"
    assert len(revisions.revisions) == 2
    assert restored.current_revision_number == 3
    assert gate.status == "ready"
    assert published.summary_json["publish_gate_digest"] == gate.digest
    assert copied.slug == "builder-service-flow-copy"


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


async def test_list_registry_filters_publish_readiness_and_search(
    session, settings, filesystem_storage_provider, sample_workflow_document
) -> None:
    principal = (
        LocalPrincipalCatalog(settings.local_principal_catalog_json)
        .as_principal_context(
            "platform-admin",
            trace_id="trace-list-filters",
            request_id="req-list-filters",
        )
        .model_copy(update={"principal_identity_id": uuid4()})
    )
    service = build_service(session, settings, filesystem_storage_provider)
    needle = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="needle-flow",
            display_name="Needle Flow",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "needle-flow",
                    "display_name": "Needle Flow",
                }
            ),
        ),
    )
    await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="platform",
            workflow_kind="main_workflow",
            slug="ordinary-flow",
            display_name="Ordinary Flow",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "ordinary-flow",
                    "display_name": "Ordinary Flow",
                }
            ),
        ),
    )
    await service.validate_draft(
        principal=principal,
        workflow_draft_id=needle.workflow_draft_id,
    )

    ready_items = await service.list_registry(
        principal=principal,
        status="publish_ready",
    )
    search_items = await service.list_registry(
        principal=principal,
        search_query="needle",
    )

    assert [item.slug for item in ready_items] == ["needle-flow"]
    assert [item.slug for item in search_items] == ["needle-flow"]


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


async def test_required_test_manual_status_does_not_bypass_repository_evidence(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
    sample_workflow_document,
) -> None:
    principal = _principal(settings, "tenant-admin-acme")
    service = build_service(session, settings, filesystem_storage_provider)
    document = sample_workflow_document.model_copy(
        update={
            "workflow_key": "manual-status-bypass",
            "display_name": "Manual Status Bypass",
            "test_requirements": [
                BuilderTestSuiteRequirement(
                    requirement_key="smoke",
                    suite_id=str(uuid4()),
                    latest_result_status="passed",
                )
            ],
        }
    )
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="tenant",
            tenant_id=seeded_tenant.tenant_id,
            workflow_kind="main_workflow",
            slug="manual-status-bypass",
            display_name="Manual Status Bypass",
            document=document,
        ),
    )

    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    gate = await service.evaluate_publish_gate(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishGateRequest(
            validation_result_id=str(validation.validation_result_id)
        ),
    )

    assert validation.status == "failed"
    assert validation.required_test_summary["missing_count"] == 1
    assert gate.status == "blocked"
    assert gate.required_test_summary.missing_count == 1
    assert any(
        finding.code == "reference.required_test.not_passing"
        for finding in validation.findings
    )


async def test_required_test_current_passing_evidence_allows_publish(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
    sample_workflow_document,
) -> None:
    principal = _principal(settings, "tenant-admin-acme")
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="tenant",
            tenant_id=seeded_tenant.tenant_id,
            workflow_kind="main_workflow",
            slug="current-evidence",
            display_name="Current Evidence",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "current-evidence",
                    "display_name": "Current Evidence",
                }
            ),
        ),
    )
    agent_service, suite = await _create_required_suite(
        session,
        tenant_id=seeded_tenant.tenant_id,
        target_id=str(created.workflow_draft_id),
        actor_principal_id=principal.principal_id,
    )
    document = sample_workflow_document.model_copy(
        update={
            "workflow_key": "current-evidence",
            "display_name": "Current Evidence",
            "test_requirements": [
                BuilderTestSuiteRequirement(
                    requirement_key="smoke",
                    suite_id=str(suite.agent_test_suite_id),
                    latest_result_status="missing",
                )
            ],
        }
    )
    saved = await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=created.current_revision_number,
            display_name="Current Evidence",
            document=document,
            change_summary="Require repository evidence",
        ),
    )
    run = await agent_service.launch_run(
        suite_id=suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        actor_principal_id=principal.principal_id,
        safe_mode="mock_model",
        target_version=str(saved.latest_revision.workflow_draft_revision_id),
        idempotency_key="qa024-current-evidence",
        trace_id=principal.trace_id,
    )

    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    assert validation.status == "passed", (
        validation.findings,
        validation.reference_readiness,
        validation.required_test_summary,
    )
    fetched_validation = await service.repository.get_validation_result(
        validation.validation_result_id
    )
    assert fetched_validation is not None
    await session.refresh(fetched_validation)
    assert fetched_validation.blocking_issue_count == 0
    published = await service.publish_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishDraftRequest(
            validation_result_id=validation.validation_result_id,
        ),
    )

    assert run.status.value == "passed"
    assert validation.status == "passed"
    assert published.summary_json["required_test_evidence"]["passing_count"] == 1


async def test_required_test_stale_wrong_target_and_cross_tenant_evidence_block(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
    sample_workflow_document,
) -> None:
    principal = _principal(settings, "tenant-admin-acme")
    service = build_service(session, settings, filesystem_storage_provider)
    created = await service.create_draft(
        principal=principal,
        payload=WorkflowDraftCreateRequest(
            scope_type="tenant",
            tenant_id=seeded_tenant.tenant_id,
            workflow_kind="main_workflow",
            slug="stale-evidence",
            display_name="Stale Evidence",
            document=sample_workflow_document.model_copy(
                update={
                    "workflow_key": "stale-evidence",
                    "display_name": "Stale Evidence",
                }
            ),
        ),
    )
    agent_service, stale_suite = await _create_required_suite(
        session,
        tenant_id=seeded_tenant.tenant_id,
        target_id=str(created.workflow_draft_id),
        actor_principal_id=principal.principal_id,
        name="QA024 Stale Suite",
    )
    wrong_target_service, wrong_target_suite = await _create_required_suite(
        session,
        tenant_id=seeded_tenant.tenant_id,
        target_id=str(uuid4()),
        actor_principal_id=principal.principal_id,
        name="QA024 Wrong Target Suite",
    )
    _ = wrong_target_service
    foreign_tenant = Tenant(slug="globex", display_name="Globex")
    session.add(foreign_tenant)
    await session.flush()
    foreign_service, foreign_suite = await _create_required_suite(
        session,
        tenant_id=foreign_tenant.tenant_id,
        target_id=str(created.workflow_draft_id),
        actor_principal_id=principal.principal_id,
        name="QA024 Foreign Suite",
    )
    _ = foreign_service
    document = sample_workflow_document.model_copy(
        update={
            "workflow_key": "stale-evidence",
            "display_name": "Stale Evidence",
            "test_requirements": [
                BuilderTestSuiteRequirement(
                    requirement_key="stale",
                    suite_id=str(stale_suite.agent_test_suite_id),
                ),
                BuilderTestSuiteRequirement(
                    requirement_key="wrong-target",
                    suite_id=str(wrong_target_suite.agent_test_suite_id),
                ),
                BuilderTestSuiteRequirement(
                    requirement_key="foreign",
                    suite_id=str(foreign_suite.agent_test_suite_id),
                ),
            ],
        }
    )
    saved = await service.save_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=created.current_revision_number,
            display_name="Stale Evidence",
            document=document,
            change_summary="Require stale evidence checks",
        ),
    )
    await agent_service.launch_run(
        suite_id=stale_suite.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
        actor_principal_id=principal.principal_id,
        safe_mode="mock_model",
        target_version="older-revision",
        idempotency_key="qa024-stale-evidence",
        trace_id=principal.trace_id,
    )

    validation = await service.validate_draft(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
    )
    gate = await service.evaluate_publish_gate(
        principal=principal,
        workflow_draft_id=created.workflow_draft_id,
        payload=PublishGateRequest(
            validation_result_id=str(validation.validation_result_id)
        ),
    )

    assert saved.current_revision_number == 2
    assert validation.status == "failed"
    assert gate.required_test_summary.stale_count == 2
    assert gate.required_test_summary.missing_count == 1
    safe_summaries = " ".join(
        snapshot.safe_summary or ""
        for snapshot in gate.reference_readiness
        if snapshot.reference_type == "test_suite"
    )
    assert "Globex" not in safe_summaries
    assert "QA024 Foreign Suite" not in safe_summaries


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
