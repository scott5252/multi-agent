from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingCommuteMode,
    BriefingPreferenceAccessScope,
    BriefingPreferenceAction,
    BriefingPreferenceDecision,
    BriefingPreferencePayload,
    BriefingPreferencePermissionError,
    BriefingPreferenceScopeType,
    BriefingPreferenceStaleRevisionError,
)
from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingOutputStyle as DomainBriefingOutputStyle,
)
from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
)
from multi_agent_platform.admin.telegram_config.models import (
    TelegramAccessScope,
    TelegramConfigScopeType,
    TelegramConfigStaleRevisionError,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramProviderReadiness,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
)
from multi_agent_platform.api.schemas.admin_channel_telegram_briefing_react import (
    AliasLifecycleStatus,
    AliasProtectedReadiness,
    BotBoundaryStatus,
    BriefingOutputStyle,
    BriefingPreferenceExportRequest,
    BriefingPreferenceImportRequest,
    BriefingPreferenceList,
    BriefingPreferenceMutationResult,
    BriefingPreferenceProfile,
    BriefingPreferenceSaveRequest,
    ChannelAction,
    ChannelMutationResult,
    ChannelMutationStatus,
    ChannelProblem,
    ChannelReadinessStatus,
    ChannelTelegramBriefingDashboard,
    ChannelTelegramReadiness,
    CommuteMode,
    DeliveryAttemptStatus,
    DeliveryAttemptSummary,
    DeliveryDiagnosticList,
    DeliveryRetryCategory,
    LinkedIdentityStatus,
    LinkedTelegramIdentitySummary,
    LinkTokenCreateRequest,
    LinkTokenResult,
    RunStatusCategory,
    RunStatusSummary,
    TelegramAliasActionRequest,
    TelegramAliasRecord,
    TelegramAliasSaveRequest,
    TelegramConfigSaveRequest,
    TelegramTenantConfiguration,
    WebhookDiagnosticStatus,
    WebhookDiagnosticSummary,
    WebhookValidationRequest,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceProfile as BriefingPreferenceProfileRecord,
)
from multi_agent_platform.db.models.channels import NotificationDeliveryAttemptRecord
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeRunStatus,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.telegram_config import (
    TelegramCommandAlias,
    TelegramDiagnosticEvent,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramUpdateReceipt,
)
from multi_agent_platform.db.models.telegram_config import (
    TelegramTenantConfiguration as TelegramTenantConfigurationRecord,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)

NOT_CONFIGURED_REVISION = "telegram-config-not-configured"
TIME_RE = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")


@dataclass(frozen=True, slots=True)
class ChannelActor:
    platform_admin: bool
    tenant_admin: bool
    tenant_user: bool
    active_tenant_id: UUID | None
    active_tenant_label: str | None
    principal_label: str
    trace_id: str


@dataclass(frozen=True, slots=True)
class TenantProjection:
    tenant_id: UUID
    label: str


async def build_channel_telegram_briefing_dashboard(
    *,
    telegram_service: TelegramConfigurationService,
    telegram_repository: TelegramConfigRepository,
    briefing_service: BriefingPreferenceService,
    briefing_repository: BriefingPreferenceRepository,
    channel_repository: ChannelRepository,
    runtime_repository: RuntimeOrchestrationRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = (),
) -> ChannelTelegramBriefingDashboard:
    actor = _actor(scope=scope, principal=principal)
    tenants = _visible_tenants(actor, allowed_scope_options)
    readiness_model = telegram_service.provider_readiness()
    tenant_snapshots = [
        (
            tenant,
            await telegram_repository.get_tenant_config(tenant.tenant_id),
            await telegram_repository.list_aliases(
                tenant_id=tenant.tenant_id, limit=25
            ),
            await telegram_repository.list_identity_summaries(
                tenant_id=tenant.tenant_id,
                limit=25,
            ),
            await telegram_repository.list_token_audits(
                tenant_id=tenant.tenant_id,
                limit=10,
            ),
            await telegram_repository.list_diagnostics(
                tenant_id=tenant.tenant_id,
                platform_scope=False,
                limit=25,
            ),
            await telegram_repository.list_update_receipts(
                tenant_id=tenant.tenant_id,
                platform_scope=False,
                limit=25,
            ),
            await channel_repository.list_recent_delivery_attempts(
                tenant_id=tenant.tenant_id,
                platform_scope=False,
                limit=25,
            ),
        )
        for tenant in tenants
    ]
    preferences = await build_briefing_preferences(
        briefing_service=briefing_service,
        briefing_repository=briefing_repository,
        scope=scope,
        principal=principal,
        allowed_scope_options=allowed_scope_options,
    )
    run_links = await _run_status_links(
        runtime_repository=runtime_repository,
        actor=actor,
        scope=scope,
    )
    deliveries = tuple(
        attempt
        for tenant, *_rest, delivery_records in tenant_snapshots
        for attempt in _delivery_attempts(
            tenant=tenant,
            actor=actor,
            delivery_records=delivery_records,
        )
    )[:25]
    configs: list[TelegramTenantConfiguration] = []
    alias_records: list[TelegramAliasRecord] = []
    token_audits: list[TelegramLinkTokenAudit] = []
    identity_records: list[LinkedTelegramIdentitySummary] = []
    webhook_records: list[WebhookDiagnosticSummary] = []
    for snapshot in tenant_snapshots:
        (
            tenant,
            config,
            aliases,
            identities,
            tokens,
            diagnostics,
            receipts,
            _delivery_records,
        ) = snapshot
        configs.append(
            _tenant_config(
                tenant=tenant,
                config=config,
                provider_readiness=readiness_model,
                latest_webhook=_latest_webhook_diagnostic(diagnostics),
                actor=actor,
            )
        )
        alias_records.extend(
            _aliases(
                tenant=tenant,
                actor=actor,
                config=config,
                aliases=aliases,
                identities=identities,
            )
        )
        token_audits.extend(tokens)
        identity_records.extend(
            _linked_identities(tenant=tenant, identities=identities)
        )
        webhook_records.append(
            _webhook(
                tenant=tenant,
                diagnostics=diagnostics,
                receipts=receipts,
                fallback_time=_updated_at(config),
            )
        )
    return ChannelTelegramBriefingDashboard(
        page_id="channel-telegram-briefing-live",
        title="Channel, Telegram, and Briefing Preferences",
        description=(
            "Review live channel readiness, Telegram aliases, delivery diagnostics, "
            "run status, and briefing preference evidence."
        ),
        scope=scope,
        allowed_scope_options=_visible_scope_options(actor, allowed_scope_options),
        readiness=tuple(
            _readiness(
                tenant=tenant,
                config=config,
                aliases=aliases,
                identities=identities,
                diagnostics=diagnostics,
                delivery_records=delivery_records,
                preference_profiles=preferences,
                provider_readiness=readiness_model,
            )
            for (
                tenant,
                config,
                aliases,
                identities,
                _tokens,
                diagnostics,
                _receipts,
                delivery_records,
            ) in tenant_snapshots
        ),
        tenant_configs=tuple(configs),
        aliases=tuple(alias_records),
        link_token_result=_masked_link_token(
            actor=actor,
            token_audits=tuple(token_audits),
        ),
        linked_identities=tuple(identity_records),
        webhook_diagnostics=tuple(webhook_records),
        delivery_attempts=deliveries,
        run_status_links=run_links,
        preference_profiles=preferences,
        states=_states(
            actor=actor,
            tenants=tenants,
            has_live_rows=bool(
                alias_records
                or identity_records
                or token_audits
                or deliveries
                or run_links
                or preferences.current_user_profile
                or preferences.admin_summaries
            ),
        ),
        common_states=(),
        updated_at=_now(),
    )


