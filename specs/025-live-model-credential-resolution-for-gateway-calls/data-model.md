# Data Model: Live Model Credential Resolution For Gateway Calls

## Existing Entities Used

### ModelProviderConnection

Stores provider configuration.

- `provider_connection_id`: stable connection id.
- `provider_type`: `openai` or `local_openai_compatible`.
- `base_url_safe`: safe endpoint for local or override providers.
- `timeout_policy`: connection timeout settings.
- `active`: whether routing may consider the connection.
- `health_state`: latest derived health state.
- `credential_secret_reference_ids`: ordered list of safe secret reference ids.
- `safe_metadata`: provider-safe metadata only.

Credential rule: values in `credential_secret_reference_ids` are references, not secrets. The first configured reference is selected for a probe or runtime call.

### ProviderModelDefinition

Stores model ids configured for a connection.

- `provider_model_definition_id`
- `provider_connection_id`
- `model_id`
- `available`

Credential resolution uses the connection, not the model definition.

### ConnectionTestResult

Stores provider probe evidence.

- `connection_test_result_id`
- `provider_connection_id`
- `provider_model_definition_id`
- `outcome`
- `normalized_reason`
- `safe_diagnostic_summary`
- `safe_provider_request_id`
- `timeout_policy`

Credential failure rule: missing, unresolved, and empty secrets create a failed result with `normalized_reason=secret_reference_invalid` and a safe diagnostic summary.

### ConnectionHealthSnapshot

Stores derived health after save and test actions.

- `connection_health_snapshot_id`
- `provider_connection_id`
- `health_state`
- `latest_test_result_id`
- `derived_reason`
- `selectable`

Credential failure rule: failed credential resolution makes the connection not selectable through existing health derivation.

### GatewayInvocationAttempt

Stores runtime model-call attempt evidence.

- `gateway_invocation_attempt_id`
- `tenant_id`
- `workflow_run_id`
- `test_bench_run_id`
- `trace_id`
- `idempotency_key`
- `provider_connection_id`
- `provider_type`
- `model_id`
- `outcome`
- `normalized_error_category`
- `retry_decision_summary`
- `breaker_scope`
- `breaker_decision_summary`
- `usage_metadata`
- `safe_audit_summary`

Credential failure rule: a failed resolution creates an attempt with `normalized_error_category=secret_reference_invalid` and safe reference metadata.

### GatewayOperation

Stores logical operation identity and duplicate recovery state.

- `gateway_operation_id`
- `operation_identity`
- `tenant_id`
- `workflow_run_id`
- `workflow_run_step_id`
- `test_bench_run_id`
- `workflow_validation_id`
- `provider_connection_id`
- `model_id`
- `status`
- `authoritative_outcome`
- `normalized_error_category`
- `safe_summary_json`

Credential failure rule: the operation's authoritative outcome may be failure with `secret_reference_invalid`; duplicate recovery remains unchanged.

### GatewayPhysicalAttempt

Stores physical attempt evidence under a gateway operation.

- `gateway_physical_attempt_id`
- `gateway_operation_id`
- `gateway_invocation_attempt_id`
- `physical_attempt_number`
- `outcome`
- `normalized_error_category`
- `retry_category`
- `retry_decision_summary_json`
- `breaker_scope`
- `breaker_decision_summary_json`
- `usage_metadata_json`
- `safe_audit_summary_json`

Credential failure rule: failed resolution records a physical attempt without a provider request id.

## New Domain Object

### ProviderCredentialResolution

In-memory value object only; not persisted.

- `reference`: selected safe secret reference id.
- `value`: resolved credential value, scoped to the immediate adapter request.
- `required`: whether provider type requires a credential.

Lifecycle:

1. Select reference from `credential_secret_reference_ids`.
2. Resolve through configured `SecretProvider`.
3. Pass resolved value into `AdapterRequest.credential`.
4. Drop value after adapter call returns.

No raw value is logged, persisted, rendered, or returned.

## Validation Rules

- Blank credential references are rejected.
- Duplicate credential references are rejected.
- Raw-secret-looking references are rejected.
- OpenAI connections may be saved without a reference, but probes and runtime calls fail closed until a reference resolves.
- Local OpenAI-compatible connections may omit a reference when the endpoint is allowlisted.

## State Transitions

### Probe Success

1. Connection and first model are loaded.
2. Credential is selected and resolved if required or configured.
3. Adapter receives `AdapterRequest.credential`.
4. `ConnectionTestResult` records success.
5. `ConnectionHealthSnapshot` marks connection according to existing health rules.

### Probe Credential Failure

1. Connection and first model are loaded.
2. Credential selection or resolution fails.
3. No adapter call occurs.
4. `ConnectionTestResult` records failure with `secret_reference_invalid`.
5. `ConnectionHealthSnapshot` marks connection not selectable.
6. Provider probe operation is completed with safe failure evidence.

### Gateway Success

1. Connection is loaded and checked for active/healthy status.
2. Gateway operation identity is created or recovered.
3. Credential is selected and resolved if required or configured.
4. Adapter receives `AdapterRequest.credential`.
5. Gateway attempt, physical attempt, retry/breaker summaries, and usage evidence are recorded safely.

### Gateway Credential Failure

1. Connection is loaded and checked for active/healthy status.
2. Gateway operation identity is created or recovered.
3. Credential selection or resolution fails.
4. No adapter call occurs.
5. Gateway attempt and physical attempt are recorded with `secret_reference_invalid`.
6. Usage capture records no usage.

## Data Retention

No new retention rules. Existing provider test and gateway attempt retention policies apply.
