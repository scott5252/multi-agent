from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
ACCOUNT_REF_PREFIXES = (
    "delegated:",
    "secret-ref:",
    "account:",
    "local:",
    "test:",
    "fake:",
    "none",
)
RAW_CREDENTIAL_MARKERS = (
    "bearer ",
    "api_key=",
    "password=",
    "oauth_token",
    "refresh_token",
    "access_token",
    "-----begin",
)


class BriefingPreferenceScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class BriefingCommuteMode(StrEnum):
    NONE = "none"
    DRIVING = "driving"
    TRANSIT = "transit"
    WALKING = "walking"
    CYCLING = "cycling"
    REMOTE = "remote"


class BriefingOutputStyle(StrEnum):
    CONCISE = "concise"
    STANDARD = "standard"
    DETAILED = "detailed"
    EXECUTIVE = "executive"


class BriefingPreferenceAction(StrEnum):
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    PROFILE_READ = "profile_read"
    PROFILE_SUMMARY_READ = "profile_summary_read"
    PROFILE_EXPORTED = "profile_exported"
    PROFILE_IMPORTED = "profile_imported"
    RUNTIME_RESOLVED = "runtime_resolved"
    RUNTIME_MISSING = "runtime_missing"
    ACCESS_DENIED = "access_denied"
    VALIDATION_DENIED = "validation_denied"


class BriefingPreferenceDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    VALIDATION_ERROR = "validation_error"
    MISSING = "missing"


class BriefingPreferenceStaleRevisionError(ValueError):
    """Raised when an update uses an outdated profile revision token."""


class BriefingPreferencePermissionError(PermissionError):
    """Raised when a profile operation crosses tenant or principal boundaries."""


@dataclass(frozen=True, slots=True)
class BriefingPreferenceAccessScope:
    scope_type: BriefingPreferenceScopeType
    principal_id: str
    tenant_id: UUID | None = None
    platform_admin: bool = False
    trace_id: str | None = None

    def require_tenant(self) -> UUID:
        if self.tenant_id is None:
            raise BriefingPreferencePermissionError(
                "tenant briefing preference scope required"
            )
        return self.tenant_id


class BriefingPreferencePayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    location_label: str = Field(min_length=1, max_length=120)
    timezone: str = Field(min_length=1, max_length=120)
    news_topics: tuple[str, ...] = Field(default_factory=tuple, max_length=10)
    vip_senders: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    workday_start: str = "09:00"
    workday_end: str = "17:00"
    commute_mode: BriefingCommuteMode = BriefingCommuteMode.NONE
    calendar_account_ref: str = "none"
    email_account_ref: str = "none"
    output_style: BriefingOutputStyle = BriefingOutputStyle.STANDARD
    scheduled_enabled: bool = False
    scheduled_time: str | None = None

    @field_validator("location_label", "timezone")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        stripped = " ".join(value.strip().split())
        if not stripped:
            raise ValueError("value is required")
        return stripped

    @field_validator("timezone")
    @classmethod
    def _valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone must be a valid IANA timezone") from exc
        return value

    @field_validator("news_topics", "vip_senders", mode="before")
    @classmethod
    def _normalize_list(cls, value: object) -> tuple[str, ...]:
        if value is None or value == "":
            return ()
        items = value if isinstance(value, (list, tuple)) else str(value).split(",")
        normalized: list[str] = []
        for item in items:
            text = " ".join(str(item).strip().split())
            if text and text not in normalized:
                normalized.append(text)
        return tuple(normalized)

    @field_validator("workday_start", "workday_end", "scheduled_time")
    @classmethod
    def _valid_time(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        stripped = str(value).strip()
        if not TIME_RE.match(stripped):
            raise ValueError("time must use HH:MM 24-hour format")
        return stripped

    @field_validator("calendar_account_ref", "email_account_ref")
    @classmethod
    def _safe_account_reference(cls, value: str) -> str:
        stripped = value.strip()
        lowered = stripped.casefold()
        if not stripped:
            return "none"
        if any(marker in lowered for marker in RAW_CREDENTIAL_MARKERS):
            raise ValueError("account reference must not contain raw credentials")
        if not any(lowered.startswith(prefix) for prefix in ACCOUNT_REF_PREFIXES):
            raise ValueError("account reference must use a safe reference prefix")
        return stripped

    @model_validator(mode="after")
    def _validate_schedule(self) -> BriefingPreferencePayload:
        if self.workday_start is None or self.workday_end is None:
            raise ValueError("workday start and end are required")
        if _minutes(self.workday_start) >= _minutes(self.workday_end):
            raise ValueError("workday start must be earlier than workday end")
        if self.scheduled_enabled and self.scheduled_time is None:
            raise ValueError("scheduled time is required when scheduling is enabled")
        if not self.scheduled_enabled:
            self.scheduled_time = None
        return self

    def to_storage(self) -> dict[str, object]:
        data = self.model_dump(mode="json")
        data["news_topics"] = list(self.news_topics)
        data["vip_senders"] = list(self.vip_senders)
        return data


def _minutes(value: str) -> int:
    hour, minute = value.split(":", maxsplit=1)
    return int(hour) * 60 + int(minute)
