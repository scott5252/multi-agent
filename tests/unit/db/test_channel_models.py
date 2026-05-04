from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models.channels import (
    ChannelIdempotencyRecord,
    ChannelSessionRecord,
    ChannelTimelineEventRecord,
    NotificationDeliveryAttemptRecord,
    TelegramIdentityLinkRecord,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository


def test_channel_models_are_registered_in_metadata() -> None:
    assert "channel_sessions" in Base.metadata.tables
    assert "telegram_identity_links" in Base.metadata.tables
    assert "normalized_channel_requests" in Base.metadata.tables
    assert "interaction_audit_records" in Base.metadata.tables


@pytest.mark.asyncio
async def test_channel_repository_stores_core_records(session: AsyncSession) -> None:
    repository = ChannelRepository(session)
    now = datetime.now(UTC)
    tenant_id = uuid4()
    channel_session = await repository.add_session(
        ChannelSessionRecord(
            tenant_id=tenant_id,
            platform_identity_id="user-1",
            channel_type="web_api",
            channel_subject="client-1",
            auth_state="authenticated",
            expires_at=now + timedelta(hours=1),
            metadata_json={},
        )
    )
    await repository.add_telegram_link(
        TelegramIdentityLinkRecord(
            tenant_id=tenant_id,
            platform_identity_id="user-1",
            telegram_user_id="10",
            telegram_chat_id="20",
            link_token_hash="hash",
            status="pending",
            created_at=now,
            expires_at=now + timedelta(minutes=10),
        )
    )
    await repository.add_idempotency_record(
        ChannelIdempotencyRecord(
            tenant_id=tenant_id,
            platform_identity_id="user-1",
            channel_type="web_api",
            action_type="invoke",
            idempotency_key="idem-1",
            request_fingerprint="fp",
            status="accepted",
            stored_response={"ok": True},
            run_id=None,
            created_at=now,
            expires_at=now + timedelta(days=1),
        )
    )
    run_id = uuid4()
    await repository.add_timeline_event(
        ChannelTimelineEventRecord(
            tenant_id=tenant_id,
            run_id=run_id,
            sequence=1,
            event_type="run_queued",
            visible_state="queued",
            summary="Queued",
            severity="info",
            occurred_at=now,
            trace_id="trace-1",
            source_channel="web_api",
            metadata_json={},
        )
    )

    assert await repository.get_session(channel_session.channel_session_id)
    assert await repository.get_pending_telegram_link(token_hash="hash", now=now)
    assert await repository.get_idempotency_record(
        tenant_id=tenant_id,
        platform_identity_id="user-1",
        channel_type="web_api",
        action_type="invoke",
        idempotency_key="idem-1",
    )
    assert len(await repository.list_timeline(tenant_id=tenant_id, run_id=run_id)) == 1


@pytest.mark.asyncio
async def test_channel_repository_persists_telegram_identity_and_delivery_attempt(
    session: AsyncSession,
) -> None:
    repository = ChannelRepository(session)
    now = datetime.now(UTC)
    tenant_id = uuid4()
    run_id = uuid4()
    identity = await repository.upsert_telegram_identity_link(
        tenant_id=tenant_id,
        platform_identity_id="tenant-admin",
        telegram_user_id=987654321,
        telegram_chat_id=123456789,
        link_token_hash="hash",
        now=now,
    )
    attempt = await repository.add_delivery_attempt(
        NotificationDeliveryAttemptRecord(
            tenant_id=tenant_id,
            notification_subscription_id=uuid4(),
            run_id=run_id,
            channel_type="telegram",
            event_type="terminal",
            payload_fingerprint="payload-hash",
            delivery_status="delivered",
            destination_fingerprint="chat-hash",
            provider_message_id="mock-1",
            failure_category=None,
            attempt_number=1,
            next_retry_at=None,
            trace_id="trace-delivery",
            created_at=now,
            delivered_at=now,
        )
    )

    assert identity.status == "linked"
    assert (
        await repository.get_active_telegram_identity(
            telegram_user_id=987654321,
            telegram_chat_id=123456789,
        )
        == identity
    )
    assert await repository.list_delivery_attempts(
        tenant_id=tenant_id,
        run_id=run_id,
    ) == [attempt]