async def build_telegram_config_result(
    *,
    telegram_service: TelegramConfigurationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: TelegramConfigSaveRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not _can_admin(actor):
        return _mutation_denied("Only administrators can update Telegram settings.")
    access_scope = _tenant_access_scope_from_actor(actor)
    if access_scope is None:
        return _mutation_denied("Choose a tenant before updating Telegram settings.")
    try:
        config = await telegram_service.update_tenant_config(
            access_scope=access_scope,
            enabled=request.enabled,
            protected_commands=(),
            status_note="Updated from the admin channel workspace.",
            revision_token=None
            if request.revision == NOT_CONFIGURED_REVISION
            else request.revision,
        )
    except TelegramConfigStaleRevisionError:
        current = await telegram_service.tenant_config(access_scope)
        return ChannelMutationResult(
            status=ChannelMutationStatus.CONFLICT,
            summary="Telegram settings were changed by another administrator.",
            revision=None if current is None else current.revision_token,
            idempotency_key=request.idempotency_key,
            audit_reference="telegram-config-conflict",
            next_step="Reload the workspace and retry with the current revision.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary="Telegram settings saved with service-owned audit evidence.",
        revision=config.revision_token,
        idempotency_key=request.idempotency_key,
        audit_reference=str(config.telegram_tenant_config_id),
        next_step="Run webhook validation to refresh readiness.",
    )


async def build_webhook_validation_result(
    *,
    telegram_service: TelegramConfigurationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: WebhookValidationRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not _can_admin(actor):
        return _mutation_denied(
            "Only administrators can validate Telegram webhook readiness."
        )
    access_scope = _tenant_access_scope_from_actor(
        actor,
        tenant_id=_uuid_or_none(request.tenant_id),
    )
    if access_scope is None:
        return _mutation_denied("Choose a tenant before validating the webhook.")
    diagnostic = await telegram_service.validate_webhook(access_scope)
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary=diagnostic.summary,
        revision=request.revision,
        idempotency_key=request.idempotency_key,
        audit_reference=str(diagnostic.telegram_diagnostic_event_id),
        next_step="Review the refreshed validation timestamp.",
    )


async def build_alias_save_result(
    *,
    telegram_service: TelegramConfigurationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: TelegramAliasSaveRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not _can_admin(actor):
        return _mutation_denied("Only administrators can change Telegram aliases.")
    access_scope = _tenant_access_scope_from_actor(actor)
    if access_scope is None:
        return _mutation_denied("Choose a tenant before changing Telegram aliases.")
    tenant_id = access_scope.require_tenant()
    try:
        alias = await telegram_service.upsert_alias(
            access_scope=access_scope,
            alias_text=request.alias_text,
            published_workflow_version_id=_workflow_version_id(
                tenant_id,
                request.target_summary,
            ),
            description=request.target_summary,
            protected=True,
            enabled=True,
            revision_token=request.revision,
        )
    except TelegramConfigStaleRevisionError:
        return ChannelMutationResult(
            status=ChannelMutationStatus.CONFLICT,
            summary="Telegram alias was changed by another administrator.",
            idempotency_key=request.idempotency_key,
            audit_reference="telegram-alias-conflict",
            next_step="Reload aliases and retry with the current revision.",
        )
    except ValueError as exc:
        return ChannelMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            summary="Alias text needs field corrections.",
            field_errors={"alias_text": str(exc)},
            idempotency_key=request.idempotency_key,
            audit_reference="telegram-alias-validation",
            next_step="Use a non-protected natural-language phrase.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary="Alias saved with protected readiness and audit evidence.",
        revision=alias.revision_token,
        idempotency_key=request.idempotency_key,
        audit_reference=str(alias.telegram_command_alias_id),
        next_step="Review delivery diagnostics after the next trigger.",
    )


async def build_alias_action_result(
    *,
    telegram_service: TelegramConfigurationService,
    telegram_repository: TelegramConfigRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    alias_id: str,
    action: str,
    request: TelegramAliasActionRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not _can_admin(actor):
        return _mutation_denied("Only administrators can run alias lifecycle actions.")
    access_scope = _tenant_access_scope_from_actor(actor)
    if access_scope is None:
        return _mutation_denied("Choose a tenant before changing Telegram aliases.")
    if action not in {"disable", "delete", "refresh"}:
        return ChannelMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            summary="Alias action is not available.",
            field_errors={"action": "Choose disable, delete, or refresh."},
            idempotency_key=request.idempotency_key,
            audit_reference="telegram-alias-action-validation",
            next_step="Use one of the enabled alias actions.",
        )
    alias_uuid = _uuid_or_none(alias_id)
    alias = (
        None
        if alias_uuid is None
        else await telegram_repository.get_alias(
            tenant_id=access_scope.require_tenant(),
            alias_id=alias_uuid,
        )
    )
    if alias is None:
        return ChannelMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            summary="Alias was not found for the active tenant.",
            field_errors={"alias_id": "Alias is unavailable."},
            idempotency_key=request.idempotency_key,
            audit_reference="telegram-alias-action-missing",
            next_step="Reload aliases and choose an available action.",
        )
    if action in {"disable", "delete"}:
        try:
            alias = await telegram_service.upsert_alias(
                access_scope=access_scope,
                alias_text=alias.alias_text,
                published_workflow_version_id=alias.published_workflow_version_id,
                description=alias.description,
                protected=alias.protected,
                enabled=False,
                revision_token=request.revision,
            )
        except TelegramConfigStaleRevisionError:
            return ChannelMutationResult(
                status=ChannelMutationStatus.CONFLICT,
                summary="Telegram alias was changed by another administrator.",
                idempotency_key=request.idempotency_key,
                audit_reference="telegram-alias-action-conflict",
                next_step="Reload aliases and retry with the current revision.",
            )
    else:
        await telegram_repository.add_diagnostic(
            tenant_id=access_scope.tenant_id,
            principal_id=access_scope.principal_id,
            category=TelegramDiagnosticCategory.READINESS,
            status=TelegramDiagnosticStatus.OK,
            summary="Telegram alias readiness refreshed.",
            trace_id=access_scope.principal_id,
            redacted_metadata={"alias_id": str(alias.telegram_command_alias_id)},
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary=f"Alias {action} action recorded with audit evidence.",
        revision=alias.revision_token,
        idempotency_key=request.idempotency_key,
        audit_reference=str(alias.telegram_command_alias_id),
        next_step="Reload aliases to view the updated readiness state.",
    )


