# Data Model: Model Provider Gateway

## ModelProviderConnection

Administrative record for an approved provider endpoint.

**Fields**: `provider_connection_id`, `provider_type` (`openai`,
`local_openai_compatible`), `display_name`, `base_url_safe`, `timeout_policy`,
`visibility_mode` (`platform_default`, `tenant_allowlist`), `active`,
`health_state`, `credential_secret_reference_ids`, `safe_metadata`,
`allowlist_decision_hash`, `created_by_principal_id`, `updated_by_principal_id`,
`created_at`, `updated_at`, `deactivated_at`.

**Validation**: Platform-admin-only mutation; provider type must be supported;
local providers require `base_url_safe` and allowlist approval; OpenAI may use
the default provider endpoint unless a safe override is explicitly supported;
timeout values must be bounded and positive; raw secrets, tokens, headers,
prompts, completions, and secret-bearing URL components are rejected.

**Relationships**: Has many `ProviderModelDefinition`,
`ConnectionTenantVisibility`, `ConnectionTestResult`,
`ConnectionHealthSnapshot`, `CatalogSyncRecord`, and
`GatewayInvocationAttempt`.

## ProviderModelDefinition

Configured model id and metadata within a connection.

**Fields**: `provider_model_definition_id`, `provider_connection_id`,
`model_id`, `display_name`, `capability_metadata`, `cost_metadata`,
`default_parameters`, `available`, `created_at`, `updated_at`.

**Validation**: Model ids are unique within a connection; capability/cost
metadata is JSON-safe and bounded; default parameters cannot contain prompts,
credentials, or provider response content.

**Relationships**: Publishes one or more `ModelProviderCatalogEntry` rows
through `CatalogSyncRecord`.

## ConnectionTenantVisibility

Explicit tenant allowlist row for a connection when visibility mode is
`tenant_allowlist`.

**Fields**: `connection_tenant_visibility_id`, `provider_connection_id`,
`tenant_id`, `visible`, `created_by_principal_id`, `created_at`, `revoked_at`.

**Validation**: Tenant id must exist and be grantable by the actor; revoked
rows are preserved for audit; visibility changes affect future routing only.

## ConnectionTestResult

Append-only safe probe result for a connection and optional model.

**Fields**: `connection_test_result_id`, `provider_connection_id`,
`provider_model_definition_id`, `actor_principal_id`, `source`
(`admin_user`, `system_refresh`), `started_at`, `completed_at`,
`latency_ms`, `outcome` (`success`, `failure`), `normalized_reason`,
`tested_model_id`, `safe_diagnostic_summary`, `safe_provider_request_id`,
`http_status_class`, `timeout_policy`, `created_at`.

**Validation**: Probe prompt and completion are never stored; raw provider
responses and secret-bearing errors are redacted before persistence; every
test attempt writes exactly one result even on timeout or validation failure.

## ConnectionHealthSnapshot

Current derived operational state for connection review and routing.

**Fields**: `connection_health_snapshot_id`, `provider_connection_id`,
`health_state` (`disabled`, `untested`, `healthy`, `degraded`, `failing`,
`unavailable`), `latest_test_result_id`, `derived_reason`, `derived_at`,
`selectable`.

**Validation**: `selectable=true` only when connection is active, latest
relevant test is successful, and health state is `healthy`.

## ModelProviderCatalogEntry

Existing model_skill_config catalog entry extended by this feature.

**Additional fields**: `provider_connection_id`,
`provider_model_definition_id`, `health_state`, `availability_status`,
`visibility_mode`, `tenant_visibility_hash`, `last_synced_at`,
`gateway_governed`.

**Validation**: Routing-selectable rows must be active, healthy,
tenant-visible, and gateway-governed. Publication blocks collisions on
tenant scope plus model id, including platform-default scope.

## CatalogSyncRecord

Append-only synchronization evidence from provider connection state into the
model provider catalog.

**Fields**: `catalog_sync_record_id`, `provider_connection_id`,
`provider_model_definition_id`, `model_provider_entry_id`, `tenant_id`,
`sync_action` (`created`, `updated`, `marked_unavailable`, `blocked`),
`outcome`, `normalized_reason`, `safe_summary`, `actor_principal_id`,
`created_at`.

**Validation**: Blocked collisions preserve prior catalog entries; deactivation
or removed visibility marks governed rows unavailable instead of deleting
history.

## GatewayInvocationAttempt

Append-only metadata for every runtime or test bench model attempt.

**Fields**: `gateway_invocation_attempt_id`, `tenant_id`,
`workflow_run_id`, `test_bench_run_id`, `trace_id`, `idempotency_key`,
`model_provider_entry_id`, `provider_connection_id`,
`provider_model_definition_id`, `provider_type`, `model_id`, `started_at`,
`completed_at`, `latency_ms`, `outcome`, `normalized_error_category`,
`retry_attempt_number`, `retry_decision_summary`, `breaker_scope`,
`breaker_decision_summary`, `usage_metadata`, `usage_available`,
`safe_audit_summary`, `created_at`.

**Validation**: Prompt messages, completions, raw provider request/response
bodies, resolved credentials, API keys, provider tokens, and local endpoint
secrets are prohibited. Usage metadata contains counts and provider model ids
only.

## CredentialSecretReference

Safe pointer to existing secret-provider-managed credential material.

**Fields**: Existing secret reference id plus provider role metadata such as
`api_key`, `bearer_token`, or `extra_header`.

**Validation**: References must resolve at test/runtime use, be active for the
requested environment, and pass existing secret-access policy. Missing,
inactive, expired, revoked, or tenant-inappropriate references fail closed.

## State Transitions

```text
connection draft/saved -> active -> disabled
active + untested -> untested
active + successful probe -> healthy -> catalog synced/selectable
active + transient failure -> degraded or failing -> catalog unavailable
active + timeout/unreachable/secret failure -> unavailable -> catalog unavailable
visibility removed -> catalog marked_unavailable for that tenant
model collision detected -> sync blocked, prior catalog unchanged
runtime invocation success -> attempt success with usage available/unavailable
runtime invocation transient failure -> retry-eligible then success/failure
runtime invocation non-retryable failure -> failure with normalized category
```

## Indexes And Constraints

- Unique provider model ids per connection.
- Partial unique catalog index for `(tenant_id, model_id)` where tenant id is
  present and entry is active.
- Partial unique catalog index for platform-default `model_id` where tenant id
  is null and entry is active.
- Indexes on connection active state, provider type, health state, tenant
  visibility, catalog provider connection id, test result timestamp, and
  invocation tenant/run/time filters.
- Check constraints for supported provider types, health states, normalized
  error categories, positive timeout values, and JSON object shape where
  practical.
