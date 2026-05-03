from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from multi_agent_platform.channels.artifacts import (
    create_artifact_grant,
    default_artifact_for_run,
)
from multi_agent_platform.channels.callbacks import validate_callback_url
from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.idempotency import (
    IdempotencyStatus,
    InMemoryIdempotencyStore,
    request_fingerprint,
)
from multi_agent_platform.channels.models import (
    ArtifactAvailability,
    ArtifactDownloadGrant,
    ArtifactMetadata,
    CallbackRegistration,
    ChannelActor,
    ChannelRun,
    ChannelType,
    ErrorCategory,
    NotificationSubscription,
    PromptAction,
    PromptDecisionResult,
    PromptType,
    ResultAvailability,
    RunInvocationResult,
    RunResult,
    RunStatusView,
    TerminalOutcome,
    TimelineEvent,
    TimelineEventType,
    UserVisibleRunState,
    WaitingPrompt,
    channel_now,
)
from multi_agent_platform.channels.notifications import subscription_key
from multi_agent_platform.channels.state_mapping import permitted_actions_for_state
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


@dataclass(slots=True)
class TelegramLinkToken:
    token: str
    tenant_id: UUID | None
    platform_identity_id: str
    expires_at: datetime
    consumed_at: datetime | None = None


@dataclass(slots=True, frozen=True)
class TelegramIdentity:
    tenant_id: UUID | None
    platform_identity_id: str
    telegram_user_id: int
    telegram_chat_id: int


@dataclass(slots=True, frozen=True)
class TelegramIdentitySnapshot:
    tenant_id: UUID | None
    platform_identity_id: str
    telegram_user_id: int
    telegram_chat_id: int