async def build_link_token_result(
    *,
    telegram_service: TelegramConfigurationService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: LinkTokenCreateRequest,
) -> LinkTokenResult:
    actor = _actor(scope=scope, principal=principal)
    if not _can_admin(actor):
        return LinkTokenResult(
            link_token_request_id="telegram-link-token-denied",
            masked_status="Denied by tenant scope.",
            expires_at=_now(),
            next_step="Ask a tenant administrator to create a linking code.",
            audit_reference="telegram-link-token-denied",
            display_mode="masked",
        )
    access_scope = _tenant_access_scope_from_actor(actor)
    if access_scope is None:
        return LinkTokenResult(
            link_token_request_id="telegram-link-token-missing-tenant",
            masked_status="Choose a tenant before creating a code.",
            expires_at=_now(),
            next_step="Open an authorized tenant scope.",
            audit_reference="telegram-link-token-denied",
            display_mode="masked",
        )
    issued = await telegram_service.issue_link_token(access_scope)
    return LinkTokenResult(
        link_token_request_id=str(issued.audit.telegram_link_token_audit_id),
        token_value=issued.raw_token,
        masked_status="Visible once. Future views show masked status only.",
        expires_at=issued.audit.expires_at,
        next_step=f"Share this code with {request.principal_label} before it expires.",
        audit_reference=str(issued.audit.telegram_link_token_audit_id),
        display_mode="immediate",
    )


async def build_delivery_diagnostics(
    *,
    telegram_repository: TelegramConfigRepository,
    channel_repository: ChannelRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = (),
) -> DeliveryDiagnosticList:
    actor = _actor(scope=scope, principal=principal)
    tenants = _visible_tenants(actor, allowed_scope_options)
    platform_scope = actor.platform_admin and actor.active_tenant_id is None
    attempts = tuple(
        _delivery_attempt(
            tenant_label=_tenant_label_for_id(record.tenant_id, tenants),
            record=record,
        )
        for record in await channel_repository.list_recent_delivery_attempts(
            tenant_id=actor.active_tenant_id,
            platform_scope=platform_scope,
            limit=25,
        )
    )
    webhook_receipts: list[WebhookDiagnosticSummary] = []
    for tenant in tenants:
        webhook_receipts.append(
            _webhook(
                tenant=tenant,
                diagnostics=await telegram_repository.list_diagnostics(
                    tenant_id=tenant.tenant_id,
                    platform_scope=False,
                    limit=25,
                ),
                receipts=await telegram_repository.list_update_receipts(
                    tenant_id=tenant.tenant_id,
                    platform_scope=False,
                    limit=25,
                ),
                fallback_time=_now(),
            )
        )
    return DeliveryDiagnosticList(
        attempts=attempts,
        total_rows=len(attempts),
        webhook_receipts=tuple(webhook_receipts),
    )


async def build_run_status_summary(
    *,
    runtime_repository: RuntimeOrchestrationRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    workflow_run_id: str,
) -> RunStatusSummary:
    actor = _actor(scope=scope, principal=principal)
    run_uuid = _uuid_or_none(workflow_run_id)
    if run_uuid is None:
        return _unavailable_run(workflow_run_id, actor)
    run = await runtime_repository.get_run_by_id(workflow_run_id=run_uuid)
    if run is None:
        return _unavailable_run(workflow_run_id, actor)
    if not actor.platform_admin and run.tenant_id != actor.active_tenant_id:
        return _unavailable_run(workflow_run_id, actor)
    return _run_summary(run)


async def build_briefing_preferences(
    *,
    briefing_service: BriefingPreferenceService,
    briefing_repository: BriefingPreferenceRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = (),
) -> BriefingPreferenceList:
    actor = _actor(scope=scope, principal=principal)
    tenant_labels = _tenant_labels(allowed_scope_options)
    current_profile: BriefingPreferenceProfile | None = None
    if actor.active_tenant_id is not None:
        access_scope = _briefing_access_scope(actor)
        if access_scope is not None:
            profile = await briefing_service.get_own_profile(access_scope)
            current_profile = (
                None
                if profile is None
                else _preference_profile(profile, tenant_labels=tenant_labels)
            )
    summaries: tuple[BriefingPreferenceProfile, ...] = ()
    if _can_admin(actor):
        summary_scope = _briefing_access_scope(actor, allow_platform=True)
        if summary_scope is not None:
            profiles = await briefing_service.list_summaries(summary_scope)
            summaries = tuple(
                _preference_profile(profile, tenant_labels=tenant_labels)
                for profile in profiles[:20]
            )
    platform_scope = actor.platform_admin and actor.active_tenant_id is None
    audits = await briefing_repository.list_audit_events(
        tenant_id=actor.active_tenant_id,
        platform_scope=platform_scope,
        limit=8,
    )
    return BriefingPreferenceList(
        current_user_profile=current_profile,
        admin_summaries=summaries,
        import_export_evidence=tuple(
            str(audit.briefing_preference_audit_event_id) for audit in audits
        ),
    )


