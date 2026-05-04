from __future__ import annotations

from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    ErrorCategory,
    ProviderTestSummary,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
)
from multi_agent_platform.model_providers.secrets import (
    ProviderSecretResolver,
    SecretReferenceError,
)

SAFE_PROBE_MESSAGE = (
    {"role": "system", "content": "Return a short health check response."},
    {"role": "user", "content": "health"},
)


class ProviderProbeRunner:
    def __init__(
        self,
        registry: ProviderAdapterRegistry,
        *,
        secret_resolver: ProviderSecretResolver | None = None,
    ) -> None:
        self._registry = registry
        self._secret_resolver = secret_resolver

    async def run_probe(
        self,
        *,
        provider_type: ProviderType,
        model_id: str,
        timeout_policy: TimeoutPolicy,
        base_url: str | None,
        credential: str | None = None,
        credential_secret_reference_ids: tuple[str, ...] = (),
    ) -> ProviderTestSummary:
        resolved_credential = credential
        if self._secret_resolver is not None and credential is None:
            try:
                provider_credential = await self._secret_resolver.resolve_for_provider(
                    provider_type=provider_type,
                    credential_secret_reference_ids=credential_secret_reference_ids,
                )
            except SecretReferenceError as exc:
                return _credential_failure_summary(model_id=model_id, error=exc)
            resolved_credential = (
                provider_credential.value if provider_credential is not None else None
            )
        adapter = self._registry.get(provider_type)
        response = await adapter.chat_completion(
            AdapterRequest(
                model_id=model_id,
                messages=SAFE_PROBE_MESSAGE,
                timeout_policy=timeout_policy,
                base_url=base_url,
                credential=resolved_credential,
            )
        )
        return ProviderTestSummary(
            outcome=response.outcome,
            normalized_reason=response.normalized_error_category,
            latency_ms=response.latency_ms,
            tested_model_id=model_id,
            safe_diagnostic_summary=response.safe_diagnostic_summary,
            safe_provider_request_id=response.provider_request_id,
        )


def probe_succeeded(summary: ProviderTestSummary) -> bool:
    return summary.outcome is TestOutcome.SUCCESS


def _credential_failure_summary(
    *,
    model_id: str,
    error: SecretReferenceError,
) -> ProviderTestSummary:
    return ProviderTestSummary(
        outcome=TestOutcome.FAILURE,
        normalized_reason=ErrorCategory.SECRET_REFERENCE_INVALID,
        latency_ms=0,
        tested_model_id=model_id,
        safe_diagnostic_summary=str(error),
    )
