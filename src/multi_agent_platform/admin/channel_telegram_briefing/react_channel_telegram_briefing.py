from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

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

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA_NOW = datetime(2026, 5, 5, 17, 0, tzinfo=UTC)
SAFE_RUN_ID = "qa036-run-morning-briefing"


@dataclass(frozen=True, slots=True)
class ChannelActor:
    platform_admin: bool
    tenant_admin: bool
    tenant_user: bool
    active_tenant_id: UUID | None
    active_tenant_label: str | None
    principal_label: str


@dataclass(frozen=True, slots=True)
class TenantProjection:
    tenant_id: UUID
    label: str
    enabled: bool = True


def build_channel_telegram_briefing_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = (),
) -> ChannelTelegramBriefingDashboard:
    actor = _actor(scope=scope, principal=principal)
    tenants = _visible_tenants(actor, allowed_scope_options)
    readiness = tuple(_readiness(tenant) for tenant in tenants)
    configs = tuple(_tenant_config(tenant, actor) for tenant in tenants)
    aliases = tuple(alias for tenant in tenants for alias in _aliases(tenant, actor))
    identities = tuple(
        identity for tenant in tenants for identity in _linked_identities(tenant)
    )
    webhook = tuple(_webhook(tenant) for tenant in tenants)
    deliveries = tuple(
        attempt for tenant in tenants for attempt in _delivery_attempts(tenant, actor)
    )[:25]
    run_links = tuple(
        link for tenant in tenants for link in _run_status_links(tenant, actor)
    )
    preferences = build_briefing_preferences(
        scope=scope,
        principal=principal,
        allowed_scope_options=allowed_scope_options,
    )
    return ChannelTelegramBriefingDashboard(
        page_id="qa036-channel-telegram-briefing",
        title="Channel, Telegram, and Briefing Preferences",
        description=(
            "Review channel readiness, Telegram aliases, delivery diagnostics, "
            "safe run status, and briefing preference evidence."
        ),
        scope=scope,
        allowed_scope_options=_visible_scope_options(actor, allowed_scope_options),
        readiness=readiness,
        tenant_configs=configs,
        aliases=aliases,
        link_token_result=_masked_link_token(actor),
        linked_identities=identities,
        webhook_diagnostics=webhook,
        delivery_attempts=deliveries,
        run_status_links=run_links,
        preference_profiles=preferences,
        states=_states(actor=actor, tenants=tenants),
        common_states=(),
        updated_at=QA_NOW,
    )


def build_telegram_config_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: TelegramConfigSaveRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_admin and not actor.platform_admin:
        return _mutation_denied("Only administrators can update Telegram settings.")
    if request.revision != "telegram-config-rev-qa036":
        return ChannelMutationResult(
            status=ChannelMutationStatus.CONFLICT,
            summary="Telegram settings were changed by another administrator.",
            revision="telegram-config-rev-qa036",
            audit_reference="audit-qa036-telegram-config-conflict",
            next_step="Reload the workspace and retry with the current revision.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary="Telegram settings saved with safe references and audit evidence.",
        revision="telegram-config-rev-qa036-next",
        idempotency_key=request.idempotency_key,
        audit_reference="audit-qa036-telegram-config-save",
        next_step="Run webhook validation to refresh readiness.",
    )


def build_webhook_validation_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: WebhookValidationRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_admin and not actor.platform_admin:
        return _mutation_denied(
            "Only administrators can validate Telegram webhook readiness."
        )
    if request.idempotency_key and request.idempotency_key.endswith("replay"):
        return ChannelMutationResult(
            status=ChannelMutationStatus.REPLAYED,
            summary="Webhook validation replayed from prior safe evidence.",
            revision=request.revision,
            idempotency_key=request.idempotency_key,
            replayed=True,
            audit_reference="audit-qa036-webhook-replay",
            next_step="Review the refreshed validation timestamp.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary="Webhook validation completed with local mock-safe evidence.",
        revision=request.revision,
        idempotency_key=request.idempotency_key,
        audit_reference="audit-qa036-webhook-validate",
        next_step="Delivery diagnostics can now use the refreshed readiness state.",
    )