async def build_preference_save_result(
    *,
    briefing_service: BriefingPreferenceService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceSaveRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    access_scope = _briefing_access_scope(actor)
    if access_scope is None:
        return _preference_denied()
    try:
        payload = _preference_payload(request)
        result = await briefing_service.save_own_profile(
            access_scope=access_scope,
            payload=payload,
            revision_token=request.revision,
        )
    except BriefingPreferenceStaleRevisionError:
        return BriefingPreferenceMutationResult(
            status=ChannelMutationStatus.CONFLICT,
            profile_summary="Preference profile was changed by another request.",
            field_errors={},
            audit_reference="briefing-preference-conflict",
            next_step="Reload the profile and retry with the current revision.",
        )
    except (BriefingPreferencePermissionError, PermissionError):
        return _preference_denied()
    except ValueError as exc:
        return BriefingPreferenceMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            profile_summary="Preference profile needs field corrections.",
            field_errors={"preferences": str(exc)},
            audit_reference="briefing-preference-validation",
            next_step="Correct the preference fields and save again.",
        )
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary="Preference profile saved with redacted summaries.",
        revision=result.profile.revision_token,
        audit_reference=str(result.revision.briefing_preference_revision_id),
        next_step="Runtime preference resolution is ready for the next channel run.",
    )


async def build_preference_import_result(
    *,
    briefing_repository: BriefingPreferenceRepository,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceImportRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    access_scope = _briefing_access_scope(actor)
    if access_scope is None:
        return _preference_denied()
    audit = await briefing_repository.add_audit_event(
        tenant_id=access_scope.tenant_id,
        principal_id=access_scope.principal_id,
        actor_principal_id=access_scope.principal_id,
        action=BriefingPreferenceAction.PROFILE_IMPORTED,
        decision=BriefingPreferenceDecision.ALLOW,
        summary="Briefing preference import artifact recorded.",
        trace_id=access_scope.trace_id or actor.trace_id,
        redacted_metadata={
            "artifact_reference": request.artifact_reference,
            "field_count": request.field_count,
        },
    )
    profile = await briefing_repository.get_profile(
        tenant_id=access_scope.require_tenant(),
        principal_id=access_scope.principal_id,
    )
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary="Preference import accepted with safe artifact metadata.",
        revision=None if profile is None else profile.revision_token,
        artifact_reference=request.artifact_reference,
        row_count=request.field_count,
        audit_reference=str(audit.briefing_preference_audit_event_id),
        next_step="Review field counts and revision evidence.",
    )


async def build_preference_export_result(
    *,
    briefing_service: BriefingPreferenceService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceExportRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    access_scope = _briefing_access_scope(actor)
    if access_scope is None:
        return _preference_denied()
    try:
        export = await briefing_service.export_own_profile(access_scope)
    except LookupError:
        return BriefingPreferenceMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            profile_summary="Preference export needs an existing profile.",
            audit_reference="briefing-preference-export-missing",
            next_step="Save preferences before exporting.",
        )
    artifact_reference = (
        f"briefing-export-{export.profile.current_revision_id}-{request.format}"
    )
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary=f"Preference export accepted as {request.format}.",
        revision=export.profile.revision_token,
        artifact_reference=artifact_reference,
        row_count=1,
        audit_reference=str(export.profile.current_revision_id),
        next_step="Use the artifact reference from storage metadata.",
    )


def _actor(*, scope: ReactAdminScope, principal: PrincipalContext) -> ChannelActor:
    roles = set(principal.role_codes)
    platform_admin = "platform_admin" in roles
    tenant_admin = "tenant_admin" in roles
    tenant_user = "tenant_user" in roles or tenant_admin
    active_tenant_id = (
        scope.tenant_id if scope.scope_type == ReactAdminScopeType.TENANT else None
    )
    return ChannelActor(
        platform_admin=platform_admin,
        tenant_admin=tenant_admin,
        tenant_user=tenant_user,
        active_tenant_id=active_tenant_id,
        active_tenant_label=scope.label if active_tenant_id else None,
        principal_label=principal.principal_id,
        trace_id=principal.trace_id or f"react-channel-{principal.principal_id}",
    )


def _visible_tenants(
    actor: ChannelActor,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
) -> tuple[TenantProjection, ...]:
    if actor.platform_admin and actor.active_tenant_id is None:
        return tuple(
            TenantProjection(
                tenant_id=option.scope.tenant_id,
                label=option.scope.label,
            )
            for option in allowed_scope_options
            if option.scope.scope_type == ReactAdminScopeType.TENANT
            and option.scope.tenant_id is not None
        )
    if actor.active_tenant_id is not None:
        return (
            TenantProjection(
                tenant_id=actor.active_tenant_id,
                label=actor.active_tenant_label or "Tenant",
            ),
        )
    return ()


def _visible_scope_options(
    actor: ChannelActor,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
) -> tuple[ReactAdminScopeOption, ...]:
    if actor.platform_admin and actor.active_tenant_id is None:
        return allowed_scope_options
    if actor.active_tenant_id is None:
        return ()
    return tuple(
        option
        for option in allowed_scope_options
        if option.scope.scope_type == ReactAdminScopeType.TENANT
        and option.scope.tenant_id == actor.active_tenant_id
    )


def _readiness(
    *,
    tenant: TenantProjection,
    config: TelegramTenantConfigurationRecord | None,
    aliases: list[TelegramCommandAlias],
    identities: list[TelegramLinkedIdentitySummary],
    diagnostics: list[TelegramDiagnosticEvent],
    delivery_records: list[NotificationDeliveryAttemptRecord],
    preference_profiles: BriefingPreferenceList,
    provider_readiness: TelegramProviderReadiness,
) -> ChannelTelegramReadiness:
    latest_webhook = _latest_webhook_diagnostic(diagnostics)
    enabled = bool(config and config.enabled)
    status = _readiness_status(enabled=enabled, provider_readiness=provider_readiness)
    return ChannelTelegramReadiness(
        readiness_id=f"telegram-readiness-{tenant.tenant_id}",
        status=status,
        channel_label="Telegram",
        tenant_label=tenant.label,
        telegram_enabled=enabled,
        webhook_status=_webhook_status(latest_webhook),
        secret_reference_status=ChannelReadinessStatus.READY
        if provider_readiness.ready
        else ChannelReadinessStatus.PARTIAL
        if provider_readiness.token_reference_configured
        or provider_readiness.webhook_secret_configured
        else ChannelReadinessStatus.UNAVAILABLE,
        linked_identity_count=len(
            [identity for identity in identities if identity.status == "linked"]
        ),
        alias_count=len([alias for alias in aliases if alias.enabled]),
        delivery_health_label=_delivery_health_label(delivery_records),
        preference_resolver_label=_preference_resolver_label(preference_profiles),
        audit_reference=_live_reference(latest_webhook, tenant),
        next_step=_readiness_next_step(status),
    )


