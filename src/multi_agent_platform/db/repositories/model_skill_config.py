from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.config.model_skill import ConfigKind, ScopeSelector
from multi_agent_platform.db.models.model_skill_config import (
    ActiveConfigurationPointer,
    AllowedToolPolicyVersion,
    ConfigurationAuditRecord,
    ConfigurationRollbackRecord,
    ModelProviderCatalogEntry,
    ModelRoutingVersion,
    ModelSkillConfigKind,
    ModelSkillVersionStatus,
    OutboundDomainPolicyVersion,
    PromptReferenceVersion,
    ResolvedExecutionConfiguration,
    RuntimePolicyDecision,
    SecretReferenceVersion,
    SkillBindingVersion,
    ToolCredentialRequirementVersion,
)


class StaleConfigurationError(RuntimeError):
    pass


def _db_kind(kind: ConfigKind) -> ModelSkillConfigKind:
    return ModelSkillConfigKind(kind.value)


@dataclass(slots=True)
class ActiveVersionResult:
    pointer: ActiveConfigurationPointer
    previous_version_id: UUID | None


class ModelSkillConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_provider(
        self, provider: ModelProviderCatalogEntry
    ) -> ModelProviderCatalogEntry:
        self.session.add(provider)
        await self.session.flush()
        return provider

    async def list_active_providers(
        self, *, tenant_id: UUID
    ) -> list[ModelProviderCatalogEntry]:
        stmt = select(ModelProviderCatalogEntry).where(
            (
                (ModelProviderCatalogEntry.tenant_id == tenant_id)
                | (ModelProviderCatalogEntry.tenant_id.is_(None))
            ),
            ModelProviderCatalogEntry.status == "ACTIVE",
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def find_provider(
        self, *, tenant_id: UUID, provider_key: str, model_id: str
    ) -> ModelProviderCatalogEntry | None:
        stmt = select(ModelProviderCatalogEntry).where(
            ModelProviderCatalogEntry.provider_key == provider_key,
            ModelProviderCatalogEntry.model_id == model_id,
            (
                (ModelProviderCatalogEntry.tenant_id == tenant_id)
                | (ModelProviderCatalogEntry.tenant_id.is_(None))
            ),
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def next_sequence(
        self, *, kind: ConfigKind, tenant_id: UUID, scope_hash: str
    ) -> int:
        model = _model_for_kind(kind)
        stmt = select(model).where(
            model.tenant_id == tenant_id,
            model.scope_hash == scope_hash,
        )
        records = list((await self.session.execute(stmt)).scalars().all())
        return max((record.version_sequence for record in records), default=0) + 1

    async def add_version(self, version: object) -> object:
        self.session.add(version)
        await self.session.flush()
        return version

    async def activate(
        self,
        *,
        tenant_id: UUID,
        kind: ConfigKind,
        scope: ScopeSelector,
        version_id: UUID,
        actor_principal_id: UUID,
        reason: str,
        expected_active_version_id: UUID | None = None,
    ) -> ActiveVersionResult:
        pointer = await self.active_pointer(
            tenant_id=tenant_id,
            kind=kind,
            scope_hash=scope.scope_hash(),
        )
        previous_version_id = pointer.active_version_id if pointer else None
        if expected_active_version_id is not None and (
            previous_version_id != expected_active_version_id
        ):
            raise StaleConfigurationError("active version changed")
        if pointer is None:
            pointer = ActiveConfigurationPointer(
                tenant_id=tenant_id,
                config_kind=_db_kind(kind),
                scope_hash=scope.scope_hash(),
                scope_selectors=scope.model_dump(mode="json", exclude_none=True),
                active_version_id=version_id,
                activated_by_principal_id=actor_principal_id,
                activation_reason=reason,
                expected_previous_version_id=expected_active_version_id,
            )
            self.session.add(pointer)
        else:
            pointer.active_version_id = version_id
            pointer.activated_by_principal_id = actor_principal_id
            pointer.activation_reason = reason
            pointer.expected_previous_version_id = expected_active_version_id
        await self._set_status(kind=kind, version_id=version_id, status="active")
        if previous_version_id and previous_version_id != version_id:
            await self._set_status(
                kind=kind,
                version_id=previous_version_id,
                status="inactive",
            )
        await self.session.flush()
        return ActiveVersionResult(
            pointer=pointer, previous_version_id=previous_version_id
        )

    async def active_pointer(
        self, *, tenant_id: UUID, kind: ConfigKind, scope_hash: str
    ) -> ActiveConfigurationPointer | None:
        stmt = select(ActiveConfigurationPointer).where(
            ActiveConfigurationPointer.tenant_id == tenant_id,
            ActiveConfigurationPointer.config_kind == _db_kind(kind),
            ActiveConfigurationPointer.scope_hash == scope_hash,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_active_model_routes(
        self, tenant_id: UUID
    ) -> list[ModelRoutingVersion]:
        stmt = select(ModelRoutingVersion).where(
            ModelRoutingVersion.tenant_id == tenant_id,
            ModelRoutingVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_prompt_references(
        self, tenant_id: UUID
    ) -> list[PromptReferenceVersion]:
        stmt = select(PromptReferenceVersion).where(
            PromptReferenceVersion.tenant_id == tenant_id,
            PromptReferenceVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_skill_bindings(
        self, tenant_id: UUID
    ) -> list[SkillBindingVersion]:
        stmt = select(SkillBindingVersion).where(
            SkillBindingVersion.tenant_id == tenant_id,
            SkillBindingVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_tool_policies(
        self, tenant_id: UUID
    ) -> list[AllowedToolPolicyVersion]:
        stmt = select(AllowedToolPolicyVersion).where(
            AllowedToolPolicyVersion.tenant_id == tenant_id,
            AllowedToolPolicyVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_outbound_policies(
        self, tenant_id: UUID
    ) -> list[OutboundDomainPolicyVersion]:
        stmt = select(OutboundDomainPolicyVersion).where(
            OutboundDomainPolicyVersion.tenant_id == tenant_id,
            OutboundDomainPolicyVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_secret_references(
        self, tenant_id: UUID
    ) -> list[SecretReferenceVersion]:
        stmt = select(SecretReferenceVersion).where(
            SecretReferenceVersion.tenant_id == tenant_id,
            SecretReferenceVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_active_credential_requirements(
        self, tenant_id: UUID
    ) -> list[ToolCredentialRequirementVersion]:
        stmt = select(ToolCredentialRequirementVersion).where(
            ToolCredentialRequirementVersion.tenant_id == tenant_id,
            ToolCredentialRequirementVersion.status == ModelSkillVersionStatus.ACTIVE,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_history(
        self,
        *,
        tenant_id: UUID,
        kind: ConfigKind | None = None,
        limit: int = 100,
    ) -> list[ConfigurationAuditRecord]:
        stmt = select(ConfigurationAuditRecord).where(
            ConfigurationAuditRecord.tenant_id == tenant_id
        )
        if kind is not None:
            stmt = stmt.where(ConfigurationAuditRecord.config_kind == _db_kind(kind))
        stmt = stmt.order_by(ConfigurationAuditRecord.created_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_audit_record(
        self, record: ConfigurationAuditRecord
    ) -> ConfigurationAuditRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_rollback_record(
        self, record: ConfigurationRollbackRecord
    ) -> ConfigurationRollbackRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_resolved_configuration(
        self, record: ResolvedExecutionConfiguration
    ) -> ResolvedExecutionConfiguration:
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_resolved_configuration(
        self, resolved_execution_configuration_id: UUID
    ) -> ResolvedExecutionConfiguration | None:
        return await self.session.get(
            ResolvedExecutionConfiguration,
            resolved_execution_configuration_id,
        )

    async def get_resolved_configuration_for_run(
        self, *, tenant_id: UUID, workflow_run_id: UUID
    ) -> ResolvedExecutionConfiguration | None:
        stmt = select(ResolvedExecutionConfiguration).where(
            ResolvedExecutionConfiguration.tenant_id == tenant_id,
            ResolvedExecutionConfiguration.workflow_run_id == workflow_run_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_runtime_decision(
        self, record: RuntimePolicyDecision
    ) -> RuntimePolicyDecision:
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_runtime_decision_by_idempotency(
        self,
        *,
        tenant_id: UUID,
        workflow_run_id: UUID,
        decision_category: str,
        idempotency_key: str,
    ) -> RuntimePolicyDecision | None:
        stmt = select(RuntimePolicyDecision).where(
            RuntimePolicyDecision.tenant_id == tenant_id,
            RuntimePolicyDecision.workflow_run_id == workflow_run_id,
            RuntimePolicyDecision.decision_category == decision_category,
            RuntimePolicyDecision.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_run_decisions(
        self, *, tenant_id: UUID, workflow_run_id: UUID
    ) -> list[RuntimePolicyDecision]:
        stmt = (
            select(RuntimePolicyDecision)
            .where(
                RuntimePolicyDecision.tenant_id == tenant_id,
                RuntimePolicyDecision.workflow_run_id == workflow_run_id,
            )
            .order_by(RuntimePolicyDecision.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def _set_status(
        self, *, kind: ConfigKind, version_id: UUID, status: str
    ) -> None:
        model = _model_for_kind(kind)
        record = await self.session.get(model, version_id)
        if record is not None:
            record.status = ModelSkillVersionStatus(status)


def _model_for_kind(kind: ConfigKind) -> type[Any]:
    return {
        ConfigKind.MODEL_ROUTING: ModelRoutingVersion,
        ConfigKind.PROMPT_REFERENCE: PromptReferenceVersion,
        ConfigKind.SKILL_BINDING: SkillBindingVersion,
        ConfigKind.ALLOWED_TOOL_POLICY: AllowedToolPolicyVersion,
        ConfigKind.OUTBOUND_DOMAIN_POLICY: OutboundDomainPolicyVersion,
        ConfigKind.SECRET_REFERENCE: SecretReferenceVersion,
        ConfigKind.CREDENTIAL_REQUIREMENT: ToolCredentialRequirementVersion,
    }[kind]
