from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAction,
)
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceAuditEvent,
    BriefingPreferenceProfile,
    BriefingPreferenceRevision,
)
from multi_agent_platform.db.models.channels import NotificationDeliveryAttemptRecord
from multi_agent_platform.db.models.runtime_orchestration import WorkflowRunRecord
from multi_agent_platform.db.models.telegram_config import (
    TelegramCommandAlias,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramTenantConfiguration,
    TelegramUpdateReceipt,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA055_RUN_ID = UUID("55555555-5555-4555-8555-555555555555")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        configs = _count(
            session,
            select(func.count())
            .select_from(TelegramTenantConfiguration)
            .where(
                TelegramTenantConfiguration.tenant_id == ACME_TENANT_ID,
                TelegramTenantConfiguration.enabled.is_(True),
            ),
        )
        aliases = _count(
            session,
            select(func.count())
            .select_from(TelegramCommandAlias)
            .where(
                TelegramCommandAlias.tenant_id == ACME_TENANT_ID,
                TelegramCommandAlias.alias_normalized == "morning briefing",
            ),
        )
        globex_aliases = _count(
            session,
            select(func.count())
            .select_from(TelegramCommandAlias)
            .where(TelegramCommandAlias.tenant_id == GLOBEX_TENANT_ID),
        )
        identities = _count(
            session,
            select(func.count())
            .select_from(TelegramLinkedIdentitySummary)
            .where(TelegramLinkedIdentitySummary.tenant_id == ACME_TENANT_ID),
        )
        token_audits = _count(
            session,
            select(func.count())
            .select_from(TelegramLinkTokenAudit)
            .where(TelegramLinkTokenAudit.tenant_id == ACME_TENANT_ID),
        )
        receipts = _count(
            session,
            select(func.count())
            .select_from(TelegramUpdateReceipt)
            .where(TelegramUpdateReceipt.tenant_id == ACME_TENANT_ID),
        )
        deliveries = _count(
            session,
            select(func.count())
            .select_from(NotificationDeliveryAttemptRecord)
            .where(
                NotificationDeliveryAttemptRecord.tenant_id == ACME_TENANT_ID,
                NotificationDeliveryAttemptRecord.delivery_status == "delivered",
            ),
        )
        runs = _count(
            session,
            select(func.count())
            .select_from(WorkflowRunRecord)
            .where(
                WorkflowRunRecord.tenant_id == ACME_TENANT_ID,
                WorkflowRunRecord.workflow_run_id == QA055_RUN_ID,
            ),
        )
        profile = session.scalar(
            select(BriefingPreferenceProfile).where(
                BriefingPreferenceProfile.tenant_id == ACME_TENANT_ID,
                BriefingPreferenceProfile.principal_id == "tenant-user-acme",
            )
        )
        revisions = _count(
            session,
            select(func.count())
            .select_from(BriefingPreferenceRevision)
            .where(
                BriefingPreferenceRevision.tenant_id == ACME_TENANT_ID,
                BriefingPreferenceRevision.principal_id == "tenant-user-acme",
            ),
        )
        updated_audits = _count(
            session,
            select(func.count())
            .select_from(BriefingPreferenceAuditEvent)
            .where(
                BriefingPreferenceAuditEvent.tenant_id == ACME_TENANT_ID,
                BriefingPreferenceAuditEvent.principal_id == "tenant-user-acme",
                BriefingPreferenceAuditEvent.action
                == BriefingPreferenceAction.PROFILE_UPDATED.value,
            ),
        )
        if configs < 1:
            raise RuntimeError("Expected an enabled Acme Telegram configuration")
        if aliases < 1:
            raise RuntimeError("Expected a persisted Acme Morning briefing alias")
        if globex_aliases:
            raise RuntimeError("Globex should not have QA055 seeded aliases")
        if identities < 1:
            raise RuntimeError("Expected at least one linked Telegram identity summary")
        if token_audits < 1:
            raise RuntimeError("Expected at least one link-token audit")
        if receipts < 1:
            raise RuntimeError("Expected at least one Telegram update receipt")
        if deliveries < 1:
            raise RuntimeError("Expected at least one delivered notification attempt")
        if runs < 1:
            raise RuntimeError("Expected the QA055 workflow run status row")
        if profile is None:
            raise RuntimeError("Expected the tenant-user-acme briefing profile")
        if profile.revision_number < 2 or revisions < 2:
            raise RuntimeError(
                "Expected Playwright to save preferences and create a second revision"
            )
        if updated_audits < 1:
            raise RuntimeError(
                "Expected profile_updated audit evidence after Playwright save"
            )
    print("Verified QA055 channel Telegram briefing live-data persistence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"configs={configs}")
    print(f"aliases={aliases}")
    print(f"identities={identities}")
    print(f"token_audits={token_audits}")
    print(f"receipts={receipts}")
    print(f"deliveries={deliveries}")
    print(f"runs={runs}")
    print(f"briefing_revision_number={profile.revision_number}")
    print(f"briefing_revisions={revisions}")
    print(f"profile_updated_audits={updated_audits}")
    return 0


def _count(session: Session, stmt) -> int:
    return int(session.scalar(stmt) or 0)


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
