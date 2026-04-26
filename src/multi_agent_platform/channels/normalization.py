from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelType,
    ErrorCategory,
    NormalizedChannelRequest,
)
from multi_agent_platform.observability.logging import redact_mapping
from multi_agent_platform.observability.tracing import generate_trace_id
from multi_agent_platform.tenancy.context import ScopeContext

DUPLICATE_PRONE_ACTIONS = {
    "invoke",
    "decision",
    "cancel",
    "artifact_download",
    "subscribe",
    "callback_register",
    "notification_ack",
}


def actor_from_scope(
    scope: ScopeContext, *, channel_type: ChannelType, trace_id: str | None = None
) -> ChannelActor:
    return ChannelActor(
        tenant_id=scope.tenant_id,
        platform_identity_id=scope.principal_id,
        channel_type=channel_type,
        trace_id=trace_id or scope.trace_id or generate_trace_id(),
    )


def normalize_channel_request(
    *,
    actor: ChannelActor,
    action_type: str,
    input_payload: Mapping[str, object],
    idempotency_key: str | None = None,
    run_id: UUID | None = None,
    prompt_id: UUID | None = None,
    source_request_id: str | None = None,
    source_metadata: Mapping[str, object] | None = None,
) -> NormalizedChannelRequest:
    if action_type in DUPLICATE_PRONE_ACTIONS and not idempotency_key:
        raise ChannelError(
            ErrorCategory.MISSING_INPUT,
            "Idempotency key is required.",
            trace_id=actor.trace_id,
        )
    return NormalizedChannelRequest(
        tenant_id=actor.tenant_id,
        platform_identity_id=actor.platform_identity_id,
        channel_type=actor.channel_type,
        action_type=action_type,
        input_payload=dict(input_payload),
        run_id=run_id,
        prompt_id=prompt_id,
        idempotency_key=idempotency_key,
        trace_id=actor.trace_id,
        source_request_id=source_request_id,
        source_metadata=redact_mapping(source_metadata or {}),
    )
