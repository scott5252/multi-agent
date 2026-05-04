# PR Review Notes: Live Model Credential Resolution For Gateway Calls

## Scope

- Completes call-time credential resolution for provider probes and runtime `ModelGateway` calls.
- Keeps provider records reference-only through `credential_secret_reference_ids`.
- Uses `ProviderSecretResolver` with the configured secret provider immediately before adapter invocation.
- Requires OpenAI credentials for probes and runtime calls.
- Preserves no-auth local OpenAI-compatible behavior for allowlisted local endpoints.
- Passes resolved credentials into OpenAI and local OpenAI-compatible adapters only through `AdapterRequest.credential`.
- Normalizes missing, unresolved, and empty secrets to `secret_reference_invalid`.

## Security And Privacy

- Raw resolved credentials are not persisted in provider connection rows, probe results, health snapshots, gateway attempts, gateway operations, physical attempts, usage records, docs, logs, or admin UI responses.
- Safe evidence may include credential reference ids, provider type, provider connection id, model id, tenant id, trace id, operation identity, and normalized category.
- Adapter request headers are process-local and covered by unit tests.
- Local provider calls without credentials are still constrained by the local endpoint allowlist.
- The QA environment uses fake static secrets and no production resource references.

## Durability

- Probe credential failures append `ConnectionTestResult` evidence and update health.
- Gateway credential failures append `GatewayInvocationAttempt` and `GatewayPhysicalAttempt` evidence.
- Gateway operation duplicate recovery remains authoritative and still suppresses duplicate provider calls.
- Retry, breaker, and usage-safe evidence remain populated for credential failures where applicable.

## Test Evidence

Review:

- `tests/unit/model_providers/test_secret_references.py`
- `tests/unit/model_providers/test_probes.py`
- `tests/unit/model_providers/test_model_provider_service.py`
- `tests/unit/model_providers/test_gateway.py`
- `tests/unit/model_providers/test_adapters.py`
- `tests/integration/runtime/test_gateway_operation_recovery.py`
- `tests/integration/model_providers/test_gateway_attempt_evidence.py`

Run:

```bash
uv run pytest --no-cov \
  tests/unit/model_providers/test_secret_references.py \
  tests/unit/model_providers/test_probes.py \
  tests/unit/model_providers/test_model_provider_service.py \
  tests/unit/model_providers/test_gateway.py \
  tests/unit/model_providers/test_adapters.py \
  tests/unit/model_providers/test_validation.py \
  tests/unit/api/test_model_provider_schemas.py \
  tests/integration/runtime/test_gateway_operation_recovery.py \
  tests/integration/model_providers/test_gateway_attempt_evidence.py
```

## Residual Limits

- Ordered credential fallback and rotation are intentionally out of scope.
- Real provider network calls are intentionally outside local and CI QA.
- Existing provider visibility and routing policies remain the authorization source; this feature does not add a new model-routing policy layer.
