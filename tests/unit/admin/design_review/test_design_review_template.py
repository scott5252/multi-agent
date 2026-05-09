from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.design_review.service import DesignReviewAccessError
from multi_agent_platform.admin.design_review.template import (
    COUNCIL_REQUIRED_SUITE_NAME,
    COUNCIL_REQUIREMENT_KEY,
    build_design_review_template_service,
)
from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftSaveRequest
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
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


def _service(session, settings, filesystem_storage_provider):
    return build_design_review_template_service(
        session=session,
        storage_provider=filesystem_storage_provider,
        workflow_registry_artifact_prefix=settings.workflow_registry_artifact_prefix,
    )


async def test_template_install_creates_idempotent_workflow_and_evidence(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
) -> None:
    principal = _principal(settings, "tenant-admin-acme")
    service = _service(session, settings, filesystem_storage_provider)

    first = await service.install_council_template(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        idempotency_key="unit-template-install",
    )
    second = await service.install_council_template(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        idempotency_key="unit-template-install",
    )

    assert first.replayed is False
    assert second.replayed is True
    assert second.state.workflow_draft_id == first.state.workflow_draft_id
    assert first.state.status == "ready"
    assert first.state.required_evidence_status == "passing"
    assert first.state.ready_to_publish is True
    assert set(first.state.evidence_modes) == {"deterministic", "model backed safe"}
    assert first.state.deterministic_run_id is not None
    assert first.state.model_safe_run_id is not None

    repository = WorkflowRegistryRepository(session)
    assert first.state.workflow_draft_id is not None
    record = await repository.get_draft_record(first.state.workflow_draft_id)
    assert record is not None
    document = record.revision.authoring_document_json
    assert document["workflow_key"] == "design-reviewer-council"
    assert document["test_requirements"][0]["requirement_key"] == (
        COUNCIL_REQUIREMENT_KEY
    )

    assert first.state.agent_test_suite_id is not None
    agent_repository = AgentTestRepository(session)
    suite = await agent_repository.get_suite_for_tenant(
        suite_id=first.state.agent_test_suite_id,
        tenant_id=seeded_tenant.tenant_id,
    )
    assert suite is not None
    assert suite.name == COUNCIL_REQUIRED_SUITE_NAME
    cases = await agent_repository.list_cases_for_suite(suite.agent_test_suite_id)
    assert {case.name for case in cases} >= {
        "Four of five quorum success",
        "Three of four quorum success",
        "Manual resolution pause",
        "Model backed safe boundary",
    }


async def test_template_state_marks_evidence_stale_after_new_revision(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
) -> None:
    principal = _principal(settings, "tenant-admin-acme")
    service = _service(session, settings, filesystem_storage_provider)
    installed = await service.install_council_template(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        idempotency_key="unit-template-stale",
    )
    assert installed.state.workflow_draft_id is not None
    draft = await service.workflow_service.get_draft(
        principal=principal,
        workflow_draft_id=installed.state.workflow_draft_id,
    )
    await service.workflow_service.save_draft(
        principal=principal,
        workflow_draft_id=draft.workflow_draft_id,
        payload=WorkflowDraftSaveRequest(
            base_revision_number=draft.current_revision_number,
            display_name=draft.display_name,
            description="Refresh council template revision.",
            document=draft.document.model_copy(
                update={"description": "Refresh council template revision."}
            ),
            change_summary="Create stale evidence state.",
        ),
    )

    state = await service.get_council_template_state(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
    )

    assert state.status == "stale"
    assert state.required_evidence_status == "stale"
    assert state.ready_to_publish is False


async def test_template_install_rejects_cross_tenant_admin(
    session,
    settings,
    filesystem_storage_provider,
    seeded_tenant,
) -> None:
    principal = _principal(settings, "tenant-admin-acme").model_copy(
        update={"tenant_id": uuid4()}
    )
    service = _service(session, settings, filesystem_storage_provider)

    with pytest.raises(DesignReviewAccessError):
        await service.install_council_template(
            principal=principal,
            tenant_id=seeded_tenant.tenant_id,
            idempotency_key="unit-template-denied",
        )
