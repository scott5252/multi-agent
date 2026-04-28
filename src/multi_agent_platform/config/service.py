from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
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
    RollbackRequest,
    RollbackResponse,
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
    CredentialRequirementCandidate,
    DecisionCategory,
    ModelRoutingCandidate,
    ModelSkillErrorCategory,
    OutboundPolicyCandidate,
    PolicyOutcome,
    PromptReferenceCandidate,
    ScopeSelector,
    SecretReferenceCandidate,
    SkillBindingCandidate,
    ToolPolicyCandidate,
    VersionStatus,
)
from multi_agent_platform.config.policy import (
    PolicyDecision,
    evaluate_credential_requirements,
    evaluate_outbound_policy,
    evaluate_tool_policy,
)
from multi_agent_platform.config.policy import (
    evaluate_skill_access as evaluate_skill_access_policy,
)
from multi_agent_platform.config.provenance import ResolvedConfigurationSnapshot
from multi_agent_platform.config.resolver import resolve_model_prompt
from multi_agent_platform.config.validation import (
    assert_no_raw_secret,
    require_reason,
    validate_scope_for_kind,
)
from multi_agent_platform.db.models.model_skill_config import (
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
    RuntimeDecisionOutcome,
    RuntimePolicyDecision,
    SecretReferenceVersion,
    SkillBindingVersion,
    ToolCredentialRequirementVersion,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
    StaleConfigurationError,
)
from multi_agent_platform.observability.metrics import (
    record_model_skill_policy_decision,
)


class ModelSkillServiceError(RuntimeError):
    def __init__(self, category: ModelSkillErrorCategory, message: str) -> None:
        super().__init__(message)
        self.category = category


