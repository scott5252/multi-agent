from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from multi_agent_platform.api.ui.admin_console import AdminScope
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.admin_console import AdminSavedFilter


class AdminSavedFilterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _principal_filter(self, principal: PrincipalContext) -> ColumnElement[bool]:
        if principal.principal_identity_id is not None:
            return (
                AdminSavedFilter.principal_identity_id
                == principal.principal_identity_id
            )
        return and_(
            AdminSavedFilter.principal_identity_id.is_(None),
            AdminSavedFilter.principal_id == principal.principal_id,
        )

    def _scope_filter(self, scope: AdminScope) -> ColumnElement[bool]:
        if scope.scope_type == "platform":
            return and_(
                AdminSavedFilter.scope_type == "platform",
                AdminSavedFilter.tenant_id.is_(None),
            )
        return and_(
            AdminSavedFilter.scope_type == "tenant",
            AdminSavedFilter.tenant_id == scope.tenant_id,
        )

    async def list_filters(
        self,
        *,
        principal: PrincipalContext,
        admin_area: str,
        scope: AdminScope,
    ) -> list[AdminSavedFilter]:
        stmt = (
            select(AdminSavedFilter)
            .where(
                self._principal_filter(principal),
                AdminSavedFilter.admin_area == admin_area,
                self._scope_filter(scope),
            )
            .order_by(AdminSavedFilter.updated_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_filter(
        self,
        *,
        principal: PrincipalContext,
        admin_area: str,
        scope: AdminScope,
        filter_id: UUID,
    ) -> AdminSavedFilter | None:
        stmt = select(AdminSavedFilter).where(
            AdminSavedFilter.admin_saved_filter_id == filter_id,
            self._principal_filter(principal),
            AdminSavedFilter.admin_area == admin_area,
            self._scope_filter(scope),
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def save_filter(
        self,
        *,
        principal: PrincipalContext,
        admin_area: str,
        filter_key: str,
        scope: AdminScope,
        display_name: str,
        criteria: dict[str, object],
        safe_summary: dict[str, str],
    ) -> AdminSavedFilter:
        stmt = select(AdminSavedFilter).where(
            self._principal_filter(principal),
            AdminSavedFilter.admin_area == admin_area,
            AdminSavedFilter.filter_key == filter_key,
            self._scope_filter(scope),
            AdminSavedFilter.display_name == display_name,
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            existing.criteria = criteria
            existing.safe_summary = safe_summary
            existing.updated_at = datetime.now(UTC)
            await self.session.flush()
            return existing

        record = AdminSavedFilter(
            principal_identity_id=principal.principal_identity_id,
            principal_id=principal.principal_id,
            admin_area=admin_area,
            filter_key=filter_key,
            scope_type=scope.scope_type,
            tenant_id=scope.tenant_id,
            display_name=display_name,
            criteria=criteria,
            safe_summary=safe_summary,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def mark_restored(
        self,
        *,
        principal: PrincipalContext,
        admin_area: str,
        scope: AdminScope,
        filter_id: UUID,
    ) -> AdminSavedFilter | None:
        record = await self.get_filter(
            principal=principal,
            admin_area=admin_area,
            scope=scope,
            filter_id=filter_id,
        )
        if record is None:
            return None
        record.last_restored_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def delete_filter(
        self,
        *,
        principal: PrincipalContext,
        admin_area: str,
        scope: AdminScope,
        filter_id: UUID,
    ) -> bool:
        record = await self.get_filter(
            principal=principal,
            admin_area=admin_area,
            scope=scope,
            filter_id=filter_id,
        )
        if record is None:
            return False
        await self.session.delete(record)
        await self.session.flush()
        return True
