# Prompt Runtime Profiles PR Notes

## Summary

Spec `012` implements prompt lineage authoring, draft validation, safe fixture
previews, immutable prompt publication, retirement, tenant grants, agent
runtime profile validation, profile activation, tenant-over-platform
resolution, model-skill prompt digest hooks, workflow validation adapters,
runtime provenance pins, shared-shell browser pages, audit classifications,
metrics, docs, and QA evidence.

## Reviewer Focus

- Immutable prompt/profile versions are never edited after publication or
  activation.
- Retired prompt and profile versions are blocked for new use but remain
  reviewable through historical pins.
- Platform prompt/profile versions require explicit tenant grants.
- Prompt previews use sanitized fixture values only and do not call models or
  live run data.
- Model-skill prompt references include prompt library version ids and digests.
- Workflow validation records profile resolution and prompt ids.
- Runtime acceptance and first-use pinning preserve prompt/profile provenance.
- Audit records, logs, metrics, and pages use safe summaries.
- Bounded prompt validation rejects oversized prompt content and fixture sets.

## Browser Acceptance

Prompt authoring should be discoverable from `/admin`, complete under seven
minutes for a prepared reviewer, and expose validation, preview, publish,
retire, grants, and history without raw database access. Profile authoring
should complete under ten minutes and expose prompt references, policy
sections, validation, activation, resolution preview, retirement, and history.

Historical browser-flow coverage submitted the real prompt/profile forms
rather than checking template strings. On 2026-04-28,
`uv run pytest --no-cov tests/integration/api/test_prompt_runtime_browser_flows.py tests/integration/api/test_agent_profile_browser_flows.py`
passed with 2 tests covering prompt save, validation, safe preview, publish,
retire, grant, profile policy-section save, validation, activation, grant,
resolution, retire, and cross-tenant denial paths.

The broader completion-pass command passed with 23 focused tests across
contract coverage, auth policy coverage, form routes, services, and tenant
isolation. The full `uv run pytest --no-cov` run passed with 628 tests and one
existing SQLAlchemy table-cycle warning. The reviewer-facing QA script in
`specs/012-prompt-runtime-profiles/qa012.md` includes timed local acceptance
steps for recording the under-seven-minute prompt publish and under-ten-minute
profile activation checks during release review.

## Rollback And Retirement

Rollback is operationally handled by retiring prompt/profile versions from new
use and creating replacement versions. Historical workflow bundles and run
pins keep referencing the immutable versions they accepted.

## Spec 012 V2 Scope

Spec 012 V2 completes runtime gateway hardening by wiring container-managed
`ModelGateway` dependencies into workers and admin provider operations, adding
logical operation identities for gateway/probe/catalog recovery, and joining
prompt/profile pins with provider gateway metadata for new runs.

The V2 migration is additive with no destructive migrations, no historical
backfill rewrites, and no persistence of raw prompts, completions, provider
tokens, API keys, endpoint secrets, or unauthorized run content. Static and
behavioral guardrails enforce the `ModelGateway` adapter allowlist.

## Spec 012 V2 Acceptance Evidence

The focused V2 acceptance command passed with 35 tests:

```bash
uv run pytest --no-cov tests/unit/bootstrap/test_container_model_gateway_factories.py tests/unit/model_providers/test_gateway_dependency_lifecycle.py tests/unit/bootstrap/test_worker_gateway_bootstrap.py tests/integration/workers/test_worker_gateway_readiness.py tests/integration/db/test_prompt_runtime_profiles_v2_gateway_migration.py tests/unit/db/test_model_provider_operation_repository.py tests/unit/runtime/orchestration/test_model_gateway_invocation.py tests/integration/runtime/test_prompt_profile_gateway_pinning.py tests/integration/runtime/test_profile_test_bench_gateway.py tests/unit/agents/test_profile_gateway_routing_context.py tests/contract/test_runtime_gateway_execution_contract.py tests/integration/workflows/test_workflow_validation_model_gateway.py tests/unit/reliability/test_gateway_retry_decisions.py tests/unit/reliability/test_gateway_breaker_decisions.py tests/integration/runtime/test_gateway_operation_recovery.py tests/integration/api/test_admin_provider_probe_recovery.py tests/integration/model_providers/test_catalog_sync_recovery.py tests/integration/api/test_admin_model_provider_probe_limits.py tests/unit/model_providers/test_provider_probe_audit.py tests/unit/guardrails/test_model_gateway_only_provider_calls.py tests/integration/runtime/test_model_gateway_guardrails.py tests/unit/model_providers/test_gateway_safe_observability.py tests/integration/model_providers/test_gateway_attempt_evidence.py tests/integration/model_skill_config/test_prompt_profile_gateway_provenance.py tests/docs/test_prompt_runtime_profiles_v2_docs.py tests/integration/api/test_prompt_runtime_v2_browser_regression.py
```

This proves runtime execution, profile test bench calls, and model-backed
workflow validation use `ModelGateway` end to end; provider probes throttle
before provider activity; gateway, probe, and catalog operations recover
without duplicate authoritative effects; direct provider calls are blocked or
detected; safe audit and provenance joins prompt/profile pins with provider
metadata; and sensitive provider or prompt content is excluded from persisted
records, logs, metrics, traces, audits, and admin pages.
