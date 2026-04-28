# PR Review Notes: Model Provider Gateway

## Review Focus

- Provider connections store safe metadata and secret references only.
- Local OpenAI-compatible base URLs must pass the configured allowlist.
- Platform administrators can create, edit, activate, deactivate, test, and
  sync catalog entries from `/admin/model-providers`.
- Tenant-scoped users see only visible connections/catalog rows and cannot
  mutate or test providers.
- Safe probes capture outcome, latency, normalized reason, tested model, and
  diagnostics without raw prompt, completion, credential, or response content.
- Catalog synchronization publishes only active, healthy, tenant-visible,
  gateway-governed model entries and marks unavailable entries without deleting
  history.
- Runtime/test bench model calls use `ModelGateway` and persist safe invocation
  metadata.
- Retry and breaker summaries use normalized provider error categories.

## Known Boundaries

- The first supported providers are OpenAI and local OpenAI-compatible chat
  completions endpoints.
- Streaming, provider benchmarking, and multi-provider fallback orchestration
  remain out of scope.
- Secret values are resolved through existing secret providers and are never
  exposed in the connection UI.

## Required Evidence

Run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/011-model-provider-gateway
```

Then follow `qa011.md` and `QA011_UI.MD`.
