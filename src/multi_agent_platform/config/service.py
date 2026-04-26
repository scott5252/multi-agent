from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from multi_agent_platform.api.schemas.model_skill_config import (
    ActivationResponse,
    ConfigVersionResponse,
    CredentialRequirementCreateRequest,
    HistoryRecordResponse,
    HistoryResponse,
    ModelPreviewResponse,
    ModelRoutingCreateRequest,
    OutboundDomainPolicyCreateRequest,
    PromptReferenceCreateRequest,
    RunProvenanceResponse,
    SecretReferenceCreateRequest,
    SkillBindingCreateRequest,
    ToolPolicyCreateRequest,
    ToolPreviewRequest,
    ToolPreviewResponse,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import (
    ConfigKind,
    ModelRoutingCandidate,
    ModelSkillErrorCategory,
    PolicyOutcome,
    PromptReferenceCandidate,
    ScopeSelector,
    VersionStatus,
)
from multi_agent_platform.config.policy import (
    evaluate_tool_policy,
)
from multi_agent_platform.config.resolver import resolve_model_prompt
from multi_agent_platform.config.validation import (
    assert_no_raw_secret,
    require_reason,
    validate_scope_for_kind,
)
from multi_agent_platform.db.models.model_skill_config import (
    AllowedToolPolicyVersion,
    ConfigurationAuditRecord,
    ModelProviderCatalogEntry,
    ModelRoutingVersion,
    ModelSkillConfigKind,
    ModelSkillVersionStatus,
    OutboundDomainPolicyVersion,
    PromptReferenceVersion,
    SecretReferenceVersion,
    SkillBindingVersion,
    ToolCredentialRequirementVersion,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
    StaleConfigurationError,
)


class ModelSkillServiceError(RuntimeError):
    def __init__(self, category: ModelSkillErrorCategory, message: str) -> None:
        super().__init__(message)
        self.category = category


class ModelSkillConfigService:
    def __init__(self, *, repository: ModelSkillConfigRepository) -> None:
        self.repository = repository

    async def create_model_routing(
        self,
        *,
        principal: PrincipalContext,
        payload: ModelRoutingCreateRequest,
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        validate_scope_for_kind(ConfigKind.MODEL_ROUTING, payload.scope)
        assert_no_raw_secret(payload.routing_parameters)
        provider = await self.repository.find_provider(
            tenant_id=payload.scope.tenant_id,
            provider_key=payload.provider_key,
            model_id=payload.model_id,
        )
        if provider is None:
            provider = await self.repository.upsert_provider(
                ModelProviderCatalogEntry(
                    tenant_id=payload.scope.tenant_id,
                    provider_key=payload.provider_key,
                    model_id=payload.model_id,
                    display_name=f"{payload.provider_key} {payload.model_id}",
                )
            )
        sequence = await self.repository.next_sequence(
            kind=ConfigKind.MODEL_ROUTING,
            tenant_id=payload.scope.tenant_id,
            scope_hash=payload.scope.scope_hash(),
        )
        version = ModelRoutingVersion(
            tenant_id=payload.scope.tenant_id,
            scope_type=payload.scope.scope_type.value,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            step_key=payload.scope.step_key,
            scope_hash=payload.scope.scope_hash(),
            model_provider_entry_id=provider.model_provider_entry_id,
            routing_parameters=payload.routing_parameters,
            status=ModelSkillVersionStatus.DRAFT,
            version_sequence=sequence,
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={
                "provider_key": payload.provider_key,
                "model_id": payload.model_id,
                "scope_type": payload.scope.scope_type.value,
            },
        )
        await self.repository.add_version(version)
        active = False
        if payload.activate:
            await self._activate(
                principal=principal,
                kind=ConfigKind.MODEL_ROUTING,
                scope=payload.scope,
                version_id=version.model_routing_version_id,
                reason=reason,
                expected_active_version_id=payload.expected_active_version_id,
            )
            active = True
        await self._audit(
            principal=principal,
            action="create",
            kind=ConfigKind.MODEL_ROUTING,
            scope=payload.scope,
            reason=reason,
            new_version_id=version.model_routing_version_id,
            summary=version.redacted_summary,
        )
        return ConfigVersionResponse(
            config_kind=ConfigKind.MODEL_ROUTING,
            version_id=version.model_routing_version_id,
            tenant_id=version.tenant_id,
            scope=payload.scope,
            status=version.status.value,
            active=active,
            version_sequence=version.version_sequence,
            activation_reason=reason,
            redacted_summary=version.redacted_summary,
        )

    async def create_prompt_reference(
        self,
        *,
        principal: PrincipalContext,
        payload: PromptReferenceCreateRequest,
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        validate_scope_for_kind(ConfigKind.PROMPT_REFERENCE, payload.scope)
        version = PromptReferenceVersion(
            tenant_id=payload.scope.tenant_id,
            scope_type=payload.scope.scope_type.value,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            step_key=payload.scope.step_key,
            scope_hash=payload.scope.scope_hash(),
            prompt_id=payload.prompt_id,
            prompt_version_id=payload.prompt_version_id,
            prompt_digest=payload.prompt_digest,
            status=ModelSkillVersionStatus.DRAFT,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.PROMPT_REFERENCE,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"prompt_digest": payload.prompt_digest},
        )
        await self.repository.add_version(version)
        active = False
        if payload.activate:
            await self._activate(
                principal=principal,
                kind=ConfigKind.PROMPT_REFERENCE,
                scope=payload.scope,
                version_id=version.prompt_reference_version_id,
                reason=reason,
                expected_active_version_id=payload.expected_active_version_id,
            )
            active = True
        await self._audit(
            principal=principal,
            action="create",
            kind=ConfigKind.PROMPT_REFERENCE,
            scope=payload.scope,
            reason=reason,
            new_version_id=version.prompt_reference_version_id,
            summary=version.redacted_summary,
        )
        return self._version_response(
            ConfigKind.PROMPT_REFERENCE,
            version.prompt_reference_version_id,
            payload.scope,
            version.status.value,
            active,
            version.version_sequence,
            reason,
            version.redacted_summary,
        )

    async def create_skill_binding(
        self, *, principal: PrincipalContext, payload: SkillBindingCreateRequest
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        assert_no_raw_secret(payload.runtime_ref_constraints)
        version = SkillBindingVersion(
            skill_binding_version_id=uuid4(),
            tenant_id=payload.scope.tenant_id,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            scope_hash=payload.scope.scope_hash(),
            skill_slug=payload.skill_slug,
            skill_version=payload.skill_version,
            allowed_contexts=payload.allowed_contexts,
            runtime_ref_constraints=payload.runtime_ref_constraints,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.SKILL_BINDING,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"skill_slug": payload.skill_slug},
        )
        return await self._create_generic(
            principal=principal,
            kind=ConfigKind.SKILL_BINDING,
            scope=payload.scope,
            version=version,
            version_id=version.skill_binding_version_id,
            activate=payload.activate,
            expected_active_version_id=payload.expected_active_version_id,
            reason=reason,
        )

    async def create_tool_policy(
        self, *, principal: PrincipalContext, payload: ToolPolicyCreateRequest
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        assert_no_raw_secret(payload.constraints)
        version = AllowedToolPolicyVersion(
            allowed_tool_policy_version_id=uuid4(),
            tenant_id=payload.scope.tenant_id,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            step_key=payload.scope.step_key,
            scope_hash=payload.scope.scope_hash(),
            skill_slug=payload.skill_slug,
            tool_id=payload.tool_id,
            allowed_action_categories=payload.allowed_action_categories,
            constraints=payload.constraints,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.ALLOWED_TOOL_POLICY,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"tool_id": payload.tool_id},
        )
        return await self._create_generic(
            principal=principal,
            kind=ConfigKind.ALLOWED_TOOL_POLICY,
            scope=payload.scope,
            version=version,
            version_id=version.allowed_tool_policy_version_id,
            activate=payload.activate,
            expected_active_version_id=payload.expected_active_version_id,
            reason=reason,
        )

    async def create_outbound_policy(
        self, *, principal: PrincipalContext, payload: OutboundDomainPolicyCreateRequest
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        version = OutboundDomainPolicyVersion(
            outbound_domain_policy_version_id=uuid4(),
            tenant_id=payload.scope.tenant_id,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            step_key=payload.scope.step_key,
            scope_hash=payload.scope.scope_hash(),
            tool_id=payload.tool_id,
            action_category=payload.action_category,
            allowed_domain_patterns=payload.allowed_domain_patterns,
            allowed_schemes=payload.allowed_schemes,
            allowed_ports=payload.allowed_ports,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.OUTBOUND_DOMAIN_POLICY,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"tool_id": payload.tool_id},
        )
        return await self._create_generic(
            principal=principal,
            kind=ConfigKind.OUTBOUND_DOMAIN_POLICY,
            scope=payload.scope,
            version=version,
            version_id=version.outbound_domain_policy_version_id,
            activate=payload.activate,
            expected_active_version_id=payload.expected_active_version_id,
            reason=reason,
        )

    async def create_secret_reference(
        self, *, principal: PrincipalContext, payload: SecretReferenceCreateRequest
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        assert_no_raw_secret(payload.allowed_scopes)
        assert_no_raw_secret(payload.rotation_metadata)
        version = SecretReferenceVersion(
            secret_reference_version_id=uuid4(),
            tenant_id=payload.scope.tenant_id,
            scope_hash=payload.scope.scope_hash(),
            secret_reference_id=payload.secret_reference_id,
            provider_key=payload.provider_key,
            external_reference=payload.external_reference,
            allowed_scopes=payload.allowed_scopes,
            rotation_metadata=payload.rotation_metadata,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.SECRET_REFERENCE,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"secret_reference_id": payload.secret_reference_id},
        )
        return await self._create_generic(
            principal=principal,
            kind=ConfigKind.SECRET_REFERENCE,
            scope=payload.scope,
            version=version,
            version_id=version.secret_reference_version_id,
            activate=payload.activate,
            expected_active_version_id=payload.expected_active_version_id,
            reason=reason,
        )

    async def create_credential_requirement(
        self,
        *,
        principal: PrincipalContext,
        payload: CredentialRequirementCreateRequest,
    ) -> ConfigVersionResponse:
        self._authorize_tenant(principal, payload.scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        assert_no_raw_secret(payload.allowed_credential_scope)
        version = ToolCredentialRequirementVersion(
            tool_credential_requirement_version_id=uuid4(),
            tenant_id=payload.scope.tenant_id,
            workflow_lineage_id=payload.scope.workflow_lineage_id,
            workflow_version_bundle_id=payload.scope.workflow_version_bundle_id,
            agent_key=payload.scope.agent_key,
            step_key=payload.scope.step_key,
            scope_hash=payload.scope.scope_hash(),
            tool_id=payload.tool_id,
            action_category=payload.action_category,
            credential_kind=payload.credential_kind,
            secret_reference_version_id=payload.secret_reference_version_id,
            delegated_credential_link_id=payload.delegated_credential_link_id,
            allowed_credential_scope=payload.allowed_credential_scope,
            expiry_policy=payload.expiry_policy,
            version_sequence=await self.repository.next_sequence(
                kind=ConfigKind.CREDENTIAL_REQUIREMENT,
                tenant_id=payload.scope.tenant_id,
                scope_hash=payload.scope.scope_hash(),
            ),
            created_by_principal_id=self._principal_identity_id(principal),
            activation_reason=reason,
            redacted_summary={"tool_id": payload.tool_id},
        )
        return await self._create_generic(
            principal=principal,
            kind=ConfigKind.CREDENTIAL_REQUIREMENT,
            scope=payload.scope,
            version=version,
            version_id=version.tool_credential_requirement_version_id,
            activate=payload.activate,
            expected_active_version_id=payload.expected_active_version_id,
            reason=reason,
        )

    async def activate_version(
        self,
        *,
        principal: PrincipalContext,
        kind: ConfigKind,
        scope: ScopeSelector,
        version_id: UUID,
        reason: str,
        expected_active_version_id: UUID | None = None,
    ) -> ActivationResponse:
        self._authorize_tenant(principal, scope.tenant_id, write=True)
        return await self._activate(
            principal=principal,
            kind=kind,
            scope=scope,
            version_id=version_id,
            reason=require_reason(reason),
            expected_active_version_id=expected_active_version_id,
        )

    async def preview_model(
        self, *, principal: PrincipalContext, scope: ScopeSelector
    ) -> ModelPreviewResponse:
        self._authorize_tenant(principal, scope.tenant_id, write=False)
        model_rows = await self.repository.list_active_model_routes(scope.tenant_id)
        prompt_rows = await self.repository.list_active_prompt_references(
            scope.tenant_id
        )
        model_candidates = [
            ModelRoutingCandidate(
                version_id=row.model_routing_version_id,
                tenant_id=row.tenant_id,
                scope=_scope_from_row(row),
                status=VersionStatus(row.status.value),
                version_sequence=row.version_sequence,
                activation_reason=row.activation_reason,
                redacted_summary=row.redacted_summary,
                model_provider_entry_id=row.model_provider_entry_id,
                provider_key=str(row.redacted_summary.get("provider_key", "unknown")),
                model_id=str(row.redacted_summary.get("model_id", "unknown")),
                routing_parameters=row.routing_parameters,
            )
            for row in model_rows
        ]
        prompt_candidates = [
            PromptReferenceCandidate(
                version_id=row.prompt_reference_version_id,
                tenant_id=row.tenant_id,
                scope=_scope_from_row(row),
                status=VersionStatus(row.status.value),
                version_sequence=row.version_sequence,
                activation_reason=row.activation_reason,
                redacted_summary=row.redacted_summary,
                prompt_id=row.prompt_id,
                prompt_version_id=row.prompt_version_id,
                prompt_digest=row.prompt_digest,
            )
            for row in prompt_rows
        ]
        resolution = resolve_model_prompt(
            model_candidates=model_candidates,
            prompt_candidates=prompt_candidates,
            request_scope=scope,
        )
        await self._audit(
            principal=principal,
            action="preview",
            kind=ConfigKind.MODEL_ROUTING,
            scope=scope,
            reason="preview model resolution",
            new_version_id=resolution.model.model_routing_version_id,
            summary={"model_source_scope": resolution.model.source_scope.value},
        )
        return ModelPreviewResponse(
            model_routing_version_id=resolution.model.model_routing_version_id,
            model_provider_key=resolution.model.provider_key,
            model_id=resolution.model.model_id,
            model_source_scope=resolution.model.source_scope.value,
            prompt_reference_version_id=resolution.prompt.prompt_reference_version_id,
            prompt_id=resolution.prompt.prompt_id,
            prompt_version_id=resolution.prompt.prompt_version_id,
            prompt_digest=resolution.prompt.prompt_digest,
            prompt_source_scope=resolution.prompt.source_scope.value,
            evaluated_version_ids=[
                *resolution.model.considered_version_ids,
                *resolution.prompt.considered_version_ids,
            ],
        )

    async def preview_tool(
        self, *, principal: PrincipalContext, payload: ToolPreviewRequest
    ) -> ToolPreviewResponse:
        self._authorize_tenant(principal, payload.tenant_id, write=False)
        # Full DB policy loading lands in the next slice. This keeps API behavior
        # fail-closed until policies are queried from immutable active versions.
        _ = evaluate_tool_policy(
            candidates=[],
            scope=payload,
            skill_slug=payload.skill_slug,
            tool_id=payload.tool_id,
            action_category=payload.action_category,
        )
        return ToolPreviewResponse(
            outcome=PolicyOutcome.DENY,
            denial_category=ModelSkillErrorCategory.TOOL_DENIED,
            safe_reason="no active tool allow policy matched",
        )

    async def list_history(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        kind: ConfigKind | None = None,
        limit: int = 100,
    ) -> HistoryResponse:
        self._authorize_tenant(principal, tenant_id, write=False)
        records = await self.repository.list_history(
            tenant_id=tenant_id,
            kind=kind,
            limit=max(1, min(limit, 100)),
        )
        return HistoryResponse(
            items=[
                HistoryRecordResponse(
                    configuration_audit_record_id=row.configuration_audit_record_id,
                    actor_principal_id=row.actor_principal_id,
                    action=row.action,
                    config_kind=ConfigKind(row.config_kind.value),
                    affected_scope=row.affected_scope,
                    prior_version_id=row.prior_version_id,
                    new_version_id=row.new_version_id,
                    reason=row.reason,
                    created_at=row.created_at,
                    redacted_diff_summary=row.redacted_diff_summary,
                )
                for row in records
            ]
        )

    async def run_provenance(
        self, *, principal: PrincipalContext, tenant_id: UUID, workflow_run_id: UUID
    ) -> RunProvenanceResponse:
        self._authorize_tenant(principal, tenant_id, write=False)
        decisions = await self.repository.list_run_decisions(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
        )
        return RunProvenanceResponse(
            workflow_run_id=workflow_run_id,
            decisions=[
                {
                    "runtime_policy_decision_id": str(row.runtime_policy_decision_id),
                    "decision_category": row.decision_category,
                    "outcome": row.outcome.value,
                    "denial_category": row.denial_category,
                    "safe_reason": row.safe_reason,
                    "evaluated_version_ids": row.evaluated_version_ids,
                }
                for row in decisions
            ],
        )

    async def _create_generic(
        self,
        *,
        principal: PrincipalContext,
        kind: ConfigKind,
        scope: ScopeSelector,
        version: Any,
        version_id: UUID,
        activate: bool,
        expected_active_version_id: UUID | None,
        reason: str,
    ) -> ConfigVersionResponse:
        await self.repository.add_version(version)
        active = False
        if activate:
            await self._activate(
                principal=principal,
                kind=kind,
                scope=scope,
                version_id=version_id,
                reason=reason,
                expected_active_version_id=expected_active_version_id,
            )
            active = True
        summary = version.redacted_summary
        await self._audit(
            principal=principal,
            action="create",
            kind=kind,
            scope=scope,
            reason=reason,
            new_version_id=version_id,
            summary=summary,
        )
        return self._version_response(
            kind,
            version_id,
            scope,
            version.status.value,
            active,
            version.version_sequence,
            reason,
            summary,
        )

    async def _activate(
        self,
        *,
        principal: PrincipalContext,
        kind: ConfigKind,
        scope: ScopeSelector,
        version_id: UUID,
        reason: str,
        expected_active_version_id: UUID | None,
    ) -> ActivationResponse:
        try:
            result = await self.repository.activate(
                tenant_id=scope.tenant_id,
                kind=kind,
                scope=scope,
                version_id=version_id,
                actor_principal_id=self._principal_identity_id(principal),
                reason=reason,
                expected_active_version_id=expected_active_version_id,
            )
        except StaleConfigurationError as exc:
            raise ModelSkillServiceError(
                ModelSkillErrorCategory.STALE_CONFIGURATION,
                "active version changed since caller previewed it",
            ) from exc
        await self._audit(
            principal=principal,
            action="activate",
            kind=kind,
            scope=scope,
            reason=reason,
            prior_version_id=result.previous_version_id,
            new_version_id=version_id,
            summary={"scope_hash": scope.scope_hash()},
        )
        return ActivationResponse(
            active_configuration_pointer_id=result.pointer.active_configuration_pointer_id,
            active_version_id=version_id,
            prior_version_id=result.previous_version_id,
            config_kind=kind,
            scope_hash=scope.scope_hash(),
        )

    async def _audit(
        self,
        *,
        principal: PrincipalContext,
        action: str,
        kind: ConfigKind,
        scope: ScopeSelector,
        reason: str,
        prior_version_id: UUID | None = None,
        new_version_id: UUID | None = None,
        summary: dict[str, object] | None = None,
    ) -> None:
        await self.repository.add_audit_record(
            ConfigurationAuditRecord(
                tenant_id=scope.tenant_id,
                actor_principal_id=principal.principal_identity_id,
                actor_role=principal.role_codes[0] if principal.role_codes else None,
                action=action,
                config_kind=ModelSkillConfigKind(kind.value),
                affected_scope=scope.model_dump(mode="json", exclude_none=True),
                prior_version_id=prior_version_id,
                new_version_id=new_version_id,
                reason=reason,
                request_id=principal.request_id,
                trace_id=principal.trace_id,
                redacted_diff_summary=summary or {},
            )
        )

    def _authorize_tenant(
        self, principal: PrincipalContext, tenant_id: UUID, *, write: bool
    ) -> None:
        if principal.tenant_id not in (None, tenant_id):
            raise ModelSkillServiceError(
                ModelSkillErrorCategory.AUTHORIZATION_FAILED,
                "configuration access is scoped to the caller tenant",
            )
        if write and not {
            "tenant_admin",
            "platform_admin",
            "workflow_owner",
            "maintainer",
        }.intersection(principal.role_codes):
            raise ModelSkillServiceError(
                ModelSkillErrorCategory.AUTHORIZATION_FAILED,
                "configuration mutation requires an administrator or maintainer role",
            )

    def _principal_identity_id(self, principal: PrincipalContext) -> UUID:
        return principal.principal_identity_id or uuid4()

    def _version_response(
        self,
        kind: ConfigKind,
        version_id: UUID,
        scope: ScopeSelector,
        status: str,
        active: bool,
        version_sequence: int,
        reason: str,
        summary: dict[str, object],
    ) -> ConfigVersionResponse:
        return ConfigVersionResponse(
            config_kind=kind,
            version_id=version_id,
            tenant_id=scope.tenant_id,
            scope=scope,
            status=status,
            active=active,
            version_sequence=version_sequence,
            activation_reason=reason,
            redacted_summary=summary,
        )


def _scope_from_row(row: Any) -> ScopeSelector:
    return ScopeSelector(
        tenant_id=row.tenant_id,
        workflow_lineage_id=getattr(row, "workflow_lineage_id", None),
        workflow_version_bundle_id=getattr(row, "workflow_version_bundle_id", None),
        agent_key=getattr(row, "agent_key", None),
        step_key=getattr(row, "step_key", None),
    )