def _tenant_config(
    *,
    tenant: TenantProjection,
    config: TelegramTenantConfigurationRecord | None,
    provider_readiness: TelegramProviderReadiness,
    latest_webhook: TelegramDiagnosticEvent | None,
    actor: ChannelActor,
) -> TelegramTenantConfiguration:
    actions: tuple[ChannelAction, ...] = ()
    if _can_admin(actor):
        actions = (
            ChannelAction(
                action_id="validate-webhook",
                label="Validate",
                href="/admin/app/channels/telegram/webhook/validate",
            ),
            ChannelAction(
                action_id="save-config",
                label="Save",
                href="/admin/app/channels/telegram/config",
            ),
        )
    return TelegramTenantConfiguration(
        tenant_id=tenant.tenant_id,
        tenant_label=tenant.label,
        enabled=bool(config and config.enabled),
        bot_token_reference_label=provider_readiness.token_reference_label,
        webhook_signing_reference_label=provider_readiness.webhook_secret_label,
        webhook_url_status=ChannelReadinessStatus.READY
        if provider_readiness.ready
        else ChannelReadinessStatus.UNAVAILABLE,
        revision=NOT_CONFIGURED_REVISION if config is None else config.revision_token,
        last_validated_at=None if latest_webhook is None else latest_webhook.created_at,
        audit_reference=(
            f"telegram-config-{tenant.tenant_id}"
            if config is None
            else str(config.telegram_tenant_config_id)
        ),
        actions=actions,
    )


def _aliases(
    *,
    tenant: TenantProjection,
    actor: ChannelActor,
    config: TelegramTenantConfigurationRecord | None,
    aliases: list[TelegramCommandAlias],
    identities: list[TelegramLinkedIdentitySummary],
) -> tuple[TelegramAliasRecord, ...]:
    if not _can_admin(actor):
        return ()
    return tuple(
        TelegramAliasRecord(
            alias_id=str(alias.telegram_command_alias_id),
            tenant_label=tenant.label,
            alias_text=alias.alias_text,
            target_summary=alias.description
            or f"Workflow version {str(alias.published_workflow_version_id)[:8]}",
            protected_readiness=_alias_readiness(
                config=config,
                identities=identities,
                protected=alias.protected,
            ),
            status=AliasLifecycleStatus.ACTIVE
            if alias.enabled
            else AliasLifecycleStatus.DISABLED,
            revision=alias.revision_token,
            last_used_at=None,
            audit_reference=str(alias.telegram_command_alias_id),
            actions=_alias_actions(alias),
        )
        for alias in aliases[:25]
    )


def _masked_link_token(
    *,
    actor: ChannelActor,
    token_audits: tuple[TelegramLinkTokenAudit, ...],
) -> LinkTokenResult | None:
    if not _can_admin(actor) or not token_audits:
        return None
    latest = sorted(token_audits, key=lambda audit: audit.issued_at, reverse=True)[0]
    return LinkTokenResult(
        link_token_request_id=str(latest.telegram_link_token_audit_id),
        masked_status=f"Latest link code audit is {latest.status}.",
        expires_at=latest.expires_at,
        consumed_at=latest.consumed_at,
        next_step="Create a new code if the user did not link in time.",
        audit_reference=str(latest.telegram_link_token_audit_id),
        display_mode="masked",
    )


def _linked_identities(
    *,
    tenant: TenantProjection,
    identities: list[TelegramLinkedIdentitySummary],
) -> tuple[LinkedTelegramIdentitySummary, ...]:
    return tuple(
        LinkedTelegramIdentitySummary(
            identity_id=str(identity.telegram_linked_identity_summary_id),
            principal_label=identity.platform_identity_id,
            telegram_label=f"Telegram user {identity.telegram_user_display}",
            chat_label=f"Chat {identity.telegram_chat_display}",
            linked_at=identity.linked_at,
            status=LinkedIdentityStatus.LINKED
            if identity.status == "linked"
            else LinkedIdentityStatus.REVOKED,
            audit_reference=str(identity.telegram_linked_identity_summary_id),
        )
        for identity in identities[:25]
        if identity.tenant_id == tenant.tenant_id
    )


def _webhook(
    *,
    tenant: TenantProjection,
    diagnostics: list[TelegramDiagnosticEvent],
    receipts: list[TelegramUpdateReceipt],
    fallback_time: datetime,
) -> WebhookDiagnosticSummary:
    latest = _latest_webhook_diagnostic(diagnostics)
    return WebhookDiagnosticSummary(
        diagnostic_id=(
            f"webhook-live-{tenant.tenant_id}"
            if latest is None
            else str(latest.telegram_diagnostic_event_id)
        ),
        status=_webhook_status(latest),
        last_checked_at=fallback_time if latest is None else latest.created_at,
        safe_update_summary=(
            "No webhook validation has been persisted."
            if latest is None
            else latest.summary
        ),
        receipt_count=min(len(receipts), 50),
        next_step="Run validation after configuration changes.",
        audit_reference=_live_reference(latest, tenant),
    )


def _delivery_attempts(
    *,
    tenant: TenantProjection,
    actor: ChannelActor,
    delivery_records: list[NotificationDeliveryAttemptRecord],
) -> tuple[DeliveryAttemptSummary, ...]:
    if not _can_admin(actor):
        return ()
    return tuple(
        _delivery_attempt(tenant_label=tenant.label, record=record)
        for record in delivery_records[:25]
    )