def build_alias_save_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: TelegramAliasSaveRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_admin and not actor.platform_admin:
        return _mutation_denied("Only administrators can change Telegram aliases.")
    if request.alias_text.strip().lower() == "/start":
        return ChannelMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            summary="Alias text is reserved for protected command handling.",
            field_errors={"alias_text": "Choose a natural-language phrase."},
            audit_reference="audit-qa036-alias-validation",
            next_step="Use a phrase such as Morning briefing.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary="Alias saved with protected readiness and idempotency evidence.",
        revision="alias-rev-qa036-next",
        idempotency_key=request.idempotency_key,
        audit_reference="audit-qa036-alias-save",
        next_step="Review delivery diagnostics after the next trigger.",
    )


def build_alias_action_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    alias_id: str,
    action: str,
    request: TelegramAliasActionRequest,
) -> ChannelMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_admin and not actor.platform_admin:
        return _mutation_denied("Only administrators can run alias lifecycle actions.")
    if action not in {"disable", "delete", "refresh"}:
        return ChannelMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            summary="Alias action is not available.",
            field_errors={"action": "Choose disable, delete, or refresh."},
            audit_reference="audit-qa036-alias-action-validation",
            next_step="Use one of the enabled alias actions.",
        )
    return ChannelMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        summary=f"Alias {alias_id} {action} action recorded with audit evidence.",
        revision="alias-rev-qa036-action",
        idempotency_key=request.idempotency_key,
        audit_reference=f"audit-qa036-alias-{action}",
        next_step="Reload aliases to view the updated readiness state.",
    )


def build_link_token_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: LinkTokenCreateRequest,
) -> LinkTokenResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_admin and not actor.platform_admin:
        return LinkTokenResult(
            link_token_request_id="link-token-denied-qa036",
            masked_status="Denied by tenant scope.",
            expires_at=QA_NOW + timedelta(minutes=1),
            next_step="Ask a tenant administrator to create a linking code.",
            audit_reference="audit-qa036-link-token-denied",
            display_mode="masked",
        )
    return LinkTokenResult(
        link_token_request_id="link-token-request-qa036",
        token_value=f"pair-code-{request.expires_in_minutes:02d}-qa036",
        masked_status="Visible once. Future views show masked status only.",
        expires_at=QA_NOW + timedelta(minutes=request.expires_in_minutes),
        next_step=f"Share this code with {request.principal_label} before it expires.",
        audit_reference="audit-qa036-link-token-create",
        display_mode="immediate",
    )


def build_delivery_diagnostics(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> DeliveryDiagnosticList:
    actor = _actor(scope=scope, principal=principal)
    tenants = _visible_tenants(actor, ())
    attempts = tuple(
        attempt for tenant in tenants for attempt in _delivery_attempts(tenant, actor)
    )[:25]
    return DeliveryDiagnosticList(
        attempts=attempts,
        total_rows=len(attempts),
        webhook_receipts=tuple(_webhook(tenant) for tenant in tenants),
    )


def build_run_status_summary(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    workflow_run_id: str,
) -> RunStatusSummary:
    actor = _actor(scope=scope, principal=principal)
    if workflow_run_id not in {SAFE_RUN_ID, "qa036-run-support"}:
        return RunStatusSummary(
            run_id="qa036-run-unavailable",
            status=RunStatusCategory.UNAVAILABLE,
            workflow_label="Unavailable run",
            requested_by_label=actor.principal_label,
            next_step="The current principal cannot inspect this run status.",
            href=f"/admin/app/channels/runs/{workflow_run_id}",
            artifact_references=(),
            audit_reference="audit-qa036-run-denied",
        )
    return RunStatusSummary(
        run_id=workflow_run_id,
        status=RunStatusCategory.RUNNING,
        workflow_label="Daily briefing workflow",
        requested_by_label=actor.principal_label,
        started_at=QA_NOW - timedelta(minutes=6),
        next_step="The run is collecting safe briefing context.",
        href=f"/admin/app/channels/runs/{workflow_run_id}",
        artifact_references=("artifact-ref-qa036-safe-status",),
        audit_reference="audit-qa036-run-status",
    )


def build_briefing_preferences(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = (),
) -> BriefingPreferenceList:
    actor = _actor(scope=scope, principal=principal)
    tenant_label = actor.active_tenant_label or "Platform"
    current_profile = _preference_profile(
        tenant_label=tenant_label,
        principal_label=actor.principal_label,
        profile_id="briefing-profile-current-qa036",
    )
    summaries: tuple[BriefingPreferenceProfile, ...] = ()
    if actor.tenant_admin or actor.platform_admin:
        summaries = tuple(
            _preference_profile(
                tenant_label=tenant.label,
                principal_label=f"{tenant.label} user summary",
                profile_id=f"briefing-profile-{tenant.label.lower()}-qa036",
                admin_summary=True,
            )
            for tenant in _visible_tenants(actor, allowed_scope_options)
        )
    return BriefingPreferenceList(
        current_user_profile=current_profile,
        admin_summaries=summaries,
        import_export_evidence=(
            "preference-artifact-qa036",
            "audit-qa036-briefing-preferences",
        ),
    )


def build_preference_save_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceSaveRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_user and not actor.tenant_admin and not actor.platform_admin:
        return _preference_denied()
    if request.timezone not in {"America/New_York", "America/Chicago", "UTC"}:
        return BriefingPreferenceMutationResult(
            status=ChannelMutationStatus.VALIDATION_ERROR,
            profile_summary="Preference profile needs field corrections.",
            field_errors={"timezone": "Choose a supported timezone."},
            audit_reference="audit-qa036-preference-validation",
            next_step="Correct the timezone and save again.",
        )
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary="Preference profile saved with redacted summaries.",
        revision="briefing-pref-rev-qa036-next",
        audit_reference="audit-qa036-preference-save",
        next_step="Runtime preference resolution is ready for the next briefing run.",
    )


