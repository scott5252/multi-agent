from __future__ import annotations

from collections.abc import Mapping, Sequence
from uuid import UUID

from pydantic import BaseModel, Field

CLAIM_MAPPING_VERSION = "2026-04-22"


class NormalizedTokenClaims(BaseModel):
    subject: str
    issuer: str
    audience: tuple[str, ...]
    permissions: tuple[str, ...] = Field(default_factory=tuple)
    org_id: str | None = None
    tenant_id: UUID | None = None
    email: str | None = None
    display_name: str | None = None
    client_id: str | None = None
    jti: str | None = None


def _coerce_audience(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        audiences = tuple(item for item in value if isinstance(item, str))
        if audiences:
            return audiences
    raise ValueError("token is missing a valid audience claim")


def _coerce_permissions(payload: Mapping[str, object]) -> tuple[str, ...]:
    permissions = payload.get("permissions")
    if isinstance(permissions, Sequence) and not isinstance(permissions, str):
        values = tuple(item for item in permissions if isinstance(item, str))
        if values:
            return values
    scope = payload.get("scope")
    if isinstance(scope, str) and scope:
        return tuple(part for part in scope.split(" ") if part)
    return ()


def normalize_token_claims(
    payload: Mapping[str, object],
    *,
    required_org_claim: bool,
) -> NormalizedTokenClaims:
    subject = payload.get("sub")
    issuer = payload.get("iss")
    if not isinstance(subject, str) or not subject:
        raise ValueError("token is missing sub")
    if not isinstance(issuer, str) or not issuer:
        raise ValueError("token is missing iss")

    org_id = payload.get("org_id")
    if required_org_claim and (not isinstance(org_id, str) or not org_id):
        raise ValueError("token is missing org_id")

    tenant_id: UUID | None = None
    raw_tenant_id = payload.get("tenant_id")
    if isinstance(raw_tenant_id, str) and raw_tenant_id:
        tenant_id = UUID(raw_tenant_id)
    email = payload.get("email")
    display_name = payload.get("name")
    azp = payload.get("azp")
    client_id = payload.get("client_id")
    jti = payload.get("jti")

    return NormalizedTokenClaims(
        subject=subject,
        issuer=issuer,
        audience=_coerce_audience(payload.get("aud")),
        permissions=_coerce_permissions(payload),
        org_id=org_id if isinstance(org_id, str) else None,
        tenant_id=tenant_id,
        email=email if isinstance(email, str) else None,
        display_name=display_name if isinstance(display_name, str) else None,
        client_id=azp
        if isinstance(azp, str)
        else client_id
        if isinstance(client_id, str)
        else None,
        jti=jti if isinstance(jti, str) else None,
    )
