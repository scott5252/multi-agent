from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAction,
    BriefingPreferenceDecision,
    BriefingPreferencePayload,
)
from multi_agent_platform.admin.briefing_preferences.redaction import (
    content_digest,
    safe_summary_for_payload,
)
from multi_agent_platform.admin.telegram_config.models import (
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
)
from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
)
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceAuditEvent,
    BriefingPreferenceProfile,
    BriefingPreferenceRevision,
)
from multi_agent_platform.db.models.channels import (
    NotificationDeliveryAttemptRecord,
)
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.telegram_config import (
    TelegramCommandAlias,
    TelegramDiagnosticEvent,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramTenantConfiguration,
    TelegramUpdateReceipt,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowKind,
    WorkflowLineage,
    WorkflowLineageStatus,
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


@dataclass(frozen=True, slots=True)
class ChannelTelegramBriefingSeed:
    tenant_id: UUID
    other_tenant_id: UUID
    alias_id: UUID
    run_id: UUID
    delivery_attempt_id: UUID
    profile_id: UUID


async def seed_channel_telegram_briefing_live_data(
    session: AsyncSession,
) -> ChannelTelegramBriefingSeed:
    await _merge_tenants(session)
    await session.flush()
    now = datetime.now(UTC)
    alias_id = uuid4()
    run_id = uuid4()
    workflow_version_id = await _create_workflow_version(
        session,
        tenant_id=ACME_TENANT_ID,
    )
    profile_payload = _preference_payload()
    briefing_repository = BriefingPreferenceRepository(session)
    profile, revision, _created = await briefing_repository.upsert_profile(
        tenant_id=ACME_TENANT_ID,
        principal_id="tenant-user-acme",
        payload=profile_payload,
        expected_revision_token=None,
        actor_principal_id="tenant-user-acme",
        trace_id="trace-channel-live-pref",
    )
    telegram_repository = TelegramConfigRepository(session)
    config = await telegram_repository.update_tenant_config(
        tenant_id=ACME_TENANT_ID,
        enabled=True,
        protected_commands=["/run", "/status"],
        status_note="Telegram enabled for channel QA.",
        expected_revision_token=None,
        principal_id="tenant-admin-acme",
    )
    alias = TelegramCommandAlias(
        telegram_command_alias_id=alias_id,
        tenant_id=ACME_TENANT_ID,
        alias_text="Morning briefing",
        alias_normalized="morning briefing",
        published_workflow_version_id=workflow_version_id,
        description="Configured workflow",
        protected=True,
        enabled=True,
        revision_token="alias-live-rev",
        created_by_principal_id="tenant-admin-acme",
        updated_by_principal_id="tenant-admin-acme",
    )
    session.add(alias)
    session.add(
        TelegramLinkedIdentitySummary(
            tenant_id=ACME_TENANT_ID,
            platform_identity_id="tenant-user-acme",
            telegram_user_fingerprint="user-fingerprint-live",
            telegram_chat_fingerprint="chat-fingerprint-live",
            telegram_user_display="tg-***-1842",
            telegram_chat_display="chat-***-9081",
            status="linked",
            command_ready=True,
            trace_id="trace-channel-live-identity",
        )
    )
    session.add(
        TelegramLinkTokenAudit(
            tenant_id=ACME_TENANT_ID,
            issued_by_principal_id="tenant-admin-acme",
            token_fingerprint="link-fingerprint-live",
            status="issued",
            expires_at=now + timedelta(minutes=10),
            trace_id="trace-channel-live-token",
        )
    )
    diagnostic = await telegram_repository.add_diagnostic(
        tenant_id=ACME_TENANT_ID,
        principal_id="tenant-admin-acme",
        category=TelegramDiagnosticCategory.WEBHOOK_VALIDATION,
        status=TelegramDiagnosticStatus.READY,
        summary="Webhook configuration is ready for local command validation.",
        trace_id="trace-channel-live-webhook",
        redacted_metadata={"external_call_performed": False},
    )
    session.add(
        TelegramUpdateReceipt(
            telegram_update_id=55001,
            tenant_id=ACME_TENANT_ID,
            platform_identity_id="tenant-user-acme",
            telegram_chat_fingerprint="chat-fingerprint-live",
            action_type="alias_trigger",
            response_payload={"category": "accepted"},
            run_id=run_id,
            delivery_attempt_id=None,
            trace_id="trace-channel-live-receipt",
            received_at=now,
        )
    )
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=ACME_TENANT_ID,
        workflow_run_id=run_id,
        published_workflow_version_id=workflow_version_id,
        bundle_digest="c" * 64,
    )
    session.add(bundle)
    await session.flush()
    run = WorkflowRunRecord(
        workflow_run_id=run_id,
        tenant_id=ACME_TENANT_ID,
        scope_type="tenant",
        initiating_principal_id="tenant-user-acme",
        run_bundle_id=bundle.run_bundle_id,
        status=RuntimeRunStatus.RUNNING,
        idempotency_key="channel-live-run",
        trace_id="trace-channel-live-run",
        started_at=now - timedelta(minutes=5),
    )
    session.add(run)
    delivery_id = uuid4()
    session.add(
        NotificationDeliveryAttemptRecord(
            notification_delivery_attempt_id=delivery_id,
            tenant_id=ACME_TENANT_ID,
            notification_subscription_id=uuid4(),
            run_id=run_id,
            channel_type="telegram",
            event_type="run_status",
            payload_fingerprint="payload-fingerprint-live",
            delivery_status="delivered",
            destination_fingerprint="chat-fingerprint-live",
            provider_message_id="provider-msg-live",
            failure_category=None,
            attempt_number=1,
            trace_id="trace-channel-live-delivery",
            created_at=now - timedelta(minutes=3),
            delivered_at=now - timedelta(minutes=2),
        )
    )
    await session.flush()
    _ = config, diagnostic, revision
    return ChannelTelegramBriefingSeed(
        tenant_id=ACME_TENANT_ID,
        other_tenant_id=GLOBEX_TENANT_ID,
        alias_id=alias_id,
        run_id=run_id,
        delivery_attempt_id=delivery_id,
        profile_id=profile.briefing_preference_profile_id,
    )


