from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelActor, ErrorCategory


class IdempotencyStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    ACCEPTED = "accepted"
    FAILED = "failed"


@dataclass(slots=True)
class StoredIdempotencyOutcome:
    fingerprint: str
    response: object
    status: IdempotencyStatus
    expires_at: datetime


def request_fingerprint(payload: object) -> str:
    encoded = json.dumps(payload, default=str, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class InMemoryIdempotencyStore:
    def __init__(self, ttl_seconds: int = 86_400) -> None:
        self.ttl_seconds = ttl_seconds
        self._records: dict[
            tuple[str | None, str, str, str, str], StoredIdempotencyOutcome
        ] = {}

    def get_or_reserve(
        self,
        *,
        actor: ChannelActor,
        action_type: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> StoredIdempotencyOutcome | None:
        self._purge_expired()
        key = self._key(actor, action_type, idempotency_key)
        existing = self._records.get(key)
        if existing is not None:
            if existing.fingerprint != fingerprint:
                raise ChannelError(
                    ErrorCategory.IDEMPOTENCY_CONFLICT, trace_id=actor.trace_id
                )
            return existing
        self._records[key] = StoredIdempotencyOutcome(
            fingerprint=fingerprint,
            response=None,
            status=IdempotencyStatus.IN_PROGRESS,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.ttl_seconds),
        )
        return None

    def store(
        self,
        *,
        actor: ChannelActor,
        action_type: str,
        idempotency_key: str,
        fingerprint: str,
        response: object,
    ) -> object:
        key = self._key(actor, action_type, idempotency_key)
        self._records[key] = StoredIdempotencyOutcome(
            fingerprint=fingerprint,
            response=response,
            status=IdempotencyStatus.ACCEPTED,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.ttl_seconds),
        )
        return response

    def _key(
        self, actor: ChannelActor, action_type: str, idempotency_key: str
    ) -> tuple[str | None, str, str, str, str]:
        return (
            str(actor.tenant_id) if actor.tenant_id is not None else None,
            actor.platform_identity_id,
            actor.channel_type.value,
            action_type,
            idempotency_key,
        )

    def _purge_expired(self) -> None:
        now = datetime.now(UTC)
        expired = [
            key for key, record in self._records.items() if record.expires_at <= now
        ]
        for key in expired:
            del self._records[key]
