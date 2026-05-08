from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.skill_registry import (
    SkillAuditRecord,
    SkillInstallation,
    SkillInstallationCredential,
    SkillInstallationTest,
    SkillPackage,
    SkillPackageTenantGrant,
    SkillPackageVersion,
)


class StaleSkillRegistryWriteError(RuntimeError):
    pass


class SkillRegistryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_package(self, package: SkillPackage) -> SkillPackage:
        self.session.add(package)
        await self.session.flush()
        return package

    async def get_package_by_slug(self, slug: str) -> SkillPackage | None:
        stmt = select(SkillPackage).where(SkillPackage.slug == slug)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_package_version(
        self,
        version: SkillPackageVersion,
    ) -> SkillPackageVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def get_package_version(
        self,
        *,
        slug: str,
        semantic_version: str,
    ) -> SkillPackageVersion | None:
        stmt = select(SkillPackageVersion).where(
            SkillPackageVersion.slug == slug,
            SkillPackageVersion.semantic_version == semantic_version,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_package_version_by_id(
        self,
        version_id: UUID,
    ) -> SkillPackageVersion | None:
        return await self.session.get(SkillPackageVersion, version_id)

    async def list_package_versions(
        self,
        *,
        limit: int = 50,
    ) -> list[SkillPackageVersion]:
        stmt = (
            select(SkillPackageVersion)
            .order_by(SkillPackageVersion.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_available_versions(
        self,
        *,
        tenant_id: UUID,
    ) -> list[SkillPackageVersion]:
        stmt = (
            select(SkillPackageVersion)
            .join(
                SkillPackageTenantGrant,
                SkillPackageTenantGrant.skill_package_version_id
                == SkillPackageVersion.skill_package_version_id,
            )
            .where(
                SkillPackageVersion.lifecycle_state == "PUBLISHED",
                SkillPackageTenantGrant.status == "active",
                (
                    (SkillPackageTenantGrant.tenant_id == tenant_id)
                    | (SkillPackageTenantGrant.tenant_id.is_(None))
                ),
            )
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_tenant_grant(
        self,
        grant: SkillPackageTenantGrant,
    ) -> SkillPackageTenantGrant:
        self.session.add(grant)
        await self.session.flush()
        return grant

    async def get_tenant_grant(
        self,
        *,
        version_id: UUID,
        tenant_id: UUID | None,
    ) -> SkillPackageTenantGrant | None:
        stmt = select(SkillPackageTenantGrant).where(
            SkillPackageTenantGrant.skill_package_version_id == version_id,
            SkillPackageTenantGrant.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_tenant_grants(
        self,
        *,
        tenant_id: UUID | None = None,
        version_ids: Sequence[UUID] | None = None,
        limit: int = 100,
    ) -> list[SkillPackageTenantGrant]:
        stmt = select(SkillPackageTenantGrant)
        if tenant_id is not None:
            stmt = stmt.where(
                (SkillPackageTenantGrant.tenant_id == tenant_id)
                | (SkillPackageTenantGrant.tenant_id.is_(None))
            )
        if version_ids:
            stmt = stmt.where(
                SkillPackageTenantGrant.skill_package_version_id.in_(version_ids)
            )
        stmt = stmt.order_by(SkillPackageTenantGrant.granted_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_installation(
        self,
        installation: SkillInstallation,
    ) -> SkillInstallation:
        self.session.add(installation)
        await self.session.flush()
        return installation

    async def get_installation(
        self,
        installation_id: UUID,
    ) -> SkillInstallation | None:
        return await self.session.get(SkillInstallation, installation_id)

    async def require_revision(
        self,
        *,
        installation_id: UUID,
        expected_revision_token: str,
    ) -> SkillInstallation:
        installation = await self.get_installation(installation_id)
        if installation is None:
            raise LookupError("skill installation not found")
        if installation.revision_token != expected_revision_token:
            raise StaleSkillRegistryWriteError("stale installation revision token")
        return installation

    async def list_installations_for_tenant(
        self,
        *,
        tenant_id: UUID,
    ) -> list[SkillInstallation]:
        stmt = (
            select(SkillInstallation)
            .where(SkillInstallation.tenant_id == tenant_id)
            .order_by(SkillInstallation.updated_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_credentials_for_installations(
        self,
        installation_ids: Sequence[UUID],
    ) -> list[SkillInstallationCredential]:
        if not installation_ids:
            return []
        stmt = (
            select(SkillInstallationCredential)
            .where(
                SkillInstallationCredential.skill_installation_id.in_(
                    tuple(installation_ids)
                )
            )
            .order_by(SkillInstallationCredential.requirement_key.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_tests_for_installations(
        self,
        installation_ids: Sequence[UUID],
        *,
        limit: int = 100,
    ) -> list[SkillInstallationTest]:
        if not installation_ids:
            return []
        stmt = (
            select(SkillInstallationTest)
            .where(
                SkillInstallationTest.skill_installation_id.in_(tuple(installation_ids))
            )
            .order_by(SkillInstallationTest.started_at.desc().nullslast())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_installation_credential(
        self,
        credential: SkillInstallationCredential,
    ) -> SkillInstallationCredential:
        self.session.add(credential)
        await self.session.flush()
        return credential

    async def add_installation_test(
        self,
        test: SkillInstallationTest,
    ) -> SkillInstallationTest:
        self.session.add(test)
        await self.session.flush()
        return test

    async def add_audit_record(
        self,
        record: SkillAuditRecord,
    ) -> SkillAuditRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_audit_records(
        self,
        *,
        tenant_id: UUID | None,
        package_slug: str | None = None,
        limit: int = 100,
    ) -> list[SkillAuditRecord]:
        stmt = select(SkillAuditRecord)
        if tenant_id is not None:
            stmt = stmt.where(
                (SkillAuditRecord.tenant_id == tenant_id)
                | (SkillAuditRecord.tenant_id.is_(None))
            )
        if package_slug is not None:
            stmt = stmt.where(SkillAuditRecord.package_slug == package_slug)
        stmt = stmt.order_by(SkillAuditRecord.created_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())
