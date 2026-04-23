from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.auth.principal import PrincipalContext


class FakeWorkflowRegistryService:
    async def validate_draft(self, *, principal, workflow_draft_id):
        return {"principal": principal.principal_id, "draft_id": workflow_draft_id}

    async def publish_draft(self, *, principal, workflow_draft_id, payload):
        return {
            "principal": principal.principal_id,
            "draft_id": workflow_draft_id,
            "payload": payload,
        }

    async def get_version(self, *, principal, workflow_version_bundle_id):
        return {
            "principal": principal.principal_id,
            "version_id": workflow_version_bundle_id,
        }

    async def create_sharing_grant(
        self,
        *,
        principal,
        workflow_version_bundle_id,
        payload,
    ):
        return {
            "principal": principal.principal_id,
            "version_id": workflow_version_bundle_id,
            "payload": payload,
        }


class FakeAccessRepository:
    def __init__(self, existing=None) -> None:
        self.existing = existing

    async def get_support_override(self, support_override_request_id):
        return self.existing

    async def approve_support_override(
        self,
        support_override_request_id,
        *,
        approver_principal_id,
        expires_at,
    ):
        return SimpleNamespace(
            support_override_request_id=support_override_request_id,
            approver_principal_id=approver_principal_id,
            expires_at=expires_at,
        )


async def test_workflow_registry_service_requires_all_dependencies() -> None:
    service = AdminService()

    with pytest.raises(RuntimeError):
        service.workflow_registry_service()

    service.workflow_repository = object()  # type: ignore[assignment]
    with pytest.raises(RuntimeError):
        service.workflow_registry_service()

    service.artifact_repository = object()  # type: ignore[assignment]
    with pytest.raises(RuntimeError):
        service.workflow_registry_service()


async def test_validate_publish_version_and_grant_delegate_to_registry_service() -> (
    None
):
    principal = PrincipalContext(principal_id="platform-admin")
    admin_service = AdminService()
    admin_service.workflow_registry_service = lambda: FakeWorkflowRegistryService()  # type: ignore[method-assign]

    validate_result = await admin_service.validate_workflow_draft(
        principal=principal,
        workflow_draft_id=uuid4(),
    )
    publish_result = await admin_service.publish_workflow_draft(
        principal=principal,
        workflow_draft_id=uuid4(),
        payload={"validation_result_id": "validation-1"},
    )
    version_result = await admin_service.get_workflow_version(
        principal=principal,
        workflow_version_bundle_id=uuid4(),
    )
    grant_result = await admin_service.create_workflow_sharing_grant(
        principal=principal,
        workflow_version_bundle_id=uuid4(),
        payload={"grantee_tenant_id": "tenant-1"},
    )

    assert validate_result["principal"] == "platform-admin"
    assert publish_result["payload"]["validation_result_id"] == "validation-1"
    assert version_result["principal"] == "platform-admin"
    assert grant_result["payload"]["grantee_tenant_id"] == "tenant-1"


async def test_admin_service_access_repository_guards() -> None:
    service = AdminService()

    with pytest.raises(RuntimeError):
        await service.list_role_grants_for_tenant(uuid4())

    with pytest.raises(RuntimeError):
        await service.create_support_override(
            requester_principal_id=uuid4(),
            target_tenant_id=uuid4(),
            justification="Need support access",
            trace_id="trace-1",
            idempotency_key="idem-1",
        )


async def test_approve_support_override_handles_missing_and_self_approval() -> None:
    support_override_request_id = uuid4()
    requester_principal_id = uuid4()

    missing_service = AdminService(
        access_repository=FakeAccessRepository(existing=None)
    )
    assert (
        await missing_service.approve_support_override(
            support_override_request_id=support_override_request_id,
            approver_principal_id=uuid4(),
        )
        is None
    )

    existing = SimpleNamespace(requester_principal_id=requester_principal_id)
    existing_service = AdminService(access_repository=FakeAccessRepository(existing))
    with pytest.raises(ValueError):
        await existing_service.approve_support_override(
            support_override_request_id=support_override_request_id,
            approver_principal_id=requester_principal_id,
        )
