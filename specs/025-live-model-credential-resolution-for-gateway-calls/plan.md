# Implementation Plan: Live Model Credential Resolution For Gateway Calls

**Branch**: `codex/025-live-model-credential-resolution-for-gateway-calls` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/025-live-model-credential-resolution-for-gateway-calls/spec.md`

## Summary

Complete the credential boundary for live model provider calls by wiring `ProviderSecretResolver` into provider probes and `ModelGateway`. Provider connections continue to store only safe secret reference ids. Probe and runtime call paths select the first configured reference, resolve it through the configured secret provider immediately before adapter invocation, and pass the resolved credential to OpenAI or local OpenAI-compatible adapters. OpenAI calls fail closed when credentials are missing or unresolved. Local OpenAI-compatible calls may remain no-auth when no reference is configured and the endpoint is allowlisted. All failures and successes persist redaction-safe diagnostics only.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing secret providers, existing `ProviderSecretResolver`, `ModelProviderService`, `ProviderProbeRunner`, `ModelGateway`, OpenAI and local OpenAI-compatible adapters, audit/redaction helpers, reliability retry/breaker helpers, usage capture, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: Existing PostgreSQL tables for provider connections, connection test results, health snapshots, gateway invocation attempts, gateway operations, gateway physical attempts, usage metadata, and safe audit records. No new migration is required because credential references are already stored as `credential_secret_reference_ids`.
**Testing**: Unit tests for resolver selection/failure behavior, validation of credential references, provider probe credential use, gateway credential use, adapter authorization headers, safe summaries, container/worker dependency readiness, docs, Ruff, mypy, and coverage.
**Target Platform**: Linux API and worker containers plus local macOS/Linux development.
**Project Type**: Multi-tenant Python web service and durable worker runtime.
**Performance Goals**: Credential selection adds negligible CPU overhead. Secret resolution occurs once per probe or gateway physical attempt. Failed credential resolution avoids provider network latency and still records evidence.
**Constraints**: No raw credentials in database rows, logs, audit payloads, API responses, UI pages, docs, screenshots, or QA artifacts. No real provider credentials or production endpoints in local/CI validation. OpenAI calls require credentials; local OpenAI-compatible no-auth calls require an allowlisted local endpoint.
**Scale/Scope**: Applies to administrator provider probes, runtime orchestration model calls, profile/test bench model calls, model-backed workflow validation, gateway operation recovery, usage capture, and provider diagnostics.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Probe failures, gateway credential failures, health snapshots, attempt evidence, operation evidence, retry/breaker summaries, and usage-safe metadata persist before returning. |
| Immutable State And Memory | PASS | No mutable memory source of truth is introduced; gateway operations and physical attempts remain append-oriented evidence. |
| Contract-First Agent Coordination | PASS | Resolver, probe, adapter, and gateway contracts are documented in `contracts/gateway-credential-resolution.md`. |
| Security With Practical Development Ergonomics | PASS | Local QA uses static fake secret references and local principals while executing the same resolver path used by production. |
| Operability Is A Product Requirement | PASS | Operators receive normalized `secret_reference_invalid` diagnostics, connection/model ids, safe reference ids, and trace ids without raw secret values. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contract, quickstart, tasks, QA docs, implementation, and validation remain traceable. |
| Test And Documentation Discipline | PASS | Tasks include tests, docs, QA guide, README/quickstart updates, and full quality gates. |
| Clear Ownership And Small Safe Changes | PASS | Scope is limited to provider resolver, validation, probes, gateway, adapters, container wiring, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Runtime calls keep existing tenant-visible connection selection and retry/breaker scopes; credential resolution does not expand tenant visibility. |
| Version-Pinned Execution | PASS | Gateway calls still occur after prompt/profile/model routing pins resolve; credential resolution is call-time metadata and not part of mutable workflow definitions. |
| Secret Hygiene And Controlled Tool Access | PASS | Provider records store references only; resolver returns values only to adapter requests; persisted evidence is redacted. |
| Tiered Storage For Large Payloads | PASS | No large payload storage is introduced. |
| Human Approval Is Durable State | PASS | No approval/resume semantics change. |

Post-Phase-1 re-check: research, data model, contract, and quickstart preserve every `PASS` status. No exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/025-live-model-credential-resolution-for-gateway-calls/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── gateway-credential-resolution.md
├── tasks.md
├── qa025.md
├── qa025_ui.md
├── qa025_user_guide.md
├── pr-review-notes.md
├── testing-instructions.md
└── .env.qa025
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   └── schemas/model_providers.py
├── bootstrap/
│   ├── container.py
│   └── worker.py
├── model_providers/
│   ├── adapters.py
│   ├── gateway.py
│   ├── local_adapter.py
│   ├── openai_adapter.py
│   ├── probes.py
│   ├── secrets.py
│   ├── service.py
│   └── validation.py
└── db/repositories/model_providers.py

tests/
├── docs/
├── integration/model_providers/
├── integration/runtime/
├── unit/api/
├── unit/bootstrap/
└── unit/model_providers/
```

**Structure Decision**: Reuse the existing model provider package and bootstrap container. Add no schema migration and no new service boundary because the existing provider connection and gateway abstractions are the correct ownership points.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves credential selection, OpenAI credential requirements, local no-auth behavior, probe evidence, runtime gateway evidence, adapter headers, bootstrap wiring, idempotency interaction, and redaction checks. See [research.md](./research.md).

Key decisions:

- Treat `credential_secret_reference_ids` as ordered administrator priority and use the first reference.
- Reject blank, duplicate, and raw-secret-looking credential entries before persistence.
- Require credentials for OpenAI probes and runtime calls.
- Allow local OpenAI-compatible no-auth only when no reference is configured and the endpoint is allowlisted.
- Resolve credentials once per physical provider attempt, not when saving provider metadata.
- Convert missing, unresolved, and empty secrets into `secret_reference_invalid` without adapter calls.
- Persist safe credential reference ids and normalized categories only.

## Phase 1 Design And Contracts

Design artifacts:

- [data-model.md](./data-model.md) defines the existing records affected by call-time credential resolution.
- [contracts/gateway-credential-resolution.md](./contracts/gateway-credential-resolution.md) defines resolver, probe, gateway, adapter, failure, and redaction contracts.
- [quickstart.md](./quickstart.md) defines deterministic local QA with fake static secrets and no external provider side effects.

## API And UI Surface

- Provider admin API and UI continue accepting `credential_secret_reference_ids`.
- API/schema validation rejects raw-secret-looking values.
- Test results and connection detail pages continue showing safe reference ids and normalized diagnostic summaries only.
- No new endpoint is required.

## Migration Strategy

No migration is required. Existing `model_provider_connections.credential_secret_reference_ids` stores ordered safe references. Existing provider test, health, gateway attempt, operation, physical attempt, usage, and audit tables store safe metadata.

## Observability And Audit

- Probe credential failures append connection test results and health snapshots.
- Gateway credential failures append gateway attempt and physical attempt evidence.
- Safe summaries may include `credential_reference_id`, `credential_resolution_outcome`, `provider_connection_id`, `provider_type`, `model_id`, `tenant_id`, `trace_id`, and normalized category.
- Safe summaries must not include authorization headers, provider request bodies, raw prompt text, raw completion text, raw provider errors, or resolved credential values.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with QA025 entry points.
- Add QA025 guide, QA025 UI walkthrough, non-developer QA guide, PR review notes, and testing instructions.
