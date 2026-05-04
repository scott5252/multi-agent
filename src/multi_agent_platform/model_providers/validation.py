from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import UUID

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.model_providers.allowlist import (
    AllowlistError,
    LocalEndpointAllowlist,
    validate_local_endpoint,
)
from multi_agent_platform.model_providers.models import (
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
    VisibilityMode,
)


class ProviderValidationError(ValueError):
    def __init__(self, message: str, *, field: str) -> None:
        super().__init__(message)
        self.field = field


@dataclass(frozen=True, slots=True)
class ProviderConnectionDraft:
    provider_type: ProviderType
    display_name: str
    base_url: str | None
    timeout_policy: TimeoutPolicy
    visibility: TenantVisibility
    models: tuple[ProviderModel, ...]
    credential_secret_reference_ids: tuple[str, ...]
    active: bool


def validate_connection_draft(
    draft: ProviderConnectionDraft,
    *,
    principal: PrincipalContext,
    allowlist: LocalEndpointAllowlist,
) -> ProviderConnectionDraft:
    if "platform_admin" not in principal.role_codes:
        raise ProviderValidationError("platform administrator required", field="actor")
    if not draft.display_name.strip():
        raise ProviderValidationError("display name is required", field="display_name")
    if not draft.models:
        raise ProviderValidationError("at least one model is required", field="models")
    _reject_duplicate_models(draft.models)
    if draft.provider_type is ProviderType.LOCAL_OPENAI_COMPATIBLE:
        if not draft.base_url:
            raise ProviderValidationError(
                "local providers require base_url",
                field="base_url",
            )
        try:
            validate_local_endpoint(draft.base_url, allowlist)
        except AllowlistError as exc:
            raise ProviderValidationError(str(exc), field="base_url") from exc
    if (
        draft.provider_type is ProviderType.OPENAI
        and draft.base_url
        and not draft.base_url.startswith("https://")
    ):
        raise ProviderValidationError(
            "OpenAI endpoint overrides must use https",
            field="base_url",
        )
    credential_secret_reference_ids = _validate_credential_references(
        draft.credential_secret_reference_ids
    )
    if draft.visibility.mode is VisibilityMode.TENANT_ALLOWLIST:
        _validate_grantable_tenants(draft.visibility.tenant_ids, principal=principal)
    if credential_secret_reference_ids == draft.credential_secret_reference_ids:
        return draft
    return replace(
        draft,
        credential_secret_reference_ids=credential_secret_reference_ids,
    )


def _reject_duplicate_models(models: tuple[ProviderModel, ...]) -> None:
    seen: set[str] = set()
    for model in models:
        normalized = model.model_id.strip()
        if normalized in seen:
            raise ProviderValidationError(
                "model ids must be unique within a connection",
                field="models",
            )
        seen.add(normalized)


def _validate_grantable_tenants(
    tenant_ids: tuple[UUID, ...],
    *,
    principal: PrincipalContext,
) -> None:
    if "platform_admin" in principal.role_codes:
        return
    if principal.tenant_id not in tenant_ids:
        raise ProviderValidationError(
            "actor cannot grant visibility for this tenant",
            field="visibility",
        )


def _validate_credential_references(references: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for reference in references:
        safe_reference = reference.strip()
        if not safe_reference:
            raise ProviderValidationError(
                "credential secret references cannot be blank",
                field="credential_secret_reference_ids",
            )
        lowered = safe_reference.lower()
        if any(
            marker in lowered
            for marker in ("sk-", "bearer ", "password", "secret=", "api_key=")
        ):
            raise ProviderValidationError(
                "credential fields accept secret references only",
                field="credential_secret_reference_ids",
            )
        if safe_reference in seen:
            raise ProviderValidationError(
                "credential secret references must be unique",
                field="credential_secret_reference_ids",
            )
        seen.add(safe_reference)
        normalized.append(safe_reference)
    return tuple(normalized)
