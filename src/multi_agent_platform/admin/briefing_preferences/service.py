from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAccessScope,
    BriefingPreferenceAction,
    BriefingPreferenceDecision,
    BriefingPreferencePayload,
    BriefingPreferencePermissionError,
    BriefingPreferenceScopeType,
)
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceAuditEvent,
    BriefingPreferenceProfile,
    BriefingPreferenceRevision,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.observability.tracing import generate_trace_id


@dataclass(frozen=True, slots=True)
class BriefingPreferenceSaveResult:
    profile: BriefingPreferenceProfile
    revision: BriefingPreferenceRevision
    created: bool


@dataclass(frozen=True, slots=True)
class BriefingPreferenceExport:
    document: dict[str, object]
    profile: BriefingPreferenceProfile


@dataclass(frozen=True, slots=True)
class BriefingPreferenceRuntimeContext:
    available: bool
    tenant_id: UUID
    principal_id: str
    source_channel: str
    trace_id: str
    revision_id: UUID | None = None
    content_digest: str | None = None
    preferences: dict[str, object] | None = None
    safe_summary: dict[str, object] | None = None
    reason: str | None = None

    def as_run_input(self) -> dict[str, object]:
        return {
            "available": self.available,
            "tenant_id": str(self.tenant_id),
            "principal_id": self.principal_id,
            "source_channel": self.source_channel,
            "trace_id": self.trace_id,
            "revision_id": str(self.revision_id) if self.revision_id else None,
            "content_digest": self.content_digest,
            "preferences": self.preferences or {},
            "safe_summary": self.safe_summary or {},
            "reason": self.reason,
        }


