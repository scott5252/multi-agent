from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import create_engine, select
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

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA055_RUN_ID = UUID("55555555-5555-4555-8555-555555555555")
QA055_DELIVERY_ID = UUID("55555555-5555-4555-8555-555555555556")
QA055_UPDATE_ID = 55055


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime(2026, 5, 7, 19, tzinfo=UTC)
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        publisher = _upsert_principal(
            session,
            external_subject="local|qa055-publisher",
            display_name="QA055 Publisher",
            email="qa055.publisher@example.test",
        )
        workflow_version_id = _upsert_workflow_version(
            session,
            tenant_id=ACME_TENANT_ID,
            publisher=publisher,
        )
        profile_id = _upsert_briefing_profile(session, now=now)
        alias_id = _upsert_telegram_records(
            session,
            workflow_version_id=workflow_version_id,
            now=now,
        )
        _upsert_run_and_delivery(
            session,
            workflow_version_id=workflow_version_id,
            now=now,
        )
        session.commit()
    print("Seeded QA055 channel Telegram briefing live records")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_version_id={workflow_version_id}")
    print(f"profile_id={profile_id}")
    print(f"alias_id={alias_id}")
    print(f"run_id={QA055_RUN_ID}")
    print(f"delivery_attempt_id={QA055_DELIVERY_ID}")
    return 0


def _upsert_tenant(
    session: Session, tenant_id: UUID, slug: str, display_name: str
) -> None:
    record = session.get(Tenant, tenant_id)
    if record is None:
        record = Tenant(tenant_id=tenant_id)
        session.add(record)
    record.slug = slug
    record.display_name = display_name
    record.status = TenantStatus.ACTIVE


def _upsert_principal(
    session: Session,
    *,
    external_subject: str,
    display_name: str,
    email: str,
) -> PrincipalIdentity:
    record = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == external_subject
        )
    )
    if record is None:
        record = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject=external_subject,
        )
        session.add(record)
    record.display_name = display_name
    record.email = email
    record.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return record


def _upsert_workflow_version(
    session: Session,
    *,
    tenant_id: UUID,
    publisher: PrincipalIdentity,
) -> UUID:
    existing = session.scalar(
        select(WorkflowVersionBundle)
        .join(
            WorkflowLineage,
            WorkflowLineage.workflow_lineage_id
            == WorkflowVersionBundle.workflow_lineage_id,
        )
        .where(
            WorkflowLineage.tenant_id == tenant_id,
            WorkflowLineage.slug == "qa055-channel-briefing",
            WorkflowVersionBundle.version_sequence == 1,
        )
    )
    if existing is not None:
        return existing.workflow_version_bundle_id

    lineage = WorkflowLineage(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug="qa055-channel-briefing",
        display_name="QA055 Channel Briefing",
        description="Persisted workflow version for QA055 channel run evidence.",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        status=WorkflowLineageStatus.PUBLISHED,
        created_by_principal_id=publisher.principal_identity_id,
    )
    session.add(lineage)
    session.flush()
    draft = WorkflowDraft(
        workflow_lineage_id=lineage.workflow_lineage_id,
        scope_type="tenant",
        tenant_id=tenant_id,
        status=WorkflowDraftStatus.PUBLISHED_SOURCE,
        current_revision_number=1,
        created_by_principal_id=publisher.principal_identity_id,
        last_edited_by_principal_id=publisher.principal_identity_id,
    )
    session.add(draft)
    session.flush()
    revision = WorkflowDraftRevision(
        workflow_draft_id=draft.workflow_draft_id,
        revision_number=1,
        authoring_document_json={"name": "QA055 channel briefing"},
        document_sha256="5" * 64,
        change_summary="QA055 live-data seed workflow revision.",
        created_by_principal_id=publisher.principal_identity_id,
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
        compiled_bundle_digest="5" * 64,
        compiler_version="qa055",
        summary_json={"safe_summary": "QA055 channel briefing workflow"},
        published_by_principal_id=publisher.principal_identity_id,
    )
    session.add(version)
    session.flush()
    lineage.latest_published_version_id = version.workflow_version_bundle_id
    return version.workflow_version_bundle_id


