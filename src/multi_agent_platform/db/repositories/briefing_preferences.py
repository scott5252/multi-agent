from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAction,
    BriefingPreferenceDecision,
    BriefingPreferencePayload,
    BriefingPreferenceStaleRevisionError,
)
from multi_agent_platform.admin.briefing_preferences.redaction import (
    content_digest,
    safe_summary_for_payload,
    sanitize_metadata,
    sanitize_text,
)
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceAuditEvent,
    BriefingPreferenceProfile,
    BriefingPreferenceRevision,
)


class BriefingPreferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_profile(
        self, *, tenant_id: UUID, principal_id: str
    ) -> BriefingPreferenceProfile | None:
        stmt = select(BriefingPreferenceProfile).where(
            BriefingPreferenceProfile.tenant_id == tenant_id,
            BriefingPreferenceProfile.principal_id == principal_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_profiles(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 100
    ) -> list[BriefingPreferenceProfile]:
        stmt = select(BriefingPreferenceProfile)
        if not platform_scope:
            stmt = stmt.where(BriefingPreferenceProfile.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(BriefingPreferenceProfile.tenant_id == tenant_id)
        stmt = stmt.order_by(BriefingPreferenceProfile.updated_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def upsert_profile(
        self,
        *,
        tenant_id: UUID,
        principal_id: str,
        payload: BriefingPreferencePayload,
        expected_revision_token: str | None,
        actor_principal_id: str,
        trace_id: str,
    ) -> tuple[BriefingPreferenceProfile, BriefingPreferenceRevision, bool]:
        profile = await self.get_profile(tenant_id=tenant_id, principal_id=principal_id)
        created = profile is None
        if profile is None:
            profile = BriefingPreferenceProfile(
                briefing_preference_profile_id=uuid4(),
                tenant_id=tenant_id,
                principal_id=principal_id,
                location_label=payload.location_label,
                timezone=payload.timezone,
                news_topics=list(payload.news_topics),
                vip_senders=list(payload.vip_senders),
                workday_start=payload.workday_start,
                workday_end=payload.workday_end,
                commute_mode=str(payload.commute_mode),
                calendar_account_ref=payload.calendar_account_ref,
                email_account_ref=payload.email_account_ref,
                output_style=str(payload.output_style),
                scheduled_enabled=payload.scheduled_enabled,
                scheduled_time=payload.scheduled_time,
                current_revision_id=uuid4(),
                revision_number=0,
                content_digest="pending",
                safe_summary={},
                revision_token=uuid4().hex,
            )
            self.session.add(profile)
        elif (
            expected_revision_token
            and profile.revision_token != expected_revision_token
        ):
            raise BriefingPreferenceStaleRevisionError(
                "stale briefing profile revision"
            )

        storage_payload = payload.to_storage()
        digest = content_digest(storage_payload)
        revision_id = uuid4()
        revision_number = profile.revision_number + 1
        summary = safe_summary_for_payload(
            storage_payload,
            revision_id=revision_id,
            content_hash=digest,
        )

        profile.location_label = payload.location_label
        profile.timezone = payload.timezone
        profile.news_topics = list(payload.news_topics)
        profile.vip_senders = list(payload.vip_senders)
        profile.workday_start = payload.workday_start
        profile.workday_end = payload.workday_end
        profile.commute_mode = str(payload.commute_mode)
        profile.calendar_account_ref = payload.calendar_account_ref
        profile.email_account_ref = payload.email_account_ref
        profile.output_style = str(payload.output_style)
        profile.scheduled_enabled = payload.scheduled_enabled
        profile.scheduled_time = payload.scheduled_time
        profile.current_revision_id = revision_id
        profile.revision_number = revision_number
        profile.content_digest = digest
        profile.safe_summary = summary
        profile.revision_token = uuid4().hex

        revision = BriefingPreferenceRevision(
            briefing_preference_revision_id=revision_id,
            briefing_preference_profile_id=profile.briefing_preference_profile_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            revision_number=revision_number,
            preference_payload=storage_payload,
            safe_summary=summary,
            content_digest=digest,
            created_by_principal_id=actor_principal_id,
            trace_id=trace_id,
        )
        self.session.add(revision)
        await self.session.flush()
        return profile, revision, created

    async def add_audit_event(
        self,
        *,
        tenant_id: UUID | None,
        principal_id: str | None,
        actor_principal_id: str | None,
        action: BriefingPreferenceAction,
        decision: BriefingPreferenceDecision,
        summary: str,
        trace_id: str,
        profile_id: UUID | None = None,
        revision_id: UUID | None = None,
        content_hash: str | None = None,
        redacted_metadata: dict[str, object] | None = None,
    ) -> BriefingPreferenceAuditEvent:
        record = BriefingPreferenceAuditEvent(
            tenant_id=tenant_id,
            principal_id=principal_id,
            actor_principal_id=actor_principal_id,
            action=action.value,
            decision=decision.value,
            summary=sanitize_text(summary, max_length=500)
            or "Briefing preference event recorded.",
            profile_id=profile_id,
            revision_id=revision_id,
            content_digest=content_hash,
            trace_id=trace_id,
            redacted_metadata=sanitize_metadata(redacted_metadata),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_audit_events(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 50
    ) -> list[BriefingPreferenceAuditEvent]:
        stmt = select(BriefingPreferenceAuditEvent)
        if not platform_scope:
            stmt = stmt.where(BriefingPreferenceAuditEvent.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(BriefingPreferenceAuditEvent.tenant_id == tenant_id)
        stmt = stmt.order_by(BriefingPreferenceAuditEvent.created_at.desc()).limit(
            limit
        )
        return list((await self.session.execute(stmt)).scalars().all())
