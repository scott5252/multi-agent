from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from multi_agent_platform.channels.models import (
    ArtifactAvailability,
    ChannelType,
    ErrorCategory,
    PromptAction,
    PromptType,
    ResultAvailability,
    TerminalOutcome,
    TimelineEventType,
    TimelineSeverity,
    UserVisibleRunState,
)


class ChannelErrorDetail(BaseModel):
    category: ErrorCategory
    message: str
    latest_status: RunStatusResponse | None = None


class ChannelErrorResponse(BaseModel):
    error: ChannelErrorDetail
    trace_id: str


class RunInvocationRequest(BaseModel):
    workflow_id: str
    inputs: dict[str, object] = Field(default_factory=dict)
    channel: ChannelType = ChannelType.WEB_API
    client_session_id: str | None = None
    callback_url: str | None = None


class RunInvocationResponse(BaseModel):
    run_id: UUID
    state: UserVisibleRunState
    status_url: str
    timeline_url: str | None = None
    events_url: str | None = None
    trace_id: str


class WaitingPromptResponse(BaseModel):
    prompt_id: UUID
    prompt_type: PromptType
    prompt_version: int
    summary: str
    context: dict[str, object] = Field(default_factory=dict)
    allowed_actions: tuple[PromptAction, ...]
    deadline_at: datetime | None = None


class RunStatusResponse(BaseModel):
    run_id: UUID
    state: UserVisibleRunState
    progress_summary: str
    latest_timeline_cursor: str
    permitted_actions: tuple[str, ...]
    trace_id: str
    waiting_prompt: WaitingPromptResponse | None = None
    terminal_outcome: TerminalOutcome = TerminalOutcome.NONE
    result_availability: ResultAvailability = ResultAvailability.UNAVAILABLE
    artifact_availability: ArtifactAvailability = ArtifactAvailability.NONE
    subscribed: bool = False


class TimelineEventResponse(BaseModel):
    event_id: UUID
    sequence: int
    event_type: TimelineEventType
    state: UserVisibleRunState
    summary: str
    severity: TimelineSeverity = TimelineSeverity.INFO
    occurred_at: datetime
    trace_id: str


class TimelineResponse(BaseModel):
    items: list[TimelineEventResponse]
    next_cursor: str | None = None


class RunResultResponse(BaseModel):
    run_id: UUID
    availability: ResultAvailability
    state: UserVisibleRunState
    trace_id: str
    summary: str | None = None
    structured_result: dict[str, object] | None = None


class PromptDecisionRequest(BaseModel):
    action: PromptAction
    prompt_version: int = Field(ge=1)
    decision_payload: dict[str, object] = Field(default_factory=dict)


class PromptDecisionResponse(BaseModel):
    accepted: bool
    run_status: RunStatusResponse
    trace_id: str
    decision_id: UUID | None = None
    rejection_category: ErrorCategory | None = None


class CancelRunRequest(BaseModel):
    reason: str = Field(min_length=1)


class ArtifactMetadataResponse(BaseModel):
    artifact_id: UUID
    name: str
    user_facing_type: str
    status: str
    download_url_available: bool
    size_bytes: int | None = Field(default=None, ge=0)


class ArtifactListResponse(BaseModel):
    run_id: UUID
    items: list[ArtifactMetadataResponse]


class ArtifactDownloadUrlResponse(BaseModel):
    artifact_id: UUID
    download_url: str
    expires_at: datetime
    trace_id: str


class NotificationSubscriptionRequest(BaseModel):
    channel: ChannelType
    event_types: tuple[str, ...] = ("terminal",)

    @field_validator("event_types")
    @classmethod
    def validate_event_types(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values or any(value != "terminal" for value in values):
            raise ValueError("only terminal notifications are supported")
        return values


class NotificationSubscriptionResponse(BaseModel):
    subscription_id: UUID
    status: str


class CallbackRegistrationRequest(BaseModel):
    callback_url: str
    event_types: tuple[str, ...]

    @field_validator("event_types")
    @classmethod
    def validate_callback_event_types(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        allowed = {"terminal", "waiting_prompt", "artifact_ready"}
        if not values or any(value not in allowed for value in values):
            raise ValueError("unsupported callback event type")
        return values


class CallbackRegistrationResponse(BaseModel):
    callback_registration_id: UUID
    status: str


class TelegramLinkTokenResponse(BaseModel):
    link_token: str
    expires_at: datetime
    channel: ChannelType = ChannelType.TELEGRAM


RunStatusResponse.model_rebuild()