def _delivery_attempt(
    *,
    tenant_label: str,
    record: NotificationDeliveryAttemptRecord,
) -> DeliveryAttemptSummary:
    return DeliveryAttemptSummary(
        attempt_id=str(record.notification_delivery_attempt_id),
        tenant_label=tenant_label,
        alias_label=f"{record.channel_type.title()} notification",
        status=_delivery_status(record.delivery_status),
        retry_category=_retry_category(record.failure_category),
        bot_api_boundary_status=_bot_boundary_status(record.delivery_status),
        run_status_href=f"/admin/app/channels/runs/{record.run_id}"
        if record.run_id is not None
        else None,
        safe_error_summary=record.failure_category or "No delivery issue recorded.",
        attempted_at=_as_datetime(record.created_at),
        trace_reference=record.trace_id,
        audit_reference=str(record.notification_delivery_attempt_id),
    )


async def _run_status_links(
    *,
    runtime_repository: RuntimeOrchestrationRepository,
    actor: ChannelActor,
    scope: ReactAdminScope,
) -> tuple[RunStatusSummary, ...]:
    if not (actor.platform_admin or actor.tenant_admin or actor.tenant_user):
        return ()
    platform_scope = (
        actor.platform_admin and scope.scope_type == ReactAdminScopeType.PLATFORM
    )
    runs = await runtime_repository.list_recent_runs(
        tenant_id=actor.active_tenant_id,
        platform_scope=platform_scope,
        limit=12,
    )
    return tuple(_run_summary(run) for run in runs)


def _run_summary(run: WorkflowRunRecord) -> RunStatusSummary:
    return RunStatusSummary(
        run_id=str(run.workflow_run_id),
        status=_run_status(run.status),
        workflow_label=f"Workflow run {str(run.workflow_run_id)[:8]}",
        requested_by_label=run.initiating_principal_id,
        started_at=run.started_at,
        completed_at=run.finished_at,
        next_step=_run_next_step(run.status),
        href=f"/admin/app/channels/runs/{run.workflow_run_id}",
        artifact_references=(),
        audit_reference=run.trace_id,
    )


def _unavailable_run(workflow_run_id: str, actor: ChannelActor) -> RunStatusSummary:
    return RunStatusSummary(
        run_id=workflow_run_id,
        status=RunStatusCategory.UNAVAILABLE,
        workflow_label="Unavailable run",
        requested_by_label=actor.principal_label,
        next_step="The current principal cannot inspect this run status.",
        href=f"/admin/app/channels/runs/{workflow_run_id}",
        artifact_references=(),
        audit_reference="channel-run-unavailable",
    )


def _preference_profile(
    profile: BriefingPreferenceProfileRecord,
    *,
    tenant_labels: Mapping[UUID, str],
) -> BriefingPreferenceProfile:
    summary = profile.safe_summary or {}
    topic_count = summary.get("topic_count", len(profile.news_topics or []))
    vip_count = summary.get("vip_sender_count", len(profile.vip_senders or []))
    return BriefingPreferenceProfile(
        profile_id=str(profile.briefing_preference_profile_id),
        tenant_label=tenant_labels.get(
            profile.tenant_id, f"Tenant {profile.tenant_id}"
        ),
        principal_label=profile.principal_id,
        timezone=str(summary.get("timezone") or profile.timezone),
        location_summary=str(summary.get("location_label") or "Region summary"),
        news_topics_summary=f"{topic_count} topic categories",
        vip_sender_summary=f"{vip_count} masked sender hints",
        workday_hours=str(
            summary.get("workday") or f"{profile.workday_start}-{profile.workday_end}"
        ),
        commute_mode=_commute_mode(
            str(summary.get("commute_mode") or profile.commute_mode)
        ),
        default_account_summary=_account_summary(summary),
        output_style=_output_style(
            str(summary.get("output_style") or profile.output_style)
        ),
        scheduled_time_summary=str(summary.get("scheduled_time") or "not scheduled"),
        revision=profile.revision_token,
        runtime_ready=bool(summary.get("profile_ready", True)),
        audit_reference=str(profile.current_revision_id),
    )


def _states(
    *,
    actor: ChannelActor,
    tenants: tuple[TenantProjection, ...],
    has_live_rows: bool,
) -> tuple[ChannelProblem, ...]:
    states: list[ChannelProblem] = []
    if not tenants:
        states.append(
            ChannelProblem(
                reason="denied",
                title="Tenant scope required",
                detail="Choose an authorized tenant before managing channel settings.",
                next_action="Open the scope selector.",
                audit_reference="channel-scope-denied",
            )
        )
    if not _can_admin(actor):
        states.append(
            ChannelProblem(
                reason="read_only",
                title="Read-only channel view",
                detail="Your role can review safe run status and briefing preferences.",
                next_action="Ask a tenant administrator for channel changes.",
                audit_reference="channel-read-only",
            )
        )
    if tenants and not has_live_rows:
        states.append(
            ChannelProblem(
                reason="empty",
                title="No live channel records",
                detail=(
                    "No Telegram aliases, deliveries, runs, or preference records "
                    "are persisted for this scope."
                ),
                next_action=(
                    "Create configuration or save preferences to populate this "
                    "workspace."
                ),
                audit_reference="channel-empty-live-data",
            )
        )
    return tuple(states)


def _tenant_access_scope_from_actor(
    actor: ChannelActor,
    tenant_id: UUID | None = None,
) -> TelegramAccessScope | None:
    selected_tenant = tenant_id or actor.active_tenant_id
    if selected_tenant is None:
        return None
    if not actor.platform_admin and selected_tenant != actor.active_tenant_id:
        return None
    return TelegramAccessScope(
        scope_type=TelegramConfigScopeType.TENANT,
        principal_id=actor.principal_label,
        tenant_id=selected_tenant,
        platform_admin=actor.platform_admin,
    )


def _briefing_access_scope(
    actor: ChannelActor,
    *,
    allow_platform: bool = False,
) -> BriefingPreferenceAccessScope | None:
    if allow_platform and actor.platform_admin and actor.active_tenant_id is None:
        return BriefingPreferenceAccessScope(
            scope_type=BriefingPreferenceScopeType.PLATFORM,
            principal_id=actor.principal_label,
            tenant_id=None,
            platform_admin=True,
            trace_id=actor.trace_id,
        )
    if actor.active_tenant_id is None:
        return None
    if not (actor.platform_admin or actor.tenant_admin or actor.tenant_user):
        return None
    return BriefingPreferenceAccessScope(
        scope_type=BriefingPreferenceScopeType.TENANT,
        principal_id=actor.principal_label,
        tenant_id=actor.active_tenant_id,
        platform_admin=actor.platform_admin,
        trace_id=actor.trace_id,
    )


