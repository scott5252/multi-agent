from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


def channel_now() -> datetime:
    return datetime.now(UTC)


class ChannelType(StrEnum):
    WEB_UI = "web_ui"
    WEB_API = "web_api"
    TELEGRAM = "telegram"


class UserVisibleRunState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting-for-input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TerminalOutcome(StrEnum):
    NONE = "none"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ResultAvailability(StrEnum):
    AVAILABLE = "available"
    FAILED = "failed"
    CANCELED = "canceled"
    UNAVAILABLE = "unavailable"
    EXPIRED = "expired"
    UNAUTHORIZED = "unauthorized"


class ArtifactAvailability(StrEnum):
    NONE = "none"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    EXPIRED = "expired"
    UNAUTHORIZED = "unauthorized"


class ErrorCategory(StrEnum):
    UNAUTHORIZED = "unauthorized"
    MISSING_INPUT = "missing_input"
    INVALID_RUN_ID = "invalid_run_id"
    UNAVAILABLE_CHANNEL_DELIVERY = "unavailable_channel_delivery"
    INVALID_LIFECYCLE_ACTION = "invalid_lifecycle_action"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    RATE_LIMITED = "rate_limited"
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    CALLBACK_DELIVERY_FAILED = "callback_delivery_failed"
    PLATFORM_FAILURE = "platform_failure"


class PromptAction(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    RESUME = "resume"
    CANCEL = "cancel"


class PromptType(StrEnum):
    APPROVAL = "approval"
    RESUME_INPUT = "resume_input"


class TimelineEventType(StrEnum):
    RUN_QUEUED = "run_queued"
    RUN_STARTED = "run_started"
    PROGRESS = "progress"
    WAITING_PROMPT_CREATED = "waiting_prompt_created"
    WAITING_PROMPT_ANSWERED = "waiting_prompt_answered"
    ARTIFACT_READY = "artifact_ready"
    RESULT_READY = "result_ready"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_CANCELED = "run_canceled"
    NOTIFICATION_ATTEMPTED = "notification_attempted"
    CALLBACK_ATTEMPTED = "callback_attempted"


class TimelineSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class ChannelActor:
    tenant_id: UUID | None
    platform_identity_id: str
    channel_type: ChannelType
    trace_id: str
    channel_session_id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class NormalizedChannelRequest:
    tenant_id: UUID | None
    platform_identity_id: str
    channel_type: ChannelType
    action_type: str
    input_payload: dict[str, object]
    trace_id: str
    run_id: UUID | None = None
    prompt_id: UUID | None = None
    idempotency_key: str | None = None
    source_request_id: str | None = None
    received_at: datetime = field(default_factory=channel_now)
    source_metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class WaitingPrompt:
    prompt_id: UUID
    prompt_type: PromptType
    prompt_version: int
    summary: str
    allowed_actions: tuple[PromptAction, ...]
    context: dict[str, object] = field(default_factory=dict)
    deadline_at: datetime | None = None
    answered_at: datetime | None = None


@dataclass(slots=True)
class TimelineEvent:
    sequence: int
    event_type: TimelineEventType
    state: UserVisibleRunState
    summary: str
    trace_id: str
    severity: TimelineSeverity = TimelineSeverity.INFO
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=channel_now)


@dataclass(slots=True)
class ArtifactMetadata:
    artifact_id: UUID
    name: str
    user_facing_type: str
    status: str = "available"
    download_url_available: bool = True
    size_bytes: int | None = None


@dataclass(slots=True)
class ArtifactDownloadGrant:
    artifact_id: UUID
    download_url: str
    expires_at: datetime
    trace_id: str


@dataclass(slots=True)
class RunResult:
    run_id: UUID
    availability: ResultAvailability
    state: UserVisibleRunState
    trace_id: str
    summary: str | None = None
    structured_result: dict[str, object] | None = None


@dataclass(slots=True)
class RunStatusView:
    run_id: UUID
    state: UserVisibleRunState
    progress_summary: str
    latest_timeline_cursor: str
    permitted_actions: tuple[str, ...]
    trace_id: str
    waiting_prompt: WaitingPrompt | None = None
    terminal_outcome: TerminalOutcome = TerminalOutcome.NONE
    result_availability: ResultAvailability = ResultAvailability.UNAVAILABLE
    artifact_availability: ArtifactAvailability = ArtifactAvailability.NONE
    subscribed: bool = False


@dataclass(slots=True)
class ChannelRun:
    run_id: UUID
    tenant_id: UUID | None
    requester_identity_id: str
    channel_type: ChannelType
    trace_id: str
    state: UserVisibleRunState = UserVisibleRunState.QUEUED
    progress_summary: str = "Run accepted and queued."
    timeline: list[TimelineEvent] = field(default_factory=list)
    waiting_prompt: WaitingPrompt | None = None
    terminal_outcome: TerminalOutcome = TerminalOutcome.NONE
    result: RunResult | None = None
    artifacts: list[ArtifactMetadata] = field(default_factory=list)
    subscriptions: dict[str, UUID] = field(default_factory=dict)
    callbacks: dict[UUID, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=channel_now)
    updated_at: datetime = field(default_factory=channel_now)

    def add_event(
        self,
        event_type: TimelineEventType,
        summary: str,
        *,
        severity: TimelineSeverity = TimelineSeverity.INFO,
    ) -> TimelineEvent:
        event = TimelineEvent(
            sequence=len(self.timeline) + 1,
            event_type=event_type,
            state=self.state,
            summary=summary,
            severity=severity,
            trace_id=self.trace_id,
        )
        self.timeline.append(event)
        self.updated_at = event.occurred_at
        return event


@dataclass(slots=True, frozen=True)
class RunInvocationResult:
    run_id: UUID
    state: UserVisibleRunState
    status_url: str
    timeline_url: str
    events_url: str
    trace_id: str


@dataclass(slots=True, frozen=True)
class PromptDecisionResult:
    accepted: bool
    run_status: RunStatusView
    trace_id: str
    decision_id: UUID | None = None
    rejection_category: ErrorCategory | None = None


@dataclass(slots=True, frozen=True)
class NotificationSubscription:
    subscription_id: UUID
    status: str = "active"


@dataclass(slots=True, frozen=True)
class CallbackRegistration:
    callback_registration_id: UUID
    status: str = "active"