def build_preference_import_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceImportRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_user and not actor.tenant_admin and not actor.platform_admin:
        return _preference_denied()
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary="Preference import accepted with safe artifact metadata.",
        revision="briefing-pref-rev-qa036-import",
        artifact_reference=request.artifact_reference,
        row_count=request.field_count,
        audit_reference="audit-qa036-preference-import",
        next_step="Review field counts and revision evidence.",
    )


def build_preference_export_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: BriefingPreferenceExportRequest,
) -> BriefingPreferenceMutationResult:
    actor = _actor(scope=scope, principal=principal)
    if not actor.tenant_user and not actor.tenant_admin and not actor.platform_admin:
        return _preference_denied()
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.ACCEPTED,
        profile_summary=f"Preference export accepted as {request.format}.",
        revision="briefing-pref-rev-qa036-export",
        artifact_reference="preference-export-artifact-qa036",
        row_count=1,
        audit_reference="audit-qa036-preference-export",
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
    )


def _visible_tenants(
    actor: ChannelActor,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
) -> tuple[TenantProjection, ...]:
    if actor.platform_admin and actor.active_tenant_id is None:
        tenant_options = tuple(
            TenantProjection(
                tenant_id=option.scope.tenant_id,
                label=option.scope.label,
                enabled=option.scope.label != "Globex",
            )
            for option in allowed_scope_options
            if option.scope.scope_type == ReactAdminScopeType.TENANT
            and option.scope.tenant_id is not None
        )
        if tenant_options:
            return tenant_options
        return (
            TenantProjection(tenant_id=ACME_TENANT_ID, label="Acme"),
            TenantProjection(tenant_id=GLOBEX_TENANT_ID, label="Globex", enabled=False),
        )
    if actor.active_tenant_id is not None:
        return (
            TenantProjection(
                tenant_id=actor.active_tenant_id,
                label=actor.active_tenant_label or "Tenant",
                enabled=True,
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


def _readiness(tenant: TenantProjection) -> ChannelTelegramReadiness:
    return ChannelTelegramReadiness(
        readiness_id=f"readiness-{tenant.label.lower()}-qa036",
        status=ChannelReadinessStatus.READY
        if tenant.enabled
        else ChannelReadinessStatus.PARTIAL,
        channel_label="Telegram",
        tenant_label=tenant.label,
        telegram_enabled=tenant.enabled,
        webhook_status=WebhookDiagnosticStatus.VALID
        if tenant.enabled
        else WebhookDiagnosticStatus.STALE,
        secret_reference_status=ChannelReadinessStatus.READY,
        linked_identity_count=2 if tenant.enabled else 1,
        alias_count=2 if tenant.enabled else 1,
        delivery_health_label="Recent delivery evidence is healthy"
        if tenant.enabled
        else "Delivery evidence needs review",
        preference_resolver_label="Briefing resolver ready",
        audit_reference=f"audit-qa036-readiness-{tenant.label.lower()}",
        next_step="Refresh webhook validation before changing aliases."
        if tenant.enabled
        else "Enable Telegram before delivery can proceed.",
    )


def _tenant_config(
    tenant: TenantProjection,
    actor: ChannelActor,
) -> TelegramTenantConfiguration:
    actions: tuple[ChannelAction, ...] = ()
    if actor.platform_admin or actor.tenant_admin:
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
        enabled=tenant.enabled,
        bot_token_reference_label="Telegram provider ref ready",
        webhook_signing_reference_label="Webhook signing ref ready",
        webhook_url_status=ChannelReadinessStatus.READY
        if tenant.enabled
        else ChannelReadinessStatus.STALE,
        revision="telegram-config-rev-qa036",
        last_validated_at=QA_NOW - timedelta(minutes=18),
        audit_reference=f"audit-qa036-config-{tenant.label.lower()}",
        actions=actions,
    )


def _aliases(
    tenant: TenantProjection,
    actor: ChannelActor,
) -> tuple[TelegramAliasRecord, ...]:
    if not (actor.platform_admin or actor.tenant_admin):
        return ()
    action_base = (
        ChannelAction(
            action_id="refresh",
            label="Refresh",
            href="/admin/app/channels/telegram/aliases/alias-morning-qa036/refresh",
        ),
        ChannelAction(
            action_id="disable",
            label="Disable",
            href="/admin/app/channels/telegram/aliases/alias-morning-qa036/disable",
        ),
        ChannelAction(
            action_id="delete",
            label="Delete",
            href="/admin/app/channels/telegram/aliases/alias-morning-qa036/delete",
        ),
    )
    return (
        TelegramAliasRecord(
            alias_id="alias-morning-qa036",
            tenant_label=tenant.label,
            alias_text="Morning briefing",
            target_summary="Daily briefing workflow",
            protected_readiness=AliasProtectedReadiness.READY
            if tenant.enabled
            else AliasProtectedReadiness.MISSING_CONFIG,
            status=AliasLifecycleStatus.ACTIVE
            if tenant.enabled
            else AliasLifecycleStatus.PENDING_VALIDATION,
            revision="alias-rev-qa036",
            last_used_at=QA_NOW - timedelta(hours=2),
            audit_reference=f"audit-qa036-alias-{tenant.label.lower()}",
            actions=action_base,
        ),
    )


def _masked_link_token(actor: ChannelActor) -> LinkTokenResult | None:
    if not (actor.platform_admin or actor.tenant_admin):
        return None
    return LinkTokenResult(
        link_token_request_id="link-token-request-qa036-hidden",
        masked_status="Previously created code is hidden after creation.",
        expires_at=QA_NOW + timedelta(minutes=4),
        consumed_at=None,
        next_step="Create a new code if the user did not link in time.",
        audit_reference="audit-qa036-link-token-hidden",
        display_mode="masked",
    )


def _linked_identities(
    tenant: TenantProjection,
) -> tuple[LinkedTelegramIdentitySummary, ...]:
    return (
        LinkedTelegramIdentitySummary(
            identity_id=f"identity-{tenant.label.lower()}-qa036",
            principal_label=f"{tenant.label} briefing user",
            telegram_label="Telegram user tg-***-1842",
            chat_label="Chat chat-***-9081",
            linked_at=QA_NOW - timedelta(days=3),
            status=LinkedIdentityStatus.LINKED,
            audit_reference=f"audit-qa036-identity-{tenant.label.lower()}",
        ),
    )


def _webhook(tenant: TenantProjection) -> WebhookDiagnosticSummary:
    return WebhookDiagnosticSummary(
        diagnostic_id=f"webhook-{tenant.label.lower()}-qa036",
        status=WebhookDiagnosticStatus.VALID
        if tenant.enabled
        else WebhookDiagnosticStatus.STALE,
        last_checked_at=QA_NOW - timedelta(minutes=18),
        safe_update_summary="Mock-safe receipt categories are current"
        if tenant.enabled
        else "Validation should be refreshed before delivery",
        receipt_count=3 if tenant.enabled else 1,
        next_step="Run validation again after configuration changes.",
        audit_reference=f"audit-qa036-webhook-{tenant.label.lower()}",
    )


def _delivery_attempts(
    tenant: TenantProjection,
    actor: ChannelActor,
) -> tuple[DeliveryAttemptSummary, ...]:
    if not (actor.platform_admin or actor.tenant_admin):
        return ()
    return (
        DeliveryAttemptSummary(
            attempt_id=f"delivery-{tenant.label.lower()}-qa036-1",
            tenant_label=tenant.label,
            alias_label="Morning briefing",
            status=DeliveryAttemptStatus.DELIVERED
            if tenant.enabled
            else DeliveryAttemptStatus.RETRYING,
            retry_category=DeliveryRetryCategory.NONE
            if tenant.enabled
            else DeliveryRetryCategory.RETRYABLE,
            bot_api_boundary_status=BotBoundaryStatus.MOCKED,
            run_status_href=f"/admin/app/channels/runs/{SAFE_RUN_ID}",
            safe_error_summary="No delivery issue"
            if tenant.enabled
            else "Retry queued by local boundary",
            attempted_at=QA_NOW - timedelta(minutes=12),
            trace_reference=f"trace-qa036-delivery-{tenant.label.lower()}",
            audit_reference=f"audit-qa036-delivery-{tenant.label.lower()}",
        ),
    )


def _run_status_links(
    tenant: TenantProjection,
    actor: ChannelActor,
) -> tuple[RunStatusSummary, ...]:
    if not (actor.platform_admin or actor.tenant_admin or actor.tenant_user):
        return ()
    return (
        RunStatusSummary(
            run_id=SAFE_RUN_ID,
            status=RunStatusCategory.RUNNING,
            workflow_label="Daily briefing workflow",
            requested_by_label=f"{tenant.label} briefing user",
            started_at=QA_NOW - timedelta(minutes=6),
            next_step="Review safe progress only.",
            href=f"/admin/app/channels/runs/{SAFE_RUN_ID}",
            artifact_references=("artifact-ref-qa036-safe-status",),
            audit_reference=f"audit-qa036-run-{tenant.label.lower()}",
        ),
    )


def _preference_profile(
    *,
    tenant_label: str,
    principal_label: str,
    profile_id: str,
    admin_summary: bool = False,
) -> BriefingPreferenceProfile:
    return BriefingPreferenceProfile(
        profile_id=profile_id,
        tenant_label=tenant_label,
        principal_label=principal_label,
        timezone="America/New_York",
        location_summary="Region summary only"
        if admin_summary
        else "Metro area summary",
        news_topics_summary="4 topic categories",
        vip_sender_summary="3 masked sender hints",
        workday_hours="08:30-17:30",
        commute_mode=CommuteMode.TRANSIT,
        default_account_summary="2 masked account refs",
        output_style=BriefingOutputStyle.EXECUTIVE,
        scheduled_time_summary="Profile preference 07:45",
        revision="briefing-pref-rev-qa036",
        runtime_ready=True,
        audit_reference=f"audit-qa036-pref-{tenant_label.lower()}",
    )


def _states(
    *,
    actor: ChannelActor,
    tenants: tuple[TenantProjection, ...],
) -> tuple[ChannelProblem, ...]:
    states: list[ChannelProblem] = []
    if not tenants:
        states.append(
            ChannelProblem(
                reason="denied",
                title="Tenant scope required",
                detail="Choose an authorized tenant before managing channel settings.",
                next_action="Open the scope selector.",
                audit_reference="audit-qa036-scope-denied",
            )
        )
    if not actor.platform_admin and not actor.tenant_admin:
        states.append(
            ChannelProblem(
                reason="read_only",
                title="Read-only channel view",
                detail="Your role can review safe run status and briefing preferences.",
                next_action="Ask a tenant administrator for channel changes.",
                audit_reference="audit-qa036-read-only",
            )
        )
    states.append(
        ChannelProblem(
            reason="stale_validation",
            title="Validation age",
            detail="Webhook validation is older than the preferred review window.",
            next_action="Run validation when changing Telegram settings.",
            audit_reference="audit-qa036-validation-age",
        )
    )
    return tuple(states)


def _mutation_denied(summary: str) -> ChannelMutationResult:
    return ChannelMutationResult(
        status=ChannelMutationStatus.DENIED,
        summary=summary,
        audit_reference="audit-qa036-mutation-denied",
        next_step="Switch to an authorized tenant administrator.",
    )


def _preference_denied() -> BriefingPreferenceMutationResult:
    return BriefingPreferenceMutationResult(
        status=ChannelMutationStatus.DENIED,
        profile_summary="Preference action denied by scope.",
        audit_reference="audit-qa036-preference-denied",
        next_step="Use your own tenant user profile.",
    )