def _preference_payload(
    request: BriefingPreferenceSaveRequest,
) -> BriefingPreferencePayload:
    workday_start, workday_end = _workday_bounds(request.workday_hours)
    scheduled_time = _scheduled_time(request.scheduled_time_summary)
    return BriefingPreferencePayload(
        location_label=request.location_summary,
        timezone=request.timezone,
        news_topics=(request.news_topics_summary,),
        vip_senders=(request.vip_sender_summary,),
        workday_start=workday_start,
        workday_end=workday_end,
        commute_mode=_domain_commute_mode(request.commute_mode),
        calendar_account_ref="none",
        email_account_ref="none",
        output_style=_domain_output_style(request.output_style),
        scheduled_enabled=scheduled_time is not None,
        scheduled_time=scheduled_time,
    )


def _workday_bounds(value: str) -> tuple[str, str]:
    matches = TIME_RE.findall(value)
    if len(matches) >= 2:
        return matches[0], matches[1]
    return "09:00", "17:00"


def _scheduled_time(value: str | None) -> str | None:
    if not value:
        return None
    match = TIME_RE.search(value)
    return None if match is None else match.group(0)


def _domain_commute_mode(value: CommuteMode) -> BriefingCommuteMode:
    return {
        CommuteMode.CAR: BriefingCommuteMode.DRIVING,
        CommuteMode.TRANSIT: BriefingCommuteMode.TRANSIT,
        CommuteMode.WALK: BriefingCommuteMode.WALKING,
        CommuteMode.BIKE: BriefingCommuteMode.CYCLING,
        CommuteMode.REMOTE: BriefingCommuteMode.REMOTE,
    }.get(value, BriefingCommuteMode.NONE)


def _domain_output_style(value: BriefingOutputStyle) -> DomainBriefingOutputStyle:
    return {
        BriefingOutputStyle.CONCISE: DomainBriefingOutputStyle.CONCISE,
        BriefingOutputStyle.DETAILED: DomainBriefingOutputStyle.DETAILED,
        BriefingOutputStyle.EXECUTIVE: DomainBriefingOutputStyle.EXECUTIVE,
        BriefingOutputStyle.ACTION_FIRST: DomainBriefingOutputStyle.STANDARD,
    }.get(value, DomainBriefingOutputStyle.STANDARD)


def _readiness_status(
    *,
    enabled: bool,
    provider_readiness: TelegramProviderReadiness,
) -> ChannelReadinessStatus:
    if not enabled:
        return ChannelReadinessStatus.DISABLED
    if provider_readiness.ready:
        return ChannelReadinessStatus.READY
    if (
        provider_readiness.token_reference_configured
        or provider_readiness.webhook_secret_configured
    ):
        return ChannelReadinessStatus.PARTIAL
    return ChannelReadinessStatus.UNAVAILABLE


def _webhook_status(
    diagnostic: TelegramDiagnosticEvent | None,
) -> WebhookDiagnosticStatus:
    if diagnostic is None:
        return WebhookDiagnosticStatus.UNAVAILABLE
    status = TelegramDiagnosticStatus(diagnostic.status)
    if status in {TelegramDiagnosticStatus.READY, TelegramDiagnosticStatus.OK}:
        return WebhookDiagnosticStatus.VALID
    if status is TelegramDiagnosticStatus.FAILED:
        return WebhookDiagnosticStatus.FAILED
    if status is TelegramDiagnosticStatus.DENIED:
        return WebhookDiagnosticStatus.FAILED
    return WebhookDiagnosticStatus.STALE


def _delivery_status(value: str) -> DeliveryAttemptStatus:
    return {
        "delivered": DeliveryAttemptStatus.DELIVERED,
        "retrying": DeliveryAttemptStatus.RETRYING,
        "failed": DeliveryAttemptStatus.FAILED,
        "suppressed": DeliveryAttemptStatus.SKIPPED,
        "scheduled": DeliveryAttemptStatus.RETRYING,
    }.get(value, DeliveryAttemptStatus.UNAVAILABLE)


def _retry_category(value: str | None) -> DeliveryRetryCategory:
    if value is None:
        return DeliveryRetryCategory.NONE
    lowered = value.lower()
    if "throttle" in lowered:
        return DeliveryRetryCategory.THROTTLED
    if "policy" in lowered or "denied" in lowered:
        return DeliveryRetryCategory.POLICY_DENIED
    if "dependency" in lowered:
        return DeliveryRetryCategory.DEPENDENCY_UNAVAILABLE
    if "permanent" in lowered:
        return DeliveryRetryCategory.PERMANENT
    return DeliveryRetryCategory.RETRYABLE


def _bot_boundary_status(value: str) -> BotBoundaryStatus:
    return {
        "delivered": BotBoundaryStatus.DELIVERED,
        "failed": BotBoundaryStatus.FAILED,
        "suppressed": BotBoundaryStatus.SKIPPED,
    }.get(value, BotBoundaryStatus.UNAVAILABLE)


def _run_status(value: RuntimeRunStatus) -> RunStatusCategory:
    return {
        RuntimeRunStatus.PENDING: RunStatusCategory.QUEUED,
        RuntimeRunStatus.RUNNABLE: RunStatusCategory.QUEUED,
        RuntimeRunStatus.RUNNING: RunStatusCategory.RUNNING,
        RuntimeRunStatus.PAUSED: RunStatusCategory.WAITING,
        RuntimeRunStatus.WAITING_CHILD: RunStatusCategory.WAITING,
        RuntimeRunStatus.RECOVERABLE_FAILED: RunStatusCategory.RUNNING,
        RuntimeRunStatus.CANCELLING: RunStatusCategory.RUNNING,
        RuntimeRunStatus.SUCCEEDED: RunStatusCategory.COMPLETED,
        RuntimeRunStatus.FAILED: RunStatusCategory.FAILED,
        RuntimeRunStatus.CANCELLED: RunStatusCategory.CANCELLED,
    }[value]


