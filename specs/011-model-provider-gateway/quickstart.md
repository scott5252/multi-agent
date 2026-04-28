# Quickstart: Model Provider Gateway

## Prerequisites

- PostgreSQL is running and configured for the project.
- Secret references already exist in the configured secret provider for any
  OpenAI API key or local provider credential.
- Local provider base URLs are included in the administrator-managed allowlist
  settings before local probes are attempted.

## Validate The Design Locally

```bash
uv sync
uv run alembic upgrade head
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Run The API And Admin UI

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open the shared admin shell and navigate to **Model Providers**:

```text
http://127.0.0.1:8000/admin/model-providers
```

## Reviewer Flow

1. Sign in as a platform administrator or use deterministic local-principal
   mode.
2. Create an OpenAI provider connection with display name, model ids,
   capability metadata, cost metadata, timeout policy, tenant visibility, and
   secret references.
3. Create a local OpenAI-compatible provider connection with an allowlisted
   base URL, model ids, capability metadata, cost metadata, timeout policy,
   tenant visibility, and secret references.
4. Run safe tests for both connections from the Web UI and confirm each result
   stores timestamp, actor/source, latency, outcome, normalized reason, tested
   model, and safe diagnostic summary.
5. Confirm successful healthy connections publish or update tenant-visible
   catalog entries and that collisions are blocked.
6. Sign in as a tenant-scoped user and confirm only visible connections and
   catalog entries appear, with mutation and testing controls unavailable.
7. Run a workflow and a test bench case that require model calls; confirm both
   go through `ModelGateway`.
8. Inspect audit/debug evidence for safe summaries, model selection metadata,
   latency, normalized errors, retry and breaker inputs, and token usage
   metadata when available.
9. Search connection records, catalog entries, logs, audit summaries, and
   gateway metadata for raw API keys, provider tokens, prompts, completions,
   and local endpoint secrets; none should be present.

## Mock Provider Test Scenarios

- OpenAI success with usage metadata.
- OpenAI authorization failure.
- Local provider success without usage metadata.
- Local provider timeout.
- Local provider rate limit.
- Malformed provider response.
- Missing or revoked secret reference.
- Local URL outside allowlist.
- Catalog model id collision for the same tenant scope.

## Expected Evidence

- `docs/model-provider-gateway.md` documents provider setup, safe tests,
  catalog visibility, gateway behavior, health states, and sensitive-data
  protections.
- `specs/011-model-provider-gateway/pr-review-notes.md` calls out known risks,
  review focus, and verification evidence.
- `specs/011-model-provider-gateway/testing-instructions.md` gives reviewer QA
  steps for admin UI, APIs, mocked providers, runtime calls, and secret
  hygiene.
- `specs/011-model-provider-gateway/qa011.md` provides copy/paste reviewer QA
  with deterministic seed data and expected outputs.
- `specs/011-model-provider-gateway/QA011_UI.MD` explains every Web UI page and
  how platform admins and tenant readers use the new provider features.

## Copy/Paste QA

For a full local acceptance pass:

```bash
cp specs/011-model-provider-gateway/.env.qa011 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Then follow `qa011.md` and `QA011_UI.MD`.
