# Runtime Gateway Execution Contract

## Purpose

This contract defines how Spec 012 prompt/profile pins govern Spec 011
`ModelGateway` execution for production runtime, profile test bench,
model-backed workflow validation, provider probes, catalog sync, reliability,
guardrails, and safe audit evidence.

Existing prompt authoring, prompt lifecycle, runtime profile management,
browser UI, workflow validation, model-skill prompt reference integration,
tenant grants, immutable versioning, retirement, docs, and migration behavior
remain unchanged unless this contract names a narrow integration point.

## Container Factories

`Container` must expose gateway-ready factories and helpers:

```text
model_provider_repository_factory(session) -> ModelProviderRepository
model_provider_service_factory(session) -> ModelProviderService
provider_adapter_registry_factory() -> ProviderAdapterRegistry
model_gateway_factory(session) -> ModelGateway
provider_secret_resolver_factory(session) -> ProviderSecretResolver
gateway_metrics_hooks -> GatewayMetricsHooks
gateway_tracing_hooks -> GatewayTracingHooks
gateway_audit_hooks -> GatewayAuditHooks
retry_decision_helper -> RetryDecisionHelper
breaker_decision_helper -> BreakerDecisionHelper
```

Required behavior:

- Session-bound factories construct repositories and services for the caller's
  transaction boundary.
- Adapter registry owns any provider client lifecycle and exposes cleanup
  through the container dispose path when needed.
- Missing gateway, repository, adapter, secret, retry, breaker, metrics,
  tracing, or audit dependency marks worker gateway readiness as failed.
- Existing API startup and non-model-backed admin paths continue to work with
  backward-compatible defaults.

## Worker Bootstrap Contract

`WorkerBootstrap` must expose:

```text
container
worker_id
gateway_dependencies_ready
gateway_dependency_status
model_gateway_factory(session)
model_provider_service_factory(session)
retry_decision_helper
breaker_decision_helper
```

Workers must check gateway readiness before accepting model-backed work. A
worker may continue non-model-backed maintenance only when the claimed work
does not require provider invocation.

Workers must not create direct provider SDK clients or direct provider HTTP
clients. Provider transport belongs inside gateway adapters.

## Gateway Invocation Context

All model-backed production runtime calls must pass:

```json
{
  "tenant_id": "uuid",
  "workflow_run_id": "uuid",
  "workflow_run_step_id": "uuid-or-null",
  "trace_id": "trace-id",
  "idempotency_key": "logical-operation-key",
  "operation_identity": "stable-logical-operation-identity",
  "agent_key": "planner",
  "agent_kind": "agent",
  "agent_profile_version_id": "uuid",
  "prompt_version_ids": ["uuid"],
  "prompt_reference_version_ids": ["uuid"],
  "model_routing_provenance": {
    "resolver": "model_skill_config",
    "routing_version_ids": ["uuid"],
    "selected_provider_connection_id": "uuid",
    "selected_model_id": "model-id"
  },
  "profile_provenance": {
    "source_scope": "tenant-or-platform-fallback",
    "tenant_profile_precedence_applied": true
  },
  "memory_policy_context": {},
  "tool_policy_expectations": {},
  "output_contract_metadata": {},
  "side_effect_boundary": "before_provider_invocation"
}
```

Test bench and model-backed validation calls must use the same fields where
applicable and replace run identity with `test_bench_run_id` or
`workflow_validation_id`.

Required behavior:

- Prompt/profile pins must already be persisted or recovered before gateway
  invocation context is accepted.
- Dynamic first-use pins must be persisted before context construction.
- Model routing hints from profiles are advisory until model_skill_config,
  provider visibility, tenant authorization, health, credential, and policy
  checks approve the route.
- Failure to verify pins, tenant authorization, provider visibility, connection
  health, credential references, retry state, or breaker state fails closed.

## Invocation Ordering

Production model-backed runtime steps must follow this order:

1. Claim run or step lease.
2. Load immutable execution bundle and existing prompt/profile pins.
3. Resolve dynamic first-use profile/prompt pins only when the agent or
   sub-agent was not declared upfront.