def _run_next_step(value: RuntimeRunStatus) -> str:
    if value in {
        RuntimeRunStatus.SUCCEEDED,
        RuntimeRunStatus.FAILED,
        RuntimeRunStatus.CANCELLED,
    }:
        return "Review safe terminal status and artifact references."
    if value in {RuntimeRunStatus.PAUSED, RuntimeRunStatus.WAITING_CHILD}:
        return "Review the waiting state before taking action."
    return "Review safe progress only."


def _alias_readiness(
    *,
    config: TelegramTenantConfigurationRecord | None,
    identities: list[TelegramLinkedIdentitySummary],
    protected: bool,
) -> AliasProtectedReadiness:
    if not protected:
        return AliasProtectedReadiness.READY
    if config is None or not config.enabled:
        return AliasProtectedReadiness.MISSING_CONFIG
    if not any(identity.status == "linked" for identity in identities):
        return AliasProtectedReadiness.MISSING_IDENTITY
    return AliasProtectedReadiness.READY


def _alias_actions(alias: TelegramCommandAlias) -> tuple[ChannelAction, ...]:
    return (
        ChannelAction(
            action_id="refresh",
            label="Refresh",
            href=f"/admin/app/channels/telegram/aliases/{alias.telegram_command_alias_id}/refresh",
        ),
        ChannelAction(
            action_id="disable",
            label="Disable",
            href=f"/admin/app/channels/telegram/aliases/{alias.telegram_command_alias_id}/disable",
            enabled=alias.enabled,
        ),
        ChannelAction(
            action_id="delete",
            label="Delete",
            href=f"/admin/app/channels/telegram/aliases/{alias.telegram_command_alias_id}/delete",
            enabled=alias.enabled,
        ),
    )


def _latest_webhook_diagnostic(
    diagnostics: list[TelegramDiagnosticEvent],
) -> TelegramDiagnosticEvent | None:
    webhook = [
        item
        for item in diagnostics
        if item.category == TelegramDiagnosticCategory.WEBHOOK_VALIDATION.value
    ]
    return max(webhook, key=lambda item: item.created_at, default=None)


def _delivery_health_label(
    delivery_records: list[NotificationDeliveryAttemptRecord],
) -> str:
    if not delivery_records:
        return "No delivery attempts are persisted."
    if any(record.delivery_status == "failed" for record in delivery_records):
        return "Recent delivery evidence includes failures."
    if any(record.delivery_status == "retrying" for record in delivery_records):
        return "Recent delivery evidence includes retries."
    return "Recent delivery evidence is available."


def _preference_resolver_label(preferences: BriefingPreferenceList) -> str:
    count = len(preferences.admin_summaries)
    if preferences.current_user_profile is not None:
        count += 1
    if count == 0:
        return "No persisted briefing preference profile."
    return f"{count} persisted preference profile(s)."


def _readiness_next_step(status: ChannelReadinessStatus) -> str:
    if status is ChannelReadinessStatus.READY:
        return "Review validation before changing aliases."
    if status is ChannelReadinessStatus.DISABLED:
        return "Enable Telegram before delivery can proceed."
    return "Review provider and webhook readiness."


def _live_reference(
    diagnostic: TelegramDiagnosticEvent | None,
    tenant: TenantProjection,
) -> str:
    if diagnostic is None:
        return f"telegram-live-{tenant.tenant_id}"
    return str(diagnostic.telegram_diagnostic_event_id)


def _commute_mode(value: str) -> CommuteMode:
    return {
        "driving": CommuteMode.CAR,
        "car": CommuteMode.CAR,
        "transit": CommuteMode.TRANSIT,
        "walking": CommuteMode.WALK,
        "walk": CommuteMode.WALK,
        "cycling": CommuteMode.BIKE,
        "bike": CommuteMode.BIKE,
        "remote": CommuteMode.REMOTE,
    }.get(value, CommuteMode.NONE)


def _output_style(value: str) -> BriefingOutputStyle:
    return {
        "concise": BriefingOutputStyle.CONCISE,
        "detailed": BriefingOutputStyle.DETAILED,
        "executive": BriefingOutputStyle.EXECUTIVE,
        "standard": BriefingOutputStyle.CONCISE,
    }.get(value, BriefingOutputStyle.CONCISE)


def _account_summary(summary: Mapping[str, object]) -> str:
    count = sum(
        1
        for key in ("calendar_account_label", "email_account_label")
        if summary.get(key) not in {None, "", "none"}
    )
    return f"{count} masked account refs" if count else "No account refs"


def _tenant_labels(
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
) -> dict[UUID, str]:
    return {
        option.scope.tenant_id: option.scope.label
        for option in allowed_scope_options
        if option.scope.scope_type == ReactAdminScopeType.TENANT
        and option.scope.tenant_id is not None
    }


def _tenant_label_for_id(
    tenant_id: UUID | None,
    tenants: tuple[TenantProjection, ...],
) -> str:
    for tenant in tenants:
        if tenant.tenant_id == tenant_id:
            return tenant.label
    return "Tenant" if tenant_id is None else f"Tenant {str(tenant_id)[:8]}"


def _workflow_version_id(tenant_id: UUID, target_summary: str) -> UUID:
    digest = hashlib.sha256(target_summary.encode("utf-8")).hexdigest()
    return uuid5(NAMESPACE_URL, f"telegram-alias:{tenant_id}:{digest}")


def _uuid_or_none(value: str | UUID | None) -> UUID | None:
    if isinstance(value, UUID):
        return value
    if not value:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        return None


def _updated_at(config: TelegramTenantConfigurationRecord | None) -> datetime:
    if config is None:
        return _now()
    return _as_datetime(config.updated_at)


def _as_datetime(value: object, *, fallback: datetime | None = None) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
    return fallback or _now()


def _now() -> datetime:
    return datetime.now(UTC)


def _can_admin(actor: ChannelActor) -> bool:
    return actor.platform_admin or actor.tenant_admin


def _mutation_denied(summary: str) -> ChannelMutationResult:
    return ChannelMutationResult(
        status=ChannelMutationStatus.DENIED,
        summary=summary,
        audit_reference="channel-mutation-denied",
        next_step="Switch to an authorized tenant administrator.",
    )


def _preference_denied() -> BriefingPreferenceMutationResult:
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.DENIED,
        profile_summary="Preference action denied by scope.",
        audit_reference="briefing-preference-denied",
        next_step="Use your own tenant user profile.",
    )