def seed_channel_telegram_briefing_live_data_sync(
    session: Session,
    *,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> dict[str, UUID]:
    _merge_tenants_sync(session, tenant_id=tenant_id, other_tenant_id=other_tenant_id)
    now = datetime.now(UTC)
    alias_id = uuid4()
    run_id = uuid4()
    workflow_version_id = _create_workflow_version_sync(session, tenant_id=tenant_id)
    profile_id = uuid4()
    revision_id = uuid4()
    payload = _preference_payload().to_storage()
    digest = content_digest(payload)
    safe_summary = safe_summary_for_payload(
        payload,
        revision_id=revision_id,
        content_hash=digest,
    )
    session.add(
        BriefingPreferenceProfile(
            briefing_preference_profile_id=profile_id,
            tenant_id=tenant_id,
            principal_id="tenant-user-acme",
            location_label="Metro area summary",
            timezone="America/New_York",
            news_topics=["Operations"],
            vip_senders=["vip@example.test"],
            workday_start="08:30",
            workday_end="17:30",
            commute_mode="transit",
            calendar_account_ref="none",
            email_account_ref="none",
            output_style="executive",
            scheduled_enabled=True,
            scheduled_time="07:45",
            current_revision_id=revision_id,
            revision_number=1,
            content_digest=digest,
            safe_summary=safe_summary,
            revision_token="briefing-live-rev",
        )
    )
    session.add(
        BriefingPreferenceRevision(
            briefing_preference_revision_id=revision_id,
            briefing_preference_profile_id=profile_id,
            tenant_id=tenant_id,
            principal_id="tenant-user-acme",
            revision_number=1,
            preference_payload=payload,
            safe_summary=safe_summary,
            content_digest=digest,
            created_by_principal_id="tenant-user-acme",
            trace_id="trace-channel-live-pref",
        )
    )
    session.add(
        BriefingPreferenceAuditEvent(
            tenant_id=tenant_id,
            principal_id="tenant-user-acme",
            actor_principal_id="tenant-user-acme",
            action=BriefingPreferenceAction.PROFILE_CREATED.value,
            decision=BriefingPreferenceDecision.ALLOW.value,
            summary="Briefing preference profile saved.",
            profile_id=profile_id,
            revision_id=revision_id,
            content_digest=digest,
            trace_id="trace-channel-live-pref",
            redacted_metadata=safe_summary,
        )
    )
    session.add(
        TelegramTenantConfiguration(
            tenant_id=tenant_id,
            enabled=True,
            protected_commands=["/run", "/status"],
            status_note="Telegram enabled for channel QA.",
            revision_token="telegram-live-rev",
            updated_by_principal_id="tenant-admin-acme",
        )
    )
    session.add(
        TelegramCommandAlias(
            telegram_command_alias_id=alias_id,
            tenant_id=tenant_id,
            alias_text="Morning briefing",
            alias_normalized="morning briefing",
            published_workflow_version_id=workflow_version_id,
            description="Configured workflow",
            protected=True,
            enabled=True,
            revision_token="alias-live-rev",
            created_by_principal_id="tenant-admin-acme",
            updated_by_principal_id="tenant-admin-acme",
        )
    )
    session.add(
        TelegramLinkedIdentitySummary(
            tenant_id=tenant_id,
            platform_identity_id="tenant-user-acme",
            telegram_user_fingerprint="user-fingerprint-live",
            telegram_chat_fingerprint="chat-fingerprint-live",
            telegram_user_display="tg-***-1842",
            telegram_chat_display="chat-***-9081",
            status="linked",
            command_ready=True,
            trace_id="trace-channel-live-identity",
        )
    )
    session.add(
        TelegramDiagnosticEvent(
            tenant_id=tenant_id,
            principal_id="tenant-admin-acme",
            category="webhook_validation",
            status="ready",
            summary="Webhook configuration is ready for local command validation.",
            trace_id="trace-channel-live-webhook",
            redacted_metadata={"external_call_performed": False},
            created_at=now - timedelta(minutes=8),
        )
    )
    session.add(
        TelegramLinkTokenAudit(
            tenant_id=tenant_id,
            issued_by_principal_id="tenant-admin-acme",
            token_fingerprint="link-fingerprint-live",
            status="issued",
            expires_at=now + timedelta(minutes=10),
            trace_id="trace-channel-live-token",
        )
    )
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        published_workflow_version_id=workflow_version_id,
        bundle_digest="c" * 64,
    )
    session.add(bundle)
    session.flush()
    session.add(
        WorkflowRunRecord(
            workflow_run_id=run_id,
            tenant_id=tenant_id,
            scope_type="tenant",
            initiating_principal_id="tenant-user-acme",
            run_bundle_id=bundle.run_bundle_id,
            status=RuntimeRunStatus.RUNNING,
            idempotency_key="channel-live-run",
            trace_id="trace-channel-live-run",
            started_at=now - timedelta(minutes=5),
        )
    )
    delivery_id = uuid4()
    session.add(
        NotificationDeliveryAttemptRecord(
            notification_delivery_attempt_id=delivery_id,
            tenant_id=tenant_id,
            notification_subscription_id=uuid4(),
            run_id=run_id,
            channel_type="telegram",
            event_type="run_status",
            payload_fingerprint="payload-fingerprint-live",
            delivery_status="delivered",
            destination_fingerprint="chat-fingerprint-live",
            provider_message_id="provider-msg-live",
            failure_category=None,
            attempt_number=1,
            trace_id="trace-channel-live-delivery",
            created_at=now - timedelta(minutes=3),
            delivered_at=now - timedelta(minutes=2),
        )
    )
    session.add(
        TelegramUpdateReceipt(
            telegram_update_id=55001,
            tenant_id=tenant_id,
            platform_identity_id="tenant-user-acme",
            telegram_chat_fingerprint="chat-fingerprint-live",
            action_type="alias_trigger",
            response_payload={"category": "accepted"},
            run_id=run_id,
            delivery_attempt_id=delivery_id,
            trace_id="trace-channel-live-receipt",
            received_at=now,
        )
    )
    session.commit()
    return {
        "tenant_id": tenant_id,
        "other_tenant_id": other_tenant_id,
        "alias_id": alias_id,
        "run_id": run_id,
        "delivery_attempt_id": delivery_id,
        "profile_id": profile_id,
    }