def _upsert_briefing_profile(session: Session, *, now: datetime) -> UUID:
    profile = session.scalar(
        select(BriefingPreferenceProfile).where(
            BriefingPreferenceProfile.tenant_id == ACME_TENANT_ID,
            BriefingPreferenceProfile.principal_id == "tenant-user-acme",
        )
    )
    if profile is not None:
        return profile.briefing_preference_profile_id

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
            tenant_id=ACME_TENANT_ID,
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
            revision_token="qa055-briefing-live-rev",
        )
    )
    session.add(
        BriefingPreferenceRevision(
            briefing_preference_revision_id=revision_id,
            briefing_preference_profile_id=profile_id,
            tenant_id=ACME_TENANT_ID,
            principal_id="tenant-user-acme",
            revision_number=1,
            preference_payload=payload,
            safe_summary=safe_summary,
            content_digest=digest,
            created_by_principal_id="tenant-user-acme",
            trace_id="trace-qa055-preference-seed",
            created_at=now - timedelta(minutes=12),
        )
    )
    session.add(
        BriefingPreferenceAuditEvent(
            tenant_id=ACME_TENANT_ID,
            principal_id="tenant-user-acme",
            actor_principal_id="tenant-user-acme",
            action=BriefingPreferenceAction.PROFILE_CREATED.value,
            decision=BriefingPreferenceDecision.ALLOW.value,
            summary="Briefing preference profile saved.",
            profile_id=profile_id,
            revision_id=revision_id,
            content_digest=digest,
            trace_id="trace-qa055-preference-seed",
            redacted_metadata=safe_summary,
            created_at=now - timedelta(minutes=11),
        )
    )
    return profile_id


def _upsert_telegram_records(
    session: Session,
    *,
    workflow_version_id: UUID,
    now: datetime,
) -> UUID:
    config = session.scalar(
        select(TelegramTenantConfiguration).where(
            TelegramTenantConfiguration.tenant_id == ACME_TENANT_ID
        )
    )
    if config is None:
        config = TelegramTenantConfiguration(
            tenant_id=ACME_TENANT_ID,
            updated_by_principal_id="tenant-admin-acme",
        )
        session.add(config)
    config.enabled = True
    config.protected_commands = ["/run", "/status"]
    config.status_note = "Telegram enabled for qa055 channel validation."
    config.revision_token = "qa055-telegram-live-rev"
    config.updated_by_principal_id = "tenant-admin-acme"

    alias = session.scalar(
        select(TelegramCommandAlias).where(
            TelegramCommandAlias.tenant_id == ACME_TENANT_ID,
            TelegramCommandAlias.alias_normalized == "morning briefing",
        )
    )
    if alias is None:
        alias = TelegramCommandAlias(
            telegram_command_alias_id=uuid4(),
            tenant_id=ACME_TENANT_ID,
            alias_text="Morning briefing",
            alias_normalized="morning briefing",
            created_by_principal_id="tenant-admin-acme",
            updated_by_principal_id="tenant-admin-acme",
        )
        session.add(alias)
    alias.published_workflow_version_id = workflow_version_id
    alias.description = "Configured workflow"
    alias.protected = True
    alias.enabled = True
    alias.revision_token = "qa055-alias-live-rev"
    alias.updated_by_principal_id = "tenant-admin-acme"

    _upsert_identity_summary(session)
    _upsert_token_audit(session, now=now)
    session.add(
        TelegramDiagnosticEvent(
            tenant_id=ACME_TENANT_ID,
            principal_id="tenant-admin-acme",
            category="webhook_validation",
            status="ready",
            summary="Webhook configuration is ready for local command validation.",
            trace_id="trace-qa055-webhook",
            redacted_metadata={"external_call_performed": False},
            created_at=now - timedelta(minutes=8),
        )
    )
    session.flush()
    return alias.telegram_command_alias_id