class BriefingPreferenceService:
    def __init__(self, repository: BriefingPreferenceRepository) -> None:
        self.repository = repository

    async def get_own_profile(
        self, access_scope: BriefingPreferenceAccessScope
    ) -> BriefingPreferenceProfile | None:
        tenant_id = access_scope.require_tenant()
        profile = await self.repository.get_profile(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
        )
        await self.repository.add_audit_event(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.PROFILE_READ,
            decision=BriefingPreferenceDecision.ALLOW
            if profile is not None
            else BriefingPreferenceDecision.MISSING,
            summary="Briefing preference profile read.",
            trace_id=self._trace_id(access_scope),
            profile_id=None
            if profile is None
            else profile.briefing_preference_profile_id,
            revision_id=None if profile is None else profile.current_revision_id,
            content_hash=None if profile is None else profile.content_digest,
        )
        return profile

    async def save_own_profile(
        self,
        *,
        access_scope: BriefingPreferenceAccessScope,
        payload: BriefingPreferencePayload,
        revision_token: str | None,
    ) -> BriefingPreferenceSaveResult:
        tenant_id = access_scope.require_tenant()
        profile, revision, created = await self.repository.upsert_profile(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            payload=payload,
            expected_revision_token=revision_token,
            actor_principal_id=access_scope.principal_id,
            trace_id=self._trace_id(access_scope),
        )
        await self.repository.add_audit_event(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.PROFILE_CREATED
            if created
            else BriefingPreferenceAction.PROFILE_UPDATED,
            decision=BriefingPreferenceDecision.ALLOW,
            summary="Briefing preference profile saved.",
            trace_id=self._trace_id(access_scope),
            profile_id=profile.briefing_preference_profile_id,
            revision_id=revision.briefing_preference_revision_id,
            content_hash=revision.content_digest,
            redacted_metadata=profile.safe_summary,
        )
        return BriefingPreferenceSaveResult(
            profile=profile,
            revision=revision,
            created=created,
        )

    async def list_summaries(
        self, access_scope: BriefingPreferenceAccessScope
    ) -> tuple[BriefingPreferenceProfile, ...]:
        profiles = tuple(
            await self.repository.list_profiles(
                tenant_id=access_scope.tenant_id,
                platform_scope=access_scope.scope_type
                is BriefingPreferenceScopeType.PLATFORM,
            )
        )
        await self.repository.add_audit_event(
            tenant_id=access_scope.tenant_id,
            principal_id=None,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.PROFILE_SUMMARY_READ,
            decision=BriefingPreferenceDecision.ALLOW,
            summary="Briefing preference safe summaries inspected.",
            trace_id=self._trace_id(access_scope),
            redacted_metadata={"summary_count": len(profiles)},
        )
        return profiles

    async def export_own_profile(
        self, access_scope: BriefingPreferenceAccessScope
    ) -> BriefingPreferenceExport:
        profile = await self.get_own_profile(access_scope)
        if profile is None:
            raise LookupError("briefing preference profile not found")
        document: dict[str, object] = {
            "schema_version": "1.0",
            "tenant_id": str(profile.tenant_id),
            "principal_id": profile.principal_id,
            "preferences": profile_payload(profile),
            "revision_id": str(profile.current_revision_id),
            "content_digest": profile.content_digest,
        }
        await self.repository.add_audit_event(
            tenant_id=profile.tenant_id,
            principal_id=profile.principal_id,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.PROFILE_EXPORTED,
            decision=BriefingPreferenceDecision.ALLOW,
            summary="Briefing preference profile exported.",
            trace_id=self._trace_id(access_scope),
            profile_id=profile.briefing_preference_profile_id,
            revision_id=profile.current_revision_id,
            content_hash=profile.content_digest,
        )
        return BriefingPreferenceExport(document=document, profile=profile)

    async def import_own_profile(
        self,
        *,
        access_scope: BriefingPreferenceAccessScope,
        document: dict[str, object],
        revision_token: str | None,
    ) -> BriefingPreferenceSaveResult:
        tenant_id = access_scope.require_tenant()
        if (
            str(document.get("tenant_id")) != str(tenant_id)
            or document.get("principal_id") != access_scope.principal_id
        ):
            await self.record_denial(
                access_scope=access_scope,
                reason="import ownership mismatch",
                metadata={"document_schema": document.get("schema_version")},
            )
            raise BriefingPreferencePermissionError("import ownership mismatch")
        result = await self.save_own_profile(
            access_scope=access_scope,
            payload=BriefingPreferencePayload.model_validate(
                document.get("preferences")
            ),
            revision_token=revision_token,
        )
        await self.repository.add_audit_event(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.PROFILE_IMPORTED,
            decision=BriefingPreferenceDecision.ALLOW,
            summary="Briefing preference profile imported.",
            trace_id=self._trace_id(access_scope),
            profile_id=result.profile.briefing_preference_profile_id,
            revision_id=result.revision.briefing_preference_revision_id,
            content_hash=result.revision.content_digest,
        )
        return result

    async def resolve_runtime_context(
        self,
        *,
        tenant_id: UUID,
        principal_id: str,
        source_channel: str,
        trace_id: str | None = None,
        workflow_run_id: UUID | None = None,
    ) -> BriefingPreferenceRuntimeContext:
        resolved_trace_id = trace_id or generate_trace_id()
        profile = await self.repository.get_profile(
            tenant_id=tenant_id,
            principal_id=principal_id,
        )
        if profile is None:
            await self.repository.add_audit_event(
                tenant_id=tenant_id,
                principal_id=principal_id,
                actor_principal_id=principal_id,
                action=BriefingPreferenceAction.RUNTIME_MISSING,
                decision=BriefingPreferenceDecision.MISSING,
                summary="Briefing preference runtime profile missing.",
                trace_id=resolved_trace_id,
                redacted_metadata={
                    "source_channel": source_channel,
                    "workflow_run_id": str(workflow_run_id)
                    if workflow_run_id is not None
                    else None,
                },
            )
            return BriefingPreferenceRuntimeContext(
                available=False,
                tenant_id=tenant_id,
                principal_id=principal_id,
                source_channel=source_channel,
                trace_id=resolved_trace_id,
                reason="missing_profile",
            )
        await self.repository.add_audit_event(
            tenant_id=tenant_id,
            principal_id=principal_id,
            actor_principal_id=principal_id,
            action=BriefingPreferenceAction.RUNTIME_RESOLVED,
            decision=BriefingPreferenceDecision.ALLOW,
            summary="Briefing preference runtime profile resolved.",
            trace_id=resolved_trace_id,
            profile_id=profile.briefing_preference_profile_id,
            revision_id=profile.current_revision_id,
            content_hash=profile.content_digest,
            redacted_metadata={
                "source_channel": source_channel,
                "workflow_run_id": str(workflow_run_id)
                if workflow_run_id is not None
                else None,
                "safe_summary": profile.safe_summary,
            },
        )
        return BriefingPreferenceRuntimeContext(
            available=True,
            tenant_id=tenant_id,
            principal_id=principal_id,
            source_channel=source_channel,
            trace_id=resolved_trace_id,
            revision_id=profile.current_revision_id,
            content_digest=profile.content_digest,
            preferences=profile_payload(profile),
            safe_summary=profile.safe_summary,
        )

    async def record_denial(
        self,
        *,
        access_scope: BriefingPreferenceAccessScope,
        reason: str,
        metadata: dict[str, object] | None = None,
    ) -> BriefingPreferenceAuditEvent:
        return await self.repository.add_audit_event(
            tenant_id=access_scope.tenant_id,
            principal_id=access_scope.principal_id,
            actor_principal_id=access_scope.principal_id,
            action=BriefingPreferenceAction.ACCESS_DENIED,
            decision=BriefingPreferenceDecision.DENY,
            summary="Briefing preference access denied.",
            trace_id=self._trace_id(access_scope),
            redacted_metadata={"reason": reason, **(metadata or {})},
        )

    def _trace_id(self, access_scope: BriefingPreferenceAccessScope) -> str:
        return access_scope.trace_id or generate_trace_id()


def profile_payload(profile: BriefingPreferenceProfile) -> dict[str, object]:
    return {
        "location_label": profile.location_label,
        "timezone": profile.timezone,
        "news_topics": list(profile.news_topics or []),
        "vip_senders": list(profile.vip_senders or []),
        "workday_start": profile.workday_start,
        "workday_end": profile.workday_end,
        "commute_mode": profile.commute_mode,
        "calendar_account_ref": profile.calendar_account_ref,
        "email_account_ref": profile.email_account_ref,
        "output_style": profile.output_style,
        "scheduled_enabled": profile.scheduled_enabled,
        "scheduled_time": profile.scheduled_time,
    }