class PromptLibraryReferenceValidator(Protocol):
    async def validate_prompt_reference_for_new_use(
        self,
        *,
        tenant_id: UUID,
        prompt_version_id: UUID,
        prompt_digest: str,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class PinRunConfigurationRequest:
    tenant_id: UUID
    workflow_run_id: UUID
    run_bundle_id: UUID
    bundle_digest: str
    workflow_lineage_id: UUID | None
    workflow_version_bundle_id: UUID
    initiating_principal_id: UUID | None = None
    trace_id: str | None = None


@dataclass(frozen=True, slots=True)
class PinRunConfigurationResponse:
    resolved_execution_configuration_id: UUID
    resolution_digest: str
    model_routing_version_ids: list[UUID]
    prompt_reference_version_ids: list[UUID]
    prompt_library_version_ids: list[UUID]
    prompt_library_digests: list[str]
    skill_binding_version_ids: list[UUID]
    allowed_tool_policy_version_ids: list[UUID]
    outbound_domain_policy_version_ids: list[UUID]
    secret_reference_version_ids: list[UUID]
    credential_requirement_version_ids: list[UUID]
    warnings: list[str]


@dataclass(frozen=True, slots=True)
class ModelStepResolutionRequest:
    tenant_id: UUID
    workflow_run_id: UUID
    run_step_id: UUID
    run_bundle_id: UUID
    resolved_execution_configuration_id: UUID
    workflow_lineage_id: UUID | None
    workflow_version_bundle_id: UUID | None
    agent_key: str | None
    step_key: str | None
    trace_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ModelStepResolutionResponse:
    runtime_policy_decision_id: UUID
    outcome: PolicyOutcome
    model_provider_key: str
    model_id: str
    model_routing_version_id: UUID
    model_source_scope: str
    prompt_reference_version_id: UUID
    prompt_id: UUID
    prompt_version_id: UUID
    prompt_digest: str
    evaluated_version_ids: list[UUID]
    safe_reason: str


@dataclass(frozen=True, slots=True)
class SkillAccessRequest:
    tenant_id: UUID
    workflow_run_id: UUID
    run_step_id: UUID
    resolved_execution_configuration_id: UUID
    agent_key: str | None
    skill_slug: str
    skill_version: str
    use_context: str
    trace_id: str | None = None
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyEvaluationResponse:
    runtime_policy_decision_id: UUID
    outcome: PolicyOutcome
    evaluated_version_ids: list[UUID]
    winning_version_ids: list[UUID]
    denial_category: ModelSkillErrorCategory | None
    safe_reason: str
    authorized_secret_reference_ids: list[str] | None = None
    authorized_delegated_credential_link_ids: list[UUID] | None = None


@dataclass(frozen=True, slots=True)
class ToolUseRequest:
    tenant_id: UUID
    workflow_run_id: UUID
    run_step_id: UUID
    resolved_execution_configuration_id: UUID
    agent_key: str | None
    step_key: str | None
    skill_slug: str | None
    tool_id: str
    action_category: str
    destination_url: str | None = None
    credential_context: dict[str, object] | None = None
    trace_id: str | None = None
    idempotency_key: str | None = None
    authorized_delegated_credential_link_ids: set[UUID] | None = None


class ModelSkillConfigService:
    def __init__(
        self,
        *,
        repository: ModelSkillConfigRepository,
        prompt_library_validator: PromptLibraryReferenceValidator | None = None,
    ) -> None:
        self.repository = repository
        self.prompt_library_validator = prompt_library_validator

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
        if payload.scope.tenant_id is not None and self.prompt_library_validator:
            try:
                validate_prompt_reference = (
                    self.prompt_library_validator.validate_prompt_reference_for_new_use
                )
                await validate_prompt_reference(
                    tenant_id=payload.scope.tenant_id,
                    prompt_version_id=payload.prompt_version_id,
                    prompt_digest=payload.prompt_digest,
                )
            except Exception as exc:
                raise ModelSkillServiceError(
                    ModelSkillErrorCategory.MISSING_PROMPT_VERSION,
                    "prompt library version is unavailable for new use",
                ) from exc
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
            redacted_summary={
                "prompt_library_version_id": str(payload.prompt_version_id),
                "prompt_library_digest": payload.prompt_digest,
            },
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

    async def rollback_version(
        self,
        *,
        principal: PrincipalContext,
        kind: ConfigKind,
        scope: ScopeSelector,
        payload: RollbackRequest,
    ) -> RollbackResponse:
        self._authorize_tenant(principal, scope.tenant_id, write=True)
        reason = require_reason(payload.reason)
        pointer = await self.repository.active_pointer(
            tenant_id=scope.tenant_id,
            kind=kind,
            scope_hash=scope.scope_hash(),
        )
        if pointer is None:
            raise ModelSkillServiceError(
                ModelSkillErrorCategory.NOT_FOUND,
                "active configuration pointer was not found",
            )
        if (
            payload.expected_active_version_id is not None
            and pointer.active_version_id != payload.expected_active_version_id
        ):
            raise ModelSkillServiceError(
                ModelSkillErrorCategory.STALE_CONFIGURATION,
                "active version changed since rollback was previewed",
            )
        current_active_version_id = pointer.active_version_id
        result = await self.repository.activate(
            tenant_id=scope.tenant_id,
            kind=kind,
            scope=scope,
            version_id=payload.target_version_id,
            actor_principal_id=self._principal_identity_id(principal),
            reason=reason,
            expected_active_version_id=current_active_version_id,
        )
        audit_record = await self._audit(
            principal=principal,
            action="rollback",
            kind=kind,
            scope=scope,
            reason=reason,
            prior_version_id=result.previous_version_id,
            new_version_id=payload.target_version_id,
            summary={"scope_hash": scope.scope_hash()},
        )
        rollback = await self.repository.add_rollback_record(
            ConfigurationRollbackRecord(
                tenant_id=scope.tenant_id,
                config_kind=ModelSkillConfigKind(kind.value),
                scope_hash=scope.scope_hash(),
                from_version_id=current_active_version_id,
                to_version_id=payload.target_version_id,
                actor_principal_id=principal.principal_identity_id,
                reason=reason,
                configuration_audit_record_id=(
                    audit_record.configuration_audit_record_id
                ),
            )
        )
        return RollbackResponse(
            rollback_record_id=rollback.configuration_rollback_record_id,
            active_version_id=payload.target_version_id,
            audit_record_id=audit_record.configuration_audit_record_id,
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
        policy_data = await self._active_policy_candidates(payload.tenant_id)
        decisions: list[PolicyDecision] = []
        if payload.skill_slug:
            if payload.skill_version is None:
                decisions.append(
                    PolicyDecision(
                        outcome=PolicyOutcome.DENY,
                        denial_category=ModelSkillErrorCategory.SKILL_NOT_BOUND,
                        safe_reason="skill preview requires an exact skill version",
                        evaluated_version_ids=(),
                    )
                )
            else:
                decisions.append(
                    evaluate_skill_access_policy(
                        candidates=policy_data["skill_bindings"],
                        scope=payload,
                        skill_slug=payload.skill_slug,
                        skill_version=payload.skill_version,
                        use_context=payload.use_context,
                    )
                )
        decisions.append(
            evaluate_tool_policy(
                candidates=policy_data["tool_policies"],
                scope=payload,
                skill_slug=payload.skill_slug,
                tool_id=payload.tool_id,
                action_category=payload.action_category,
            )
        )
        if payload.destination_url:
            decisions.append(
                evaluate_outbound_policy(
                    candidates=policy_data["outbound_policies"],
                    scope=payload,
                    tool_id=payload.tool_id,
                    action_category=payload.action_category,
                    destination_url=payload.destination_url,
                )
            )
        decisions.append(
            evaluate_credential_requirements(
                requirements=policy_data["credential_requirements"],
                secret_references=policy_data["secret_references"],
                scope=payload,
                tool_id=payload.tool_id,
                action_category=payload.action_category,
                credential_context=payload.credential_context,
            )
        )
        decision = _first_denial_or_allow(decisions)
        return ToolPreviewResponse(
            outcome=decision.outcome,
            denial_category=decision.denial_category,
            safe_reason=decision.safe_reason,
            evaluated_version_ids=[
                value
                for item in decisions
                for value in _uuid_tuple(item.evaluated_version_ids)
            ],
            winning_version_ids=[
                value
                for item in decisions
                for value in _uuid_tuple(item.winning_version_ids)
            ],
            authorized_secret_reference_ids=[
                secret.secret_reference_id
                for secret in policy_data["secret_references"]
                if secret.version_id
                in {
                    credential.secret_reference_version_id
                    for credential in policy_data["credential_requirements"]
                    if credential.secret_reference_version_id is not None
                }
            ],
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
        resolved = await self.repository.get_resolved_configuration_for_run(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
        )
        decisions = await self.repository.list_run_decisions(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
        )
        return RunProvenanceResponse(
            workflow_run_id=workflow_run_id,
            resolved_execution_configuration_id=None
            if resolved is None
            else resolved.resolved_execution_configuration_id,
            resolution_digest=None if resolved is None else resolved.resolution_digest,
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

    async def pin_run_configuration(
        self,
        *,
        principal: PrincipalContext,
        request: PinRunConfigurationRequest,
    ) -> PinRunConfigurationResponse:
        self._authorize_tenant(principal, request.tenant_id, write=False)
        existing = await self.repository.get_resolved_configuration_for_run(
            tenant_id=request.tenant_id,
            workflow_run_id=request.workflow_run_id,
        )
        if existing is not None:
            return _pin_response_from_row(existing)
        policy_data = await self._active_policy_candidates(request.tenant_id)
        model_rows = await self.repository.list_active_model_routes(request.tenant_id)
        prompt_rows = await self.repository.list_active_prompt_references(
            request.tenant_id
        )
        snapshot = ResolvedConfigurationSnapshot(
            tenant_id=request.tenant_id,
            workflow_run_id=request.workflow_run_id,
            run_bundle_id=request.run_bundle_id,
            bundle_digest=request.bundle_digest,
            workflow_version_bundle_id=request.workflow_version_bundle_id,
            model_routing_version_ids=tuple(
                row.model_routing_version_id for row in model_rows
            ),
            prompt_reference_version_ids=tuple(
                row.prompt_reference_version_id for row in prompt_rows
            ),
            prompt_library_version_ids=tuple(
                row.prompt_version_id for row in prompt_rows
            ),
            prompt_library_digests=tuple(row.prompt_digest for row in prompt_rows),
            skill_binding_version_ids=tuple(
                item.version_id for item in policy_data["skill_bindings"]
            ),
            allowed_tool_policy_version_ids=tuple(
                item.version_id for item in policy_data["tool_policies"]
            ),
            outbound_domain_policy_version_ids=tuple(
                item.version_id for item in policy_data["outbound_policies"]
            ),
            secret_reference_version_ids=tuple(
                item.version_id for item in policy_data["secret_references"]
            ),
            credential_requirement_version_ids=tuple(
                item.version_id for item in policy_data["credential_requirements"]
            ),
        )
        row = await self.repository.add_resolved_configuration(
            ResolvedExecutionConfiguration(
                tenant_id=request.tenant_id,
                workflow_run_id=request.workflow_run_id,
                run_bundle_id=request.run_bundle_id,
                bundle_digest=request.bundle_digest,
                workflow_version_bundle_id=request.workflow_version_bundle_id,
                resolved_by_principal_id=request.initiating_principal_id,
                model_routing_version_ids=[
                    str(value) for value in snapshot.model_routing_version_ids
                ],
                prompt_reference_version_ids=[
                    str(value) for value in snapshot.prompt_reference_version_ids
                ],
                skill_binding_version_ids=[
                    str(value) for value in snapshot.skill_binding_version_ids
                ],
                allowed_tool_policy_version_ids=[
                    str(value) for value in snapshot.allowed_tool_policy_version_ids
                ],
                outbound_domain_policy_version_ids=[
                    str(value) for value in snapshot.outbound_domain_policy_version_ids
                ],
                secret_reference_version_ids=[
                    str(value) for value in snapshot.secret_reference_version_ids
                ],
                credential_requirement_version_ids=[
                    str(value) for value in snapshot.credential_requirement_version_ids
                ],
                resolution_digest=snapshot.digest(),
                trace_id=request.trace_id,
                redacted_summary={
                    **(
                        {"workflow_lineage_id": str(request.workflow_lineage_id)}
                        if request.workflow_lineage_id
                        else {}
                    ),
                    "prompt_library_version_ids": [
                        str(value) for value in snapshot.prompt_library_version_ids
                    ],
                    "prompt_library_digests": list(snapshot.prompt_library_digests),
                },
            )
        )
        return _pin_response_from_row(row)

    async def resolve_model_step(
        self,
        *,
        principal: PrincipalContext,
        request: ModelStepResolutionRequest,
    ) -> ModelStepResolutionResponse:
        self._authorize_tenant(principal, request.tenant_id, write=False)
        existing = await self.repository.get_runtime_decision_by_idempotency(
            tenant_id=request.tenant_id,
            workflow_run_id=request.workflow_run_id,
            decision_category=DecisionCategory.MODEL_PROMPT.value,
            idempotency_key=request.idempotency_key,
        )
        scope = ScopeSelector(
            tenant_id=request.tenant_id,
            workflow_lineage_id=request.workflow_lineage_id,
            workflow_version_bundle_id=request.workflow_version_bundle_id,
            agent_key=request.agent_key,
            step_key=request.step_key,
        )
        resolution = resolve_model_prompt(
            model_candidates=[
                _model_candidate_from_row(row)
                for row in await self.repository.list_active_model_routes(
                    request.tenant_id
                )
            ],
            prompt_candidates=[
                _prompt_candidate_from_row(row)
                for row in await self.repository.list_active_prompt_references(
                    request.tenant_id
                )
            ],
            request_scope=scope,
        )
        row = existing or await self.repository.add_runtime_decision(
            RuntimePolicyDecision(
                tenant_id=request.tenant_id,
                workflow_run_id=request.workflow_run_id,
                run_step_id=request.run_step_id,
                run_bundle_id=request.run_bundle_id,
                agent_key=request.agent_key,
                step_key=request.step_key,
                decision_category=DecisionCategory.MODEL_PROMPT.value,
                requested_resource=resolution.model.model_id,
                requested_action="model_step",
                outcome=RuntimeDecisionOutcome.ALLOW,
                safe_reason="model and prompt resolved from pinned candidates",
                evaluated_version_ids=[
                    str(value)
                    for value in (
                        *resolution.model.considered_version_ids,
                        *resolution.prompt.considered_version_ids,
                    )
                ],
                winning_version_ids=[
                    str(resolution.model.model_routing_version_id),
                    str(resolution.prompt.prompt_reference_version_id),
                ],
                source_scopes=[
                    resolution.model.source_scope.value,
                    resolution.prompt.source_scope.value,
                ],
                idempotency_key=request.idempotency_key,
                trace_id=request.trace_id,
                redacted_metadata={"prompt_digest": resolution.prompt.prompt_digest},
            )
        )
        return ModelStepResolutionResponse(
            runtime_policy_decision_id=row.runtime_policy_decision_id,
            outcome=PolicyOutcome(row.outcome.value),
            model_provider_key=resolution.model.provider_key,
            model_id=resolution.model.model_id,
            model_routing_version_id=resolution.model.model_routing_version_id,
            model_source_scope=resolution.model.source_scope.value,
            prompt_reference_version_id=resolution.prompt.prompt_reference_version_id,
            prompt_id=resolution.prompt.prompt_id,
            prompt_version_id=resolution.prompt.prompt_version_id,
            prompt_digest=resolution.prompt.prompt_digest,
            evaluated_version_ids=[
                *resolution.model.considered_version_ids,
                *resolution.prompt.considered_version_ids,
            ],
            safe_reason=row.safe_reason,
        )

    async def evaluate_skill_access(
        self,
        *,
        principal: PrincipalContext,
        request: SkillAccessRequest,
    ) -> PolicyEvaluationResponse:
        self._authorize_tenant(principal, request.tenant_id, write=False)
        scope = ScopeSelector(tenant_id=request.tenant_id, agent_key=request.agent_key)
        policy_data = await self._active_policy_candidates(request.tenant_id)
        decision = evaluate_skill_access_policy(
            candidates=policy_data["skill_bindings"],
            scope=scope,
            skill_slug=request.skill_slug,
            skill_version=request.skill_version,
            use_context=request.use_context,
        )
        row = await self._persist_policy_decision(
            request=request,
            category=DecisionCategory.SKILL,
            decision=decision,
            requested_resource=request.skill_slug,
            requested_action=request.use_context,
        )
        return _policy_response_from_decision(row, decision)

    async def evaluate_tool_use(
        self,
        *,
        principal: PrincipalContext,
        request: ToolUseRequest,
    ) -> PolicyEvaluationResponse:
        self._authorize_tenant(principal, request.tenant_id, write=False)
        scope = ScopeSelector(
            tenant_id=request.tenant_id,
            agent_key=request.agent_key,
            step_key=request.step_key,
        )
        policy_data = await self._active_policy_candidates(request.tenant_id)
        decisions = [
            evaluate_tool_policy(
                candidates=policy_data["tool_policies"],
                scope=scope,
                skill_slug=request.skill_slug,
                tool_id=request.tool_id,
                action_category=request.action_category,
            )
        ]
        if request.destination_url:
            decisions.append(
                evaluate_outbound_policy(
                    candidates=policy_data["outbound_policies"],
                    scope=scope,
                    tool_id=request.tool_id,
                    action_category=request.action_category,
                    destination_url=request.destination_url,
                )
            )
        decisions.append(
            evaluate_credential_requirements(
                requirements=policy_data["credential_requirements"],
                secret_references=policy_data["secret_references"],
                scope=scope,
                tool_id=request.tool_id,
                action_category=request.action_category,
                credential_context=request.credential_context,
                authorized_delegated_credential_link_ids=(
                    request.authorized_delegated_credential_link_ids
                ),
            )
        )
        decision = _first_denial_or_allow(decisions)
        row = await self._persist_policy_decision(
            request=request,
            category=DecisionCategory.TOOL,
            decision=PolicyDecision(
                outcome=decision.outcome,
                denial_category=decision.denial_category,
                safe_reason=decision.safe_reason,
                evaluated_version_ids=tuple(
                    value
                    for item in decisions
                    for value in _uuid_tuple(item.evaluated_version_ids)
                ),
                winning_version_ids=tuple(
                    value
                    for item in decisions
                    for value in _uuid_tuple(item.winning_version_ids)
                ),
            ),
            requested_resource=request.tool_id,
            requested_action=request.action_category,
        )
        return _policy_response_from_decision(row, decision)

    async def _active_policy_candidates(self, tenant_id: UUID) -> dict[str, Any]:
        return {
            "skill_bindings": [
                _skill_binding_candidate_from_row(row)
                for row in await self.repository.list_active_skill_bindings(tenant_id)
            ],
            "tool_policies": [
                _tool_policy_candidate_from_row(row)
                for row in await self.repository.list_active_tool_policies(tenant_id)
            ],
            "outbound_policies": [
                _outbound_policy_candidate_from_row(row)
                for row in await self.repository.list_active_outbound_policies(
                    tenant_id
                )
            ],
            "secret_references": [
                _secret_reference_candidate_from_row(row)
                for row in await self.repository.list_active_secret_references(
                    tenant_id
                )
            ],
            "credential_requirements": [
                _credential_requirement_candidate_from_row(row)
                for row in await self.repository.list_active_credential_requirements(
                    tenant_id
                )
            ],
        }

    async def _persist_policy_decision(
        self,
        *,
        request: SkillAccessRequest | ToolUseRequest,
        category: DecisionCategory,
        decision: PolicyDecision,
        requested_resource: str,
        requested_action: str,
    ) -> RuntimePolicyDecision:
        idempotency_key = request.idempotency_key or (
            f"{request.workflow_run_id}:{request.run_step_id}:"
            f"{category.value}:{requested_resource}:{requested_action}"
        )
        existing = await self.repository.get_runtime_decision_by_idempotency(
            tenant_id=request.tenant_id,
            workflow_run_id=request.workflow_run_id,
            decision_category=category.value,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            return existing
        record_model_skill_policy_decision(
            decision_category=category.value,
            outcome=decision.outcome.value,
            denial_category=None
            if decision.denial_category is None
            else decision.denial_category.value,
        )
        return await self.repository.add_runtime_decision(
            RuntimePolicyDecision(
                tenant_id=request.tenant_id,
                workflow_run_id=request.workflow_run_id,
                run_step_id=request.run_step_id,
                agent_key=request.agent_key,
                step_key=getattr(request, "step_key", None),
                decision_category=category.value,
                requested_resource=requested_resource,
                requested_action=requested_action,
                outcome=RuntimeDecisionOutcome(decision.outcome.value),
                denial_category=None
                if decision.denial_category is None
                else decision.denial_category.value,
                safe_reason=decision.safe_reason,
                evaluated_version_ids=[
                    str(value) for value in _uuid_tuple(decision.evaluated_version_ids)
                ],
                winning_version_ids=[
                    str(value) for value in _uuid_tuple(decision.winning_version_ids)
                ],
                source_scopes=[],
                idempotency_key=idempotency_key,
                trace_id=request.trace_id,
                redacted_metadata={"side_effect_boundary": "before_external_call"},
            )
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
    ) -> ConfigurationAuditRecord:
        return await self.repository.add_audit_record(
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


def _model_candidate_from_row(row: ModelRoutingVersion) -> ModelRoutingCandidate:
    return ModelRoutingCandidate(
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


def _prompt_candidate_from_row(row: PromptReferenceVersion) -> PromptReferenceCandidate:
    return PromptReferenceCandidate(
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


def _skill_binding_candidate_from_row(
    row: SkillBindingVersion,
) -> SkillBindingCandidate:
    return SkillBindingCandidate(
        version_id=row.skill_binding_version_id,
        tenant_id=row.tenant_id,
        scope=_scope_from_row(row),
        status=VersionStatus(row.status.value),
        version_sequence=row.version_sequence,
        activation_reason=row.activation_reason,
        redacted_summary=row.redacted_summary,
        skill_slug=row.skill_slug,
        skill_version=row.skill_version,
        allowed_contexts=tuple(row.allowed_contexts),
        runtime_ref_constraints=row.runtime_ref_constraints,
    )


def _tool_policy_candidate_from_row(
    row: AllowedToolPolicyVersion,
) -> ToolPolicyCandidate:
    return ToolPolicyCandidate(
        version_id=row.allowed_tool_policy_version_id,
        tenant_id=row.tenant_id,
        scope=_scope_from_row(row),
        status=VersionStatus(row.status.value),
        version_sequence=row.version_sequence,
        activation_reason=row.activation_reason,
        redacted_summary=row.redacted_summary,
        skill_slug=row.skill_slug,
        tool_id=row.tool_id,
        allowed_action_categories=tuple(row.allowed_action_categories),
        constraints=row.constraints,
    )


def _outbound_policy_candidate_from_row(
    row: OutboundDomainPolicyVersion,
) -> OutboundPolicyCandidate:
    return OutboundPolicyCandidate(
        version_id=row.outbound_domain_policy_version_id,
        tenant_id=row.tenant_id,
        scope=_scope_from_row(row),
        status=VersionStatus(row.status.value),
        version_sequence=row.version_sequence,
        activation_reason=row.activation_reason,
        redacted_summary=row.redacted_summary,
        tool_id=row.tool_id,
        action_category=row.action_category,
        allowed_domain_patterns=tuple(row.allowed_domain_patterns),
        allowed_schemes=tuple(row.allowed_schemes),
        allowed_ports=tuple(row.allowed_ports),
    )


def _secret_reference_candidate_from_row(
    row: SecretReferenceVersion,
) -> SecretReferenceCandidate:
    return SecretReferenceCandidate(
        version_id=row.secret_reference_version_id,
        tenant_id=row.tenant_id,
        scope=_scope_from_row(row),
        status=VersionStatus(row.status.value),
        version_sequence=row.version_sequence,
        activation_reason=row.activation_reason,
        redacted_summary=row.redacted_summary,
        secret_reference_id=row.secret_reference_id,
        provider_key=row.provider_key,
        external_reference=row.external_reference,
        allowed_scopes=row.allowed_scopes,
        rotation_metadata=row.rotation_metadata,
    )


def _credential_requirement_candidate_from_row(
    row: ToolCredentialRequirementVersion,
) -> CredentialRequirementCandidate:
    return CredentialRequirementCandidate(
        version_id=row.tool_credential_requirement_version_id,
        tenant_id=row.tenant_id,
        scope=_scope_from_row(row),
        status=VersionStatus(row.status.value),
        version_sequence=row.version_sequence,
        activation_reason=row.activation_reason,
        redacted_summary=row.redacted_summary,
        tool_id=row.tool_id,
        action_category=row.action_category,
        credential_kind=row.credential_kind,
        secret_reference_version_id=row.secret_reference_version_id,
        delegated_credential_link_id=row.delegated_credential_link_id,
        allowed_credential_scope=row.allowed_credential_scope,
        expiry_policy=row.expiry_policy,
    )


def _first_denial_or_allow(decisions: list[PolicyDecision]) -> PolicyDecision:
    for decision in decisions:
        if not decision.allowed:
            return decision
    return PolicyDecision(
        outcome=PolicyOutcome.ALLOW,
        denial_category=None,
        safe_reason="all applicable policies allowed",
        evaluated_version_ids=tuple(
            value for decision in decisions for value in decision.evaluated_version_ids
        ),
        winning_version_ids=tuple(
            value for decision in decisions for value in decision.winning_version_ids
        ),
    )


def _uuid_tuple(values: tuple[object, ...]) -> tuple[UUID, ...]:
    return tuple(value for value in values if isinstance(value, UUID))


def _pin_response_from_row(
    row: ResolvedExecutionConfiguration,
) -> PinRunConfigurationResponse:
    raw_prompt_library_version_ids = row.redacted_summary.get(
        "prompt_library_version_ids", []
    )
    prompt_library_version_ids = (
        raw_prompt_library_version_ids
        if isinstance(raw_prompt_library_version_ids, list)
        else []
    )
    raw_prompt_library_digests = row.redacted_summary.get("prompt_library_digests", [])
    prompt_library_digests = (
        raw_prompt_library_digests
        if isinstance(raw_prompt_library_digests, list)
        else []
    )
    return PinRunConfigurationResponse(
        resolved_execution_configuration_id=row.resolved_execution_configuration_id,
        resolution_digest=row.resolution_digest,
        model_routing_version_ids=[
            UUID(value) for value in row.model_routing_version_ids
        ],
        prompt_reference_version_ids=[
            UUID(value) for value in row.prompt_reference_version_ids
        ],
        prompt_library_version_ids=[
            UUID(str(value)) for value in prompt_library_version_ids
        ],
        prompt_library_digests=[str(value) for value in prompt_library_digests],
        skill_binding_version_ids=[
            UUID(value) for value in row.skill_binding_version_ids
        ],
        allowed_tool_policy_version_ids=[
            UUID(value) for value in row.allowed_tool_policy_version_ids
        ],
        outbound_domain_policy_version_ids=[
            UUID(value) for value in row.outbound_domain_policy_version_ids
        ],
        secret_reference_version_ids=[
            UUID(value) for value in row.secret_reference_version_ids
        ],
        credential_requirement_version_ids=[
            UUID(value) for value in row.credential_requirement_version_ids
        ],
        warnings=[],
    )


def _policy_response_from_decision(
    row: RuntimePolicyDecision,
    decision: PolicyDecision,
) -> PolicyEvaluationResponse:
    return PolicyEvaluationResponse(
        runtime_policy_decision_id=row.runtime_policy_decision_id,
        outcome=PolicyOutcome(row.outcome.value),
        evaluated_version_ids=_uuid_list(row.evaluated_version_ids),
        winning_version_ids=_uuid_list(row.winning_version_ids),
        denial_category=decision.denial_category,
        safe_reason=row.safe_reason,
        authorized_secret_reference_ids=[],
        authorized_delegated_credential_link_ids=[],
    )


def _uuid_list(values: list[str]) -> list[UUID]:
    return [UUID(value) for value in values]