def _upsert_identity_summary(session: Session) -> None:
    existing = session.scalar(
        select(TelegramLinkedIdentitySummary).where(
            TelegramLinkedIdentitySummary.tenant_id == ACME_TENANT_ID,
            TelegramLinkedIdentitySummary.telegram_user_fingerprint
            == "qa055-user-fingerprint",
            TelegramLinkedIdentitySummary.telegram_chat_fingerprint
            == "qa055-chat-fingerprint",
        )
    )
    if existing is not None:
        return
    session.add(
        TelegramLinkedIdentitySummary(
            tenant_id=ACME_TENANT_ID,
            platform_identity_id="tenant-user-acme",
            telegram_user_fingerprint="qa055-user-fingerprint",
            telegram_chat_fingerprint="qa055-chat-fingerprint",
            telegram_user_display="tg-***-1055",
            telegram_chat_display="chat-***-4055",
            status="linked",
            command_ready=True,
            trace_id="trace-qa055-identity",
        )
    )


def _upsert_token_audit(session: Session, *, now: datetime) -> None:
    existing = session.scalar(
        select(TelegramLinkTokenAudit).where(
            TelegramLinkTokenAudit.token_fingerprint == "qa055-link-token-fingerprint"
        )
    )
    if existing is not None:
        return
    session.add(
        TelegramLinkTokenAudit(
            tenant_id=ACME_TENANT_ID,
            issued_by_principal_id="tenant-admin-acme",
            token_fingerprint="qa055-link-token-fingerprint",
            status="issued",
            expires_at=now + timedelta(minutes=10),
            trace_id="trace-qa055-token",
        )
    )


def _upsert_run_and_delivery(
    session: Session,
    *,
    workflow_version_id: UUID,
    now: datetime,
) -> None:
    bundle = session.scalar(
        select(RuntimeExecutionBundleRecord).where(
            RuntimeExecutionBundleRecord.workflow_run_id == QA055_RUN_ID
        )
    )
    if bundle is None:
        bundle = RuntimeExecutionBundleRecord(
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA055_RUN_ID,
            published_workflow_version_id=workflow_version_id,
            bundle_digest="6" * 64,
        )
        session.add(bundle)
        session.flush()
    run = session.get(WorkflowRunRecord, QA055_RUN_ID)
    if run is None:
        run = WorkflowRunRecord(
            workflow_run_id=QA055_RUN_ID,
            tenant_id=ACME_TENANT_ID,
            scope_type="tenant",
            initiating_principal_id="tenant-user-acme",
            run_bundle_id=bundle.run_bundle_id,
            idempotency_key="qa055-channel-live-run",
            trace_id="trace-qa055-run",
            started_at=now - timedelta(minutes=5),
        )
        session.add(run)
    run.status = RuntimeRunStatus.RUNNING

    delivery = session.get(NotificationDeliveryAttemptRecord, QA055_DELIVERY_ID)
    if delivery is None:
        delivery = NotificationDeliveryAttemptRecord(
            notification_delivery_attempt_id=QA055_DELIVERY_ID,
            tenant_id=ACME_TENANT_ID,
            notification_subscription_id=uuid4(),
            run_id=QA055_RUN_ID,
            channel_type="telegram",
            event_type="run_status",
            payload_fingerprint="qa055-payload-fingerprint",
            delivery_status="delivered",
            destination_fingerprint="qa055-chat-fingerprint",
            provider_message_id="provider-msg-qa055",
            failure_category=None,
            attempt_number=1,
            trace_id="trace-qa055-delivery",
            created_at=now - timedelta(minutes=3),
            delivered_at=now - timedelta(minutes=2),
        )
        session.add(delivery)

    receipt = session.scalar(
        select(TelegramUpdateReceipt).where(
            TelegramUpdateReceipt.telegram_update_id == QA055_UPDATE_ID
        )
    )
    if receipt is None:
        receipt = TelegramUpdateReceipt(
            telegram_update_id=QA055_UPDATE_ID,
            tenant_id=ACME_TENANT_ID,
            platform_identity_id="tenant-user-acme",
            telegram_chat_fingerprint="qa055-chat-fingerprint",
            action_type="alias_trigger",
            response_payload={"category": "accepted"},
            run_id=QA055_RUN_ID,
            delivery_attempt_id=QA055_DELIVERY_ID,
            trace_id="trace-qa055-receipt",
            received_at=now,
        )
        session.add(receipt)


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


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