4. Authorize route through model_skill_config and provider visibility.
5. Persist or recover `GatewayOperation` by logical operation identity.
6. Evaluate circuit breaker and retry budget state.
7. Invoke `ModelGateway` through an allowed adapter when policy permits.
8. Persist child physical attempt summary and safe audit evidence.
9. Continue to tool, memory, handoff, artifact, approval, or other side
   effects only after gateway outcome policy allows it.

## Idempotency And Recovery

Gateway invocations, provider probes, and catalog sync use one logical
operation identity per operation. Retries and restarts reuse it.

Duplicate behavior:

- If an operation is terminal and authoritative, return the prior safe result
  and record a duplicate-suppressed child event when useful.
- If an operation is in progress and still within the lease window, do not
  launch a duplicate physical provider attempt.
- If an operation is ambiguous after timeout or crash, recover from persisted
  checkpoint, safe provider request id when available, and retry/breaker policy.
- If recovery cannot verify safety, fail closed or schedule retry only when
  existing retry policy allows.

Catalog sync checkpoints must be safe and keyed by provider/model identity so
retry does not create duplicate authoritative catalog rows.

## Reliability Mapping

Provider categories map to retry and breaker policy as follows:

```text
timeout -> retryable timeout
rate_limit -> retryable rate_limited
provider_unavailable -> retryable dependency_unavailable
malformed_provider_response -> retryable dependency_unavailable unless policy marks provider bug as stopped
authorization_failure -> non-retryable authorization
policy_or_visibility_denial -> non-retryable policy_denial
secret_reference_invalid -> non-retryable configuration_denial
catalog_inactive -> non-retryable catalog_denial
invalid_model -> non-retryable catalog_denial
unknown_provider_failure -> retryable only when retry budget and breaker permit
none -> skipped for retry evaluation
```

Retry decision categories persisted on attempts:

```text
retryable
non-retryable
exhausted
skipped
recovered
```

Circuit breaker scope:

```text
provider_connection:{provider_connection_id}:model:{provider_model_definition_id-or-model_id}
```

Evidence may include tenant, run, step, trace, and actor context, but those do
not change breaker scope unless an existing reliability policy explicitly does
so.

## Admin Provider Probe Controls

Before provider activity, admin probes must evaluate:

```text
actor + provider connection rate limit
tenant backstop rate limit when tenant scope applies
global provider operation backstop
bounded-operation policy
provider visibility and actor authorization
credential reference validity
```

Denied and throttled attempts persist safe audit evidence containing actor,
scope, tenant where applicable, provider identity, operation identity, decision
category, and safe summary. They must not call the provider.

## Safe Audit And Observability Fields

Gateway attempts, probes, catalog sync, logs, traces, timeline events, and
browser review summaries may store:

```text
tenant id
workflow run id
run step id
test bench or validation id
trace id
agent key and kind
prompt version ids
prompt reference version ids
profile version id
provider connection id
provider model definition id
model id
operation identity
physical attempt number
retry category and summary
breaker scope and summary
latency
usage availability and token counts when safe
normalized outcome and error category
safe diagnostic summary
```

They must not store:

```text
raw prompts
rendered prompt content
completions
credentials
provider tokens
API keys
local endpoint secrets
unsafe preview content
unauthorized run content
cross-tenant protected content
```

## Direct Provider Call Guardrails

Allowed provider transport modules:

```text
src/multi_agent_platform/model_providers/openai_adapter.py
src/multi_agent_platform/model_providers/local_adapter.py
src/multi_agent_platform/model_providers/adapters.py
```

Static guardrail tests must fail when direct provider SDK imports, direct
provider client construction, or direct outbound provider HTTP calls appear in:

```text
src/multi_agent_platform/runtime/
src/multi_agent_platform/workers/
src/multi_agent_platform/agents/
src/multi_agent_platform/prompts/
src/multi_agent_platform/config/
src/multi_agent_platform/api/routers/
src/multi_agent_platform/api/ui/
tests/fixtures/ when used as runtime/test bench execution helpers
```

Behavioral tests must exercise a representative workflow run, profile test
bench execution, and model-backed workflow validation path and assert that each
provider call creates gateway operation metadata and safe attempt evidence.

## Backward Compatibility

Historical runs, prompt/profile pins, gateway attempt rows, provider probe
rows, and catalog sync rows that predate V2 remain valid. Review surfaces show
missing V2 fields as pre-V2/metadata-unavailable. No migration may backfill by
rewriting raw prompt, profile, run, or provider history.
