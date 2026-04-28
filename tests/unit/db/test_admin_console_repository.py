from __future__ import annotations

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.ui.admin_console import AdminScope
from multi_agent_platform.db.repositories.admin_console import (
    AdminSavedFilterRepository,
)
from tests.fixtures.admin_console import tenant_principal


async def test_saved_filter_repository_scopes_crud_to_principal_and_tenant(
    session: AsyncSession,
) -> None:
    repo = AdminSavedFilterRepository(session)
    principal = tenant_principal()
    scope = AdminScope.tenant(principal.tenant_id)

    record = await repo.save_filter(
        principal=principal,
        admin_area="workflows",
        filter_key="workflow-list",
        scope=scope,
        display_name="Drafts",
        criteria={"status": "draft"},
        safe_summary={"status": "draft"},
    )
    listed = await repo.list_filters(
        principal=principal,
        admin_area="workflows",
        scope=scope,
    )
    restored = await repo.mark_restored(
        principal=principal,
        admin_area="workflows",
        scope=scope,
        filter_id=record.admin_saved_filter_id,
    )
    other_scope = await repo.get_filter(
        principal=principal,
        admin_area="workflows",
        scope=AdminScope.tenant(uuid4()),
        filter_id=record.admin_saved_filter_id,
    )

    assert [item.admin_saved_filter_id for item in listed] == [
        record.admin_saved_filter_id
    ]
    assert restored is not None
    assert restored.last_restored_at is not None
    assert other_scope is None


async def test_saved_filter_repository_updates_deletes_and_falls_back_to_principal_id(
    session: AsyncSession,
) -> None:
    repo = AdminSavedFilterRepository(session)
    principal = tenant_principal().model_copy(update={"principal_identity_id": None})
    scope = AdminScope.tenant(principal.tenant_id)

    record = await repo.save_filter(
        principal=principal,
        admin_area="run_inspection",
        filter_key="run-search",
        scope=scope,
        display_name="Failed runs",
        criteria={"status": "failed"},
        safe_summary={"status": "failed"},
    )
    updated = await repo.save_filter(
        principal=principal,
        admin_area="run_inspection",
        filter_key="run-search",
        scope=scope,
        display_name="Failed runs",
        criteria={"status": "blocked"},
        safe_summary={"status": "blocked"},
    )
    missing_restore = await repo.mark_restored(
        principal=principal,
        admin_area="run_inspection",
        scope=scope,
        filter_id=uuid4(),
    )
    deleted = await repo.delete_filter(
        principal=principal,
        admin_area="run_inspection",
        scope=scope,
        filter_id=record.admin_saved_filter_id,
    )
    missing_delete = await repo.delete_filter(
        principal=principal,
        admin_area="run_inspection",
        scope=scope,
        filter_id=record.admin_saved_filter_id,
    )

    assert updated.admin_saved_filter_id == record.admin_saved_filter_id
    assert updated.criteria == {"status": "blocked"}
    assert missing_restore is None
    assert deleted is True
    assert missing_delete is False