class ChannelService:
    def __init__(
        self,
        *,
        settings: Settings,
        runtime_service: RuntimeOrchestrationService | None = None,
    ) -> None:
        self.settings = settings
        self.runtime_service = runtime_service or RuntimeOrchestrationService()
        self.idempotency = InMemoryIdempotencyStore()
        self._runs: dict[UUID, ChannelRun] = {}
        self._link_tokens: dict[str, TelegramLinkToken] = {}
        self._telegram_links: dict[tuple[int, int], TelegramIdentity] = {}
        self._telegram_updates: dict[int, dict[str, object]] = {}
        self._rate_windows: dict[tuple[str | None, str, str], list[datetime]] = {}

    async def start_run(
        self,
        *,
        actor: ChannelActor,
        workflow_id: str,
        inputs: dict[str, object],
        idempotency_key: str,
    ) -> RunInvocationResult:
        self._require_rate_budget(actor, "invoke")
        if not workflow_id or not inputs:
            raise ChannelError(ErrorCategory.MISSING_INPUT, trace_id=actor.trace_id)
        fingerprint = request_fingerprint(
            {
                "workflow_id": workflow_id,
                "inputs": inputs,
                "channel": actor.channel_type.value,
            }
        )
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="invoke",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]

        workflow_uuid = _workflow_uuid(workflow_id)
        runtime_run = await self.runtime_service.start_run(
            tenant_id=actor.tenant_id,
            scope_type="tenant" if actor.tenant_id is not None else "platform",
            principal_id=actor.platform_identity_id,
            published_workflow_version_id=workflow_uuid,
            input_payload=inputs,
            idempotency_key=idempotency_key,
            trace_id=actor.trace_id,
        )
        run = ChannelRun(
            run_id=runtime_run.workflow_run_id,
            tenant_id=actor.tenant_id,
            requester_identity_id=actor.platform_identity_id,
            channel_type=actor.channel_type,
            trace_id=runtime_run.trace_id,
        )
        run.add_event(
            TimelineEventType.RUN_QUEUED, "Run accepted through channel facade."
        )
        self._apply_simulation_inputs(run, inputs)
        run.subscriptions[
            subscription_key(actor.platform_identity_id, actor.channel_session_id)
        ] = uuid4()
        self._runs[run.run_id] = run
        response = RunInvocationResult(
            run_id=run.run_id,
            state=run.state,
            status_url=f"/runs/{run.run_id}/status",
            timeline_url=f"/runs/{run.run_id}/timeline",
            events_url=f"/runs/{run.run_id}/events",
            trace_id=run.trace_id,
        )
        return self.idempotency.store(
            actor=actor,
            action_type="invoke",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=response,
        )  # type: ignore[return-value]

    def list_runs(self, actor: ChannelActor) -> list[RunStatusView]:
        return [
            self._status_view(run, actor)
            for run in sorted(
                self._runs.values(), key=lambda item: item.updated_at, reverse=True
            )
            if self._can_access(run, actor)
        ]

    def get_status(self, *, actor: ChannelActor, run_id: UUID) -> RunStatusView:
        self._require_rate_budget(actor, "status")
        return self._status_view(self._get_run(actor, run_id), actor)

    def list_timeline(
        self, *, actor: ChannelActor, run_id: UUID, cursor: str | None, limit: int
    ) -> tuple[list[TimelineEvent], str | None]:
        run = self._get_run(actor, run_id)
        start = int(cursor or "0")
        items = [event for event in run.timeline if event.sequence > start][:limit]
        next_cursor = str(items[-1].sequence) if len(items) == limit and items else None
        return items, next_cursor

    def get_result(self, *, actor: ChannelActor, run_id: UUID) -> RunResult:
        run = self._get_run(actor, run_id)
        if run.result is not None:
            return run.result
        availability = {
            UserVisibleRunState.FAILED: ResultAvailability.FAILED,
            UserVisibleRunState.CANCELED: ResultAvailability.CANCELED,
        }.get(run.state, ResultAvailability.UNAVAILABLE)
        return RunResult(
            run_id=run.run_id,
            availability=availability,
            state=run.state,
            summary=run.progress_summary
            if availability is not ResultAvailability.UNAVAILABLE
            else None,
            trace_id=actor.trace_id,
        )

    def decide_prompt(
        self,
        *,
        actor: ChannelActor,
        run_id: UUID,
        prompt_id: UUID,
        action: PromptAction,
        prompt_version: int,
        decision_payload: dict[str, object],
        idempotency_key: str,
    ) -> PromptDecisionResult:
        run = self._get_run(actor, run_id)
        fingerprint = request_fingerprint(
            {
                "run_id": run_id,
                "prompt_id": prompt_id,
                "action": action.value,
                "prompt_version": prompt_version,
                "payload": decision_payload,
            }
        )
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="decision",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]
        prompt = run.waiting_prompt
        if (
            prompt is None
            or prompt.prompt_id != prompt_id
            or prompt.prompt_version != prompt_version
            or action not in prompt.allowed_actions
        ):
            result = PromptDecisionResult(
                accepted=False,
                run_status=self._status_view(run, actor),
                trace_id=actor.trace_id,
                rejection_category=ErrorCategory.INVALID_LIFECYCLE_ACTION,
            )
            return self.idempotency.store(
                actor=actor,
                action_type="decision",
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
                response=result,
            )  # type: ignore[return-value]
        prompt.answered_at = channel_now()
        run.waiting_prompt = None
        if action is PromptAction.CANCEL:
            self._terminal(
                run, UserVisibleRunState.CANCELED, "Run canceled from waiting prompt."
            )
        elif action is PromptAction.REJECT:
            self._terminal(run, UserVisibleRunState.FAILED, "Waiting prompt rejected.")
        else:
            run.state = UserVisibleRunState.RUNNING
            run.progress_summary = "Waiting prompt accepted; run resumed."
            run.add_event(
                TimelineEventType.WAITING_PROMPT_ANSWERED, run.progress_summary
            )
        result = PromptDecisionResult(
            accepted=True,
            decision_id=uuid4(),
            run_status=self._status_view(run, actor),
            trace_id=actor.trace_id,
        )
        return self.idempotency.store(
            actor=actor,
            action_type="decision",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=result,
        )  # type: ignore[return-value]

    async def cancel_run(
        self, *, actor: ChannelActor, run_id: UUID, reason: str, idempotency_key: str
    ) -> RunStatusView:
        run = self._get_run(actor, run_id)
        fingerprint = request_fingerprint({"run_id": run_id, "reason": reason})
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="cancel",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]
        if run.terminal_outcome is not TerminalOutcome.NONE:
            raise ChannelError(
                ErrorCategory.INVALID_LIFECYCLE_ACTION, trace_id=actor.trace_id
            )
        try:
            await self.runtime_service.cancel_run(
                workflow_run_id=run.run_id,
                tenant_id=run.tenant_id,
                reason=reason,
            )
        except (LookupError, ValueError):
            pass
        self._terminal(run, UserVisibleRunState.CANCELED, reason)
        response = self._status_view(run, actor)
        return self.idempotency.store(
            actor=actor,
            action_type="cancel",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=response,
        )  # type: ignore[return-value]

    def subscribe(
        self,
        *,
        actor: ChannelActor,
        run_id: UUID,
        channel: ChannelType,
        event_types: tuple[str, ...],
        idempotency_key: str,
    ) -> NotificationSubscription:
        run = self._get_run(actor, run_id)
        fingerprint = request_fingerprint(
            {"run_id": run_id, "channel": channel.value, "event_types": event_types}
        )
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="subscribe",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]
        subscription = NotificationSubscription(subscription_id=uuid4())
        run.subscriptions[
            subscription_key(actor.platform_identity_id, actor.channel_session_id)
        ] = subscription.subscription_id
        return self.idempotency.store(
            actor=actor,
            action_type="subscribe",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=subscription,
        )  # type: ignore[return-value]

    def register_callback(
        self,
        *,
        actor: ChannelActor,
        run_id: UUID,
        callback_url: str,
        event_types: tuple[str, ...],
        idempotency_key: str,
    ) -> CallbackRegistration:
        run = self._get_run(actor, run_id)
        validate_callback_url(
            callback_url,
            allow_local_http=self.settings.app_env.value in {"local", "test", "ci"},
        )
        fingerprint = request_fingerprint(
            {"run_id": run_id, "callback_url": callback_url, "event_types": event_types}
        )
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="callback_register",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]
        registration = CallbackRegistration(callback_registration_id=uuid4())
        run.callbacks[registration.callback_registration_id] = callback_url
        run.add_event(
            TimelineEventType.CALLBACK_ATTEMPTED, "Callback registration stored."
        )
        return self.idempotency.store(
            actor=actor,
            action_type="callback_register",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=registration,
        )  # type: ignore[return-value]

    def list_artifacts(
        self, *, actor: ChannelActor, run_id: UUID
    ) -> list[ArtifactMetadata]:
        return list(self._get_run(actor, run_id).artifacts)

    def create_artifact_download_url(
        self,
        *,
        actor: ChannelActor,
        run_id: UUID,
        artifact_id: UUID,
        idempotency_key: str,
    ) -> ArtifactDownloadGrant:
        run = self._get_run(actor, run_id)
        fingerprint = request_fingerprint(
            {"run_id": run_id, "artifact_id": artifact_id}
        )
        replay = self.idempotency.get_or_reserve(
            actor=actor,
            action_type="artifact_download",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None and replay.status is IdempotencyStatus.ACCEPTED:
            return replay.response  # type: ignore[return-value]
        grant = create_artifact_grant(
            run=run,
            actor=actor,
            artifact_id=artifact_id,
            ttl_seconds=self.settings.channel_artifact_url_ttl_seconds,
        )
        return self.idempotency.store(
            actor=actor,
            action_type="artifact_download",
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
            response=grant,
        )  # type: ignore[return-value]

    def create_telegram_link_token(self, actor: ChannelActor) -> TelegramLinkToken:
        token = uuid4().hex
        record = TelegramLinkToken(
            token=token,
            tenant_id=actor.tenant_id,
            platform_identity_id=actor.platform_identity_id,
            expires_at=datetime.now(UTC)
            + timedelta(seconds=self.settings.telegram_link_token_ttl_seconds),
        )
        self._link_tokens[token] = record
        return record

    def consume_telegram_link_token(
        self, *, token: str, telegram_user_id: int, telegram_chat_id: int
    ) -> TelegramIdentity:
        record = self._link_tokens.get(token)
        if (
            record is None
            or record.consumed_at is not None
            or record.expires_at <= datetime.now(UTC)
        ):
            raise ChannelError(
                ErrorCategory.UNAUTHORIZED, "Telegram link token is invalid or expired."
            )
        record.consumed_at = datetime.now(UTC)
        identity = TelegramIdentity(
            tenant_id=record.tenant_id,
            platform_identity_id=record.platform_identity_id,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
        )
        self._telegram_links[(telegram_user_id, telegram_chat_id)] = identity
        return identity

    def telegram_actor(
        self, *, telegram_user_id: int, telegram_chat_id: int, trace_id: str
    ) -> ChannelActor:
        identity = self._telegram_links.get((telegram_user_id, telegram_chat_id))
        if identity is None:
            raise ChannelError(ErrorCategory.UNAUTHORIZED, trace_id=trace_id)
        return ChannelActor(
            tenant_id=identity.tenant_id,
            platform_identity_id=identity.platform_identity_id,
            channel_type=ChannelType.TELEGRAM,
            trace_id=trace_id,
        )

    def revoke_telegram_link_token_by_hash(self, token_hash: str) -> bool:
        for token in tuple(self._link_tokens):
            if _fingerprint_value(token) == token_hash:
                self._link_tokens.pop(token, None)
                return True
        return False

    def telegram_identity_snapshots(
        self, *, tenant_id: UUID | None
    ) -> tuple[TelegramIdentitySnapshot, ...]:
        return tuple(
            TelegramIdentitySnapshot(
                tenant_id=identity.tenant_id,
                platform_identity_id=identity.platform_identity_id,
                telegram_user_id=identity.telegram_user_id,
                telegram_chat_id=identity.telegram_chat_id,
            )
            for identity in self._telegram_links.values()
            if identity.tenant_id == tenant_id
        )

    def revoke_telegram_identity_by_fingerprints(
        self, *, user_fingerprint: str, chat_fingerprint: str
    ) -> bool:
        for key, identity in tuple(self._telegram_links.items()):
            if (
                _fingerprint_value(identity.telegram_user_id) == user_fingerprint
                and _fingerprint_value(identity.telegram_chat_id) == chat_fingerprint
            ):
                self._telegram_links.pop(key, None)
                return True
        return False

    def get_telegram_update(self, update_id: int) -> dict[str, object] | None:
        return self._telegram_updates.get(update_id)

    def store_telegram_update(
        self, update_id: int, response: dict[str, object]
    ) -> dict[str, object]:
        self._telegram_updates[update_id] = response
        return response

    def force_waiting_prompt(self, run_id: UUID) -> WaitingPrompt:
        run = self._runs[run_id]
        run.state = UserVisibleRunState.WAITING_FOR_INPUT
        prompt = WaitingPrompt(
            prompt_id=uuid4(),
            prompt_type=PromptType.APPROVAL,
            prompt_version=1,
            summary="Review required before the run can continue.",
            allowed_actions=(
                PromptAction.APPROVE,
                PromptAction.REJECT,
                PromptAction.RESUME,
                PromptAction.CANCEL,
            ),
        )
        run.waiting_prompt = prompt
        run.progress_summary = prompt.summary
        run.add_event(TimelineEventType.WAITING_PROMPT_CREATED, prompt.summary)
        return prompt

    def force_terminal_result(self, run_id: UUID) -> RunResult:
        run = self._runs[run_id]
        self._terminal(
            run, UserVisibleRunState.COMPLETED, "Run completed successfully."
        )
        result = RunResult(
            run_id=run.run_id,
            availability=ResultAvailability.AVAILABLE,
            state=run.state,
            summary="Run completed successfully.",
            structured_result={"message": "completed", "run_id": str(run.run_id)},
            trace_id=run.trace_id,
        )
        run.result = result
        if not run.artifacts:
            run.artifacts.append(default_artifact_for_run(run.run_id))
            run.add_event(
                TimelineEventType.ARTIFACT_READY, "Artifact metadata is available."
            )
        return result

    def _status_view(self, run: ChannelRun, actor: ChannelActor) -> RunStatusView:
        key_prefix = f"{actor.platform_identity_id}:"
        subscribed = any(key.startswith(key_prefix) for key in run.subscriptions)
        artifact_availability = (
            ArtifactAvailability.AVAILABLE
            if run.artifacts
            else ArtifactAvailability.NONE
        )
        result_availability = (
            run.result.availability
            if run.result is not None
            else {
                UserVisibleRunState.FAILED: ResultAvailability.FAILED,
                UserVisibleRunState.CANCELED: ResultAvailability.CANCELED,
            }.get(run.state, ResultAvailability.UNAVAILABLE)
        )
        return RunStatusView(
            run_id=run.run_id,
            state=run.state,
            progress_summary=run.progress_summary,
            latest_timeline_cursor=str(
                run.timeline[-1].sequence if run.timeline else 0
            ),
            waiting_prompt=run.waiting_prompt,
            terminal_outcome=run.terminal_outcome,
            result_availability=result_availability,
            artifact_availability=artifact_availability,
            subscribed=subscribed,
            permitted_actions=permitted_actions_for_state(run.state),
            trace_id=actor.trace_id or run.trace_id,
        )

    def _get_run(self, actor: ChannelActor, run_id: UUID) -> ChannelRun:
        run = self._runs.get(run_id)
        if run is None or not self._can_access(run, actor):
            raise ChannelError(ErrorCategory.INVALID_RUN_ID, trace_id=actor.trace_id)
        return run

    def _can_access(self, run: ChannelRun, actor: ChannelActor) -> bool:
        return run.tenant_id == actor.tenant_id

    def _terminal(
        self, run: ChannelRun, state: UserVisibleRunState, summary: str
    ) -> None:
        run.state = state
        run.progress_summary = summary
        run.terminal_outcome = {
            UserVisibleRunState.COMPLETED: TerminalOutcome.COMPLETED,
            UserVisibleRunState.FAILED: TerminalOutcome.FAILED,
            UserVisibleRunState.CANCELED: TerminalOutcome.CANCELED,
        }[state]
        event_type = {
            UserVisibleRunState.COMPLETED: TimelineEventType.RUN_COMPLETED,
            UserVisibleRunState.FAILED: TimelineEventType.RUN_FAILED,
            UserVisibleRunState.CANCELED: TimelineEventType.RUN_CANCELED,
        }[state]
        run.add_event(event_type, summary)

    def _apply_simulation_inputs(
        self, run: ChannelRun, inputs: dict[str, object]
    ) -> None:
        channel_state = inputs.get("_channel_state")
        if channel_state == "waiting":
            self._runs[run.run_id] = run
            self.force_waiting_prompt(run.run_id)
        elif channel_state == "completed":
            self._runs[run.run_id] = run
            self.force_terminal_result(run.run_id)

    def _require_rate_budget(self, actor: ChannelActor, action_type: str) -> None:
        limit = self.settings.channel_rate_limit_per_minute
        now = datetime.now(UTC)
        key = (
            str(actor.tenant_id) if actor.tenant_id is not None else None,
            actor.platform_identity_id,
            action_type,
        )
        window = [
            timestamp
            for timestamp in self._rate_windows.get(key, [])
            if timestamp > now - timedelta(minutes=1)
        ]
        if len(window) >= limit:
            raise ChannelError(ErrorCategory.RATE_LIMITED, trace_id=actor.trace_id)
        window.append(now)
        self._rate_windows[key] = window


def _workflow_uuid(workflow_id: str) -> UUID:
    try:
        return UUID(workflow_id)
    except ValueError:
        return uuid5(NAMESPACE_URL, workflow_id)


def _fingerprint_value(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()
