from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SecretValue(BaseModel):
    reference: str
    value: str


class SecretProvider(ABC):
    provider_name: str

    @abstractmethod
    async def resolve(self, reference: str) -> SecretValue:
        raise NotImplementedError


def secret_access_audit_metadata(
    *,
    requester_type: str,
    requester_ref: str,
    secret_reference_id: str,
    policy_outcome: str,
    access_outcome: str,
    reason_code: str | None = None,
) -> dict[str, object]:
    return {
        "requester_type": requester_type,
        "requester_ref": requester_ref,
        "secret_reference_id": secret_reference_id,
        "policy_outcome": policy_outcome,
        "access_outcome": access_outcome,
        "reason_code": reason_code,
    }