def _preference_payload() -> BriefingPreferencePayload:
    return BriefingPreferencePayload(
        location_label="Metro area summary",
        timezone="America/New_York",
        news_topics=("Operations",),
        vip_senders=("vip@example.test",),
        workday_start="08:30",
        workday_end="17:30",
        commute_mode="transit",
        calendar_account_ref="none",
        email_account_ref="none",
        output_style="executive",
        scheduled_enabled=True,
        scheduled_time="07:45",
    )


async def _merge_tenants(session: AsyncSession) -> None:
    await session.merge(
        Tenant(
            tenant_id=ACME_TENANT_ID,
            slug="acme",
            display_name="Acme",
            status=TenantStatus.ACTIVE,
        )
    )
    await session.merge(
        Tenant(
            tenant_id=GLOBEX_TENANT_ID,
            slug="globex",
            display_name="Globex",
            status=TenantStatus.ACTIVE,
        )
    )


def _merge_tenants_sync(
    session: Session,
    *,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    session.merge(
        Tenant(
            tenant_id=tenant_id,
            slug="acme",
            display_name="Acme",
            status=TenantStatus.ACTIVE,
        )
    )
    session.merge(
        Tenant(
            tenant_id=other_tenant_id,
            slug="globex",
            display_name="Globex",
            status=TenantStatus.ACTIVE,
        )
    )


async def _create_workflow_version(session: AsyncSession, *, tenant_id: UUID) -> UUID:
    principal = PrincipalIdentity(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject=f"local|qa055-publisher-{uuid4()}",
        display_name="QA055 Publisher",
        email="qa055.publisher@example.test",
        status=PrincipalIdentityStatus.ACTIVE,
    )
    session.add(principal)
    await session.flush()
    lineage = WorkflowLineage(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug=f"qa055-channel-briefing-{uuid4().hex[:8]}",
        display_name="QA055 Channel Briefing",
        description="Persisted workflow version for channel run evidence.",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        status=WorkflowLineageStatus.PUBLISHED,
        created_by_principal_id=principal.principal_identity_id,
    )
    session.add(lineage)
    await session.flush()
    draft = WorkflowDraft(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="tenant",
        tenant_id=tenant_id,
        status=WorkflowDraftStatus.PUBLISHED_SOURCE,
        current_revision_number=1,
        created_by_principal_id=principal.principal_identity_id,
        last_edited_by_principal_id=principal.principal_identity_id,
    )
    session.add(draft)
    await session.flush()
    revision = WorkflowDraftRevision(
        workflow_draft_id=draft.workflow_draft_id,
        revision_number=1,
        authoring_document_json={"name": "QA055 channel briefing"},
        document_sha256="d" * 64,
        change_summary="QA055 live-data seed workflow revision.",
        created_by_principal_id=principal.principal_identity_id,
    )
    session.add(revision)
    await session.flush()
    draft.latest_revision_id = revision.workflow_draft_revision_id
    version = WorkflowVersionBundle(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="tenant",
        tenant_id=tenant_id,
        version_sequence=1,
        display_version="v1",
        status=WorkflowVersionStatus.PUBLISHED,
        published_from_draft_id=draft.workflow_draft_id,
        published_from_revision_id=revision.workflow_draft_revision_id,
        compiled_bundle_digest="d" * 64,
        compiler_version="qa055",
        summary_json={"safe_summary": "QA055 channel briefing workflow"},
        published_by_principal_id=principal.principal_identity_id,
    )
    session.add(version)
    await session.flush()
    lineage.latest_published_version_id = version.workflow_version_bundle_id
    return version.workflow_version_bundle_id


def _create_workflow_version_sync(session: Session, *, tenant_id: UUID) -> UUID:
    principal = PrincipalIdentity(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject=f"local|qa055-publisher-{uuid4()}",
        display_name="QA055 Publisher",
        email="qa055.publisher@example.test",
        status=PrincipalIdentityStatus.ACTIVE,
    )
    session.add(principal)
    session.flush()
    lineage = WorkflowLineage(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug=f"qa055-channel-briefing-{uuid4().hex[:8]}",
        display_name="QA055 Channel Briefing",
        description="Persisted workflow version for channel run evidence.",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        status=WorkflowLineageStatus.PUBLISHED,
        created_by_principal_id=principal.principal_identity_id,
    )
    session.add(lineage)
    session.flush()
    draft = WorkflowDraft(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="tenant",
        tenant_id=tenant_id,
        status=WorkflowDraftStatus.PUBLISHED_SOURCE,
        current_revision_number=1,
        created_by_principal_id=principal.principal_identity_id,
        last_edited_by_principal_id=principal.principal_identity_id,
    )
    session.add(draft)
    session.flush()
    revision = WorkflowDraftRevision(
        workflow_draft_id=draft.workflow_draft_id,
        revision_number=1,
        authoring_document_json={"name": "QA055 channel briefing"},
        document_sha256="d" * 64,
        change_summary="QA055 live-data seed workflow revision.",
        created_by_principal_id=principal.principal_identity_id,
    )
    session.add(revision)
    session.flush()
    draft.latest_revision_id = revision.workflow_draft_revision_id
    version = WorkflowVersionBundle(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="tenant",
        tenant_id=tenant_id,
        version_sequence=1,
        display_version="v1",
        status=WorkflowVersionStatus.PUBLISHED,
        published_from_draft_id=draft.workflow_draft_id,
        published_from_revision_id=revision.workflow_draft_revision_id,
        compiled_bundle_digest="d" * 64,
        compiler_version="qa055",
        summary_json={"safe_summary": "QA055 channel briefing workflow"},
        published_by_principal_id=principal.principal_identity_id,
    )
    session.add(version)
    session.flush()
    lineage.latest_published_version_id = version.workflow_version_bundle_id
    return version.workflow_version_bundle_id
