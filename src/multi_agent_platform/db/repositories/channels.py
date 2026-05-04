from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.channels import (
    ApiCallbackDeliveryAttemptRecord,
    ApiCallbackRegistrationRecord,
    ArtifactAccessGrantRecord,
    ChannelIdempotencyRecord,
    ChannelSessionRecord,
    ChannelTimelineEventRecord,
    InteractionAuditRecord,
    NormalizedChannelRequestRecord,
    NotificationDeliveryAttemptRecord,
    RunNotificationSubscriptionRecord,
    TelegramIdentityLinkRecord,
)


class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_session(self, record: ChannelSessionRecord) -> ChannelSessionRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_session(
        self, channel_session_id: UUID
    ) -> ChannelSessionRecord | None:
        return await self.session.get(ChannelSessionRecord, channel_session_id)

    async def add_telegram_link(
        self, record: TelegramIdentityLinkRecord
    ) -> TelegramIdentityLinkRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def upsert_telegram_identity_link(
        self,
        *,
        tenant_id: UUID,
        platform_identity_id: str,
        telegram_user_id: int,
        telegram_chat_id: int,
        link_token_hash: str,
        now: datetime,
        expires_at: datetime | None = None,
    ) -> TelegramIdentityLinkRecord:
        stmt = select(TelegramIdentityLinkRecord).where(
            TelegramIdentityLinkRecord.tenant_id == tenant_id,
            TelegramIdentityLinkRecord.telegram_user_id == str(telegram_user_id),
            TelegramIdentityLinkRecord.telegram_chat_id == str(telegram_chat_id),
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            record = TelegramIdentityLinkRecord(
                tenant_id=tenant_id,
                platform_identity_id=platform_identity_id,
                telegram_user_id=str(telegram_user_id),
                telegram_chat_id=str(telegram_chat_id),
                link_token_hash=link_token_hash,
                status="linked",
                created_at=now,
                expires_at=expires_at or now + timedelta(days=3650),
                linked_at=now,
            )
            self.session.add(record)
        else:
            record.platform_identity_id = platform_identity_id
            record.link_token_hash = link_token_hash
            record.status = "linked"
            record.expires_at = expires_at or record.expires_at
            record.linked_at = now
            record.revoked_at = None
        await self.session.flush()
        return record

    async def get_active_telegram_identity(
        self, *, telegram_user_id: int, telegram_chat_id: int
    ) -> TelegramIdentityLinkRecord | None:
        stmt = select(TelegramIdentityLinkRecord).where(
            TelegramIdentityLinkRecord.telegram_user_id == str(telegram_user_id),
            TelegramIdentityLinkRecord.telegram_chat_id == str(telegram_chat_id),
            TelegramIdentityLinkRecord.status == "linked",
            TelegramIdentityLinkRecord.revoked_at.is_(None),
        )
        records = list((await self.session.execute(stmt)).scalars().all())
        if len(records) != 1:
            return None
        return records[0]

    async def get_pending_telegram_link(
        self, *, token_hash: str, now: datetime
    ) -> TelegramIdentityLinkRecord | None:
        stmt = select(TelegramIdentityLinkRecord).where(
            TelegramIdentityLinkRecord.link_token_hash == token_hash,
            TelegramIdentityLinkRecord.status == "pending",
            TelegramIdentityLinkRecord.expires_at > now,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_normalized_request(
        self, record: NormalizedChannelRequestRecord
    ) -> NormalizedChannelRequestRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_idempotency_record(
        self,
        *,
        tenant_id: UUID | None,
        platform_identity_id: str,
        channel_type: str,
        action_type: str,
        idempotency_key: str,
    ) -> ChannelIdempotencyRecord | None:
        stmt = select(ChannelIdempotencyRecord).where(
            ChannelIdempotencyRecord.tenant_id == tenant_id,
            ChannelIdempotencyRecord.platform_identity_id == platform_identity_id,
            ChannelIdempotencyRecord.channel_type == channel_type,
            ChannelIdempotencyRecord.action_type == action_type,
            ChannelIdempotencyRecord.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_idempotency_record(
        self, record: ChannelIdempotencyRecord
    ) -> ChannelIdempotencyRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_timeline_event(
        self, record: ChannelTimelineEventRecord
    ) -> ChannelTimelineEventRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_timeline(
        self, *, tenant_id: UUID | None, run_id: UUID, after_sequence: int = 0
    ) -> list[ChannelTimelineEventRecord]:
        stmt = (
            select(ChannelTimelineEventRecord)
            .where(
                ChannelTimelineEventRecord.tenant_id == tenant_id,
                ChannelTimelineEventRecord.run_id == run_id,
                ChannelTimelineEventRecord.sequence > after_sequence,
            )
            .order_by(ChannelTimelineEventRecord.sequence.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_subscription(
        self, record: RunNotificationSubscriptionRecord
    ) -> RunNotificationSubscriptionRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_delivery_attempt(
        self, record: NotificationDeliveryAttemptRecord
    ) -> NotificationDeliveryAttemptRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_delivery_attempts(
        self, *, tenant_id: UUID | None, run_id: UUID
    ) -> list[NotificationDeliveryAttemptRecord]:
        stmt = (
            select(NotificationDeliveryAttemptRecord)
            .where(
                NotificationDeliveryAttemptRecord.tenant_id == tenant_id,
                NotificationDeliveryAttemptRecord.run_id == run_id,
            )
            .order_by(NotificationDeliveryAttemptRecord.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_callback_registration(
        self, record: ApiCallbackRegistrationRecord
    ) -> ApiCallbackRegistrationRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_callback_attempt(
        self, record: ApiCallbackDeliveryAttemptRecord
    ) -> ApiCallbackDeliveryAttemptRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_artifact_grant(
        self, record: ArtifactAccessGrantRecord
    ) -> ArtifactAccessGrantRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def add_audit(self, record: InteractionAuditRecord) -> InteractionAuditRecord:
        self.session.add(record)
        await self.session.flush()
        return record
