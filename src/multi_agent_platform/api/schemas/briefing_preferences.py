from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingCommuteMode,
    BriefingOutputStyle,
)


class BriefingPreferencePayloadRequest(BaseModel):
    tenant_id: UUID | None = None
    location_label: str = Field(min_length=1, max_length=120)
    timezone: str = Field(min_length=1, max_length=120)
    news_topics: tuple[str, ...] = ()
    vip_senders: tuple[str, ...] = ()
    workday_start: str = "09:00"
    workday_end: str = "17:00"
    commute_mode: BriefingCommuteMode = BriefingCommuteMode.NONE
    calendar_account_ref: str = "none"
    email_account_ref: str = "none"
    output_style: BriefingOutputStyle = BriefingOutputStyle.STANDARD
    scheduled_enabled: bool = False
    scheduled_time: str | None = None
    revision_token: str | None = None


class BriefingPreferenceResponse(BaseModel):
    briefing_preference_profile_id: UUID
    tenant_id: UUID
    principal_id: str
    location_label: str
    timezone: str
    news_topics: tuple[str, ...]
    vip_senders: tuple[str, ...]
    workday_start: str
    workday_end: str
    commute_mode: str
    calendar_account_ref: str
    email_account_ref: str
    output_style: str
    scheduled_enabled: bool
    scheduled_time: str | None
    current_revision_id: UUID
    revision_number: int
    content_digest: str
    safe_summary: dict[str, object]
    revision_token: str
    created_at: datetime
    updated_at: datetime


class BriefingPreferenceProfileResponse(BaseModel):
    profile: BriefingPreferenceResponse | None


class BriefingPreferenceSummaryResponse(BaseModel):
    briefing_preference_profile_id: UUID
    tenant_id: UUID
    principal_id: str
    current_revision_id: UUID
    revision_number: int
    content_digest: str
    safe_summary: dict[str, object]
    updated_at: datetime


class BriefingPreferenceSummaryListResponse(BaseModel):
    items: tuple[BriefingPreferenceSummaryResponse, ...]


class BriefingPreferenceExportResponse(BaseModel):
    document: dict[str, object]


class BriefingPreferenceImportRequest(BaseModel):
    tenant_id: UUID | None = None
    document: dict[str, object]
    revision_token: str | None = None


class BriefingPreferenceResolveRequest(BaseModel):
    tenant_id: UUID
    principal_id: str
    source_channel: str = "web_api"
    trace_id: str | None = None


class BriefingPreferenceResolveResponse(BaseModel):
    available: bool
    tenant_id: UUID
    principal_id: str
    source_channel: str
    trace_id: str
    revision_id: UUID | None = None
    content_digest: str | None = None
    preferences: dict[str, object] = Field(default_factory=dict)
    safe_summary: dict[str, object] = Field(default_factory=dict)
    reason: str | None = None
