# Feature Specification: Live Model Credential Resolution For Gateway Calls

**Feature Branch**: `codex/025-live-model-credential-resolution-for-gateway-calls`
**Created**: 2026-05-04
**Status**: Draft
**Input**: Complete live model provider credential resolution for provider probes and runtime gateway calls. Provider connections must store safe secret reference ids, resolve them through the configured secret provider only at call time, never expose raw values, and pass resolved credentials into OpenAI or local OpenAI-compatible adapters. Failed or missing credentials must produce safe diagnostics and audit evidence.

## User Scenarios & Testing

### User Story 1 - Probe Uses Configured Secret References (Priority: P1)

Platform administrators can test an OpenAI or local OpenAI-compatible provider connection without entering raw credentials into the provider record or seeing raw values in UI, logs, diagnostics, or database evidence.

**Why this priority**: Provider health is the first visible trust signal for model routing. A probe that ignores configured references reports misleading readiness and pushes credential failures into runtime.

**Independent Test**: Save an active OpenAI connection with a safe secret reference and a mocked secret provider, run a provider probe, and verify the adapter receives the resolved value while persisted test results contain only safe reference metadata and normalized status.

**Acceptance Scenarios**:

1. **Given** an active OpenAI connection with `credential_secret_reference_ids=["qa025/openai-placeholder"]`, **When** a platform administrator runs a provider test, **Then** the configured secret provider resolves the reference at call time and the adapter receives the resolved credential.
2. **Given** an active OpenAI connection without a credential reference, **When** a platform administrator runs a provider test, **Then** the probe fails before any provider call with `secret_reference_invalid` and a safe diagnostic summary.
3. **Given** a local OpenAI-compatible connection with no credential reference and an allowlisted local endpoint, **When** a platform administrator runs a provider test, **Then** the probe may execute without an authorization header.

---

### User Story 2 - Runtime Gateway Resolves Credentials Live (Priority: P1)

Runtime model calls, test bench calls, and workflow validation calls go through `ModelGateway`, which resolves provider credentials from the connection's safe references immediately before the adapter call.

**Why this priority**: The Daily Intelligence Briefing scenario depends on live model calls after workflow and prompt/profile pins are resolved. Runtime calls must not depend on raw credentials passed through orchestration state.

**Independent Test**: Invoke `ModelGateway` with a healthy connection, mocked secret provider, and mocked adapter; verify the credential is resolved only during `invoke`, the adapter receives the value, and gateway attempt evidence records safe credential status without the raw value.

**Acceptance Scenarios**:

1. **Given** a healthy OpenAI connection with a safe reference, **When** a gateway invocation starts, **Then** the resolver fetches the secret and passes only the resolved call-time value to the adapter.
2. **Given** the secret provider cannot resolve the configured reference, **When** a gateway invocation starts, **Then** no adapter call occurs and the gateway records a failure with `secret_reference_invalid`.
3. **Given** a gateway operation identity is retried after a credential failure, **When** the duplicate call is processed, **Then** existing idempotency behavior remains authoritative and persisted evidence remains safe.

---

### User Story 3 - Diagnostics Stay Redaction-Safe (Priority: P2)

Operators and reviewers can inspect probe results, gateway attempts, operations diagnostics, and docs without raw provider secrets appearing anywhere in rendered pages, JSON responses, audit summaries, logs, screenshots, or QA artifacts.

**Why this priority**: Credential resolution is security-sensitive; the feature is incomplete if failure evidence leaks credential material.

**Independent Test**: Run targeted tests that include secret-like fixture values and scan provider diagnostics, gateway summaries, admin responses, README/docs, and QA artifacts for the raw fixture value.

**Acceptance Scenarios**:

1. **Given** a mocked secret provider returns a fake raw credential value, **When** probes and gateway calls succeed or fail, **Then** persisted evidence contains only reference ids, provider type, model id, status, and normalized categories.
2. **Given** a provider returns an authorization error, **When** the error is normalized, **Then** operator diagnostics show a safe failure category and do not include request headers or provider response bodies.
3. **Given** a tenant-scoped runtime call uses a visible connection, **When** evidence is listed in operations or usage surfaces, **Then** tenant ids, trace ids, and safe statuses are present while credentials remain absent.

### Edge Cases

- OpenAI connections with no credential reference fail before network calls.
- Configured references that are blank, duplicate, or look like raw secrets are rejected at validation time.
- Secret provider lookup failures and empty secret values normalize to `secret_reference_invalid`.
- Local OpenAI-compatible connections may omit a credential only when the base URL passes the configured local endpoint allowlist.
- Local OpenAI-compatible connections with a configured reference resolve it at call time and send the resolved value only to the allowlisted endpoint.
- Multiple credential references use stored order as administrator priority; only the first validated reference is used for the call.
- Probe and runtime failures must update health, attempt, operation, retry, breaker, and usage-safe evidence consistently without raw secret values.

## Requirements

### Functional Requirements

- **FR-001**: Provider connections MUST persist only safe credential secret reference ids, never raw credential values.
- **FR-002**: Provider probes MUST resolve the selected credential reference through the configured `SecretProvider` immediately before invoking the provider adapter.
- **FR-003**: `ModelGateway.invoke` MUST resolve the selected credential reference through `ProviderSecretResolver` immediately before invoking the provider adapter.
- **FR-004**: OpenAI provider probes and runtime calls MUST fail closed with `secret_reference_invalid` when no credential reference is configured or the configured reference cannot be resolved.
- **FR-005**: Local OpenAI-compatible provider probes and runtime calls MUST allow no-auth calls only for allowlisted local endpoints when no credential reference is configured.
- **FR-006**: Local OpenAI-compatible provider calls MUST pass the resolved credential to the adapter when a reference is configured.
- **FR-007**: Credential selection MUST use the first configured reference after validation, preserving administrator-entered order as priority.
- **FR-008**: Validation MUST reject blank references, duplicate references, and raw-secret-looking values such as `sk-`, bearer tokens, passwords, or direct API-key strings.
- **FR-009**: Probe results, gateway attempts, gateway operations, physical attempts, usage capture, health snapshots, audit summaries, API responses, admin UI rendering, logs, and docs MUST NOT include raw resolved secret values.
- **FR-010**: Credential resolution failures MUST avoid adapter calls and record safe diagnostic evidence with provider type, connection id, model id, reference id, and normalized category.
- **FR-011**: Container and worker bootstrap factories MUST expose configured secret resolution dependencies for provider probes and runtime gateway calls.
- **FR-012**: Tests MUST cover successful resolution, missing references, missing provider secrets, empty secrets, local no-auth behavior, adapter credential delivery, safe summaries, and docs.

### Key Entities

- **Provider Connection**: Existing model-provider configuration containing provider type, safe base URL, timeout policy, health, model definitions, visibility, and ordered credential secret reference ids.
- **Provider Secret Resolver**: Runtime service that selects and resolves safe provider credential references through the configured secret provider.
- **Provider Probe Result**: Persisted evidence for an administrator-initiated provider health test, including safe diagnostics and normalized categories.
- **Gateway Invocation Attempt**: Persisted runtime evidence for a model call attempt, including safe audit summary, retry and breaker summaries, usage availability, and normalized categories.
- **Gateway Operation**: Existing idempotent logical operation identity for runtime provider calls and duplicate recovery.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Targeted tests prove OpenAI probes and gateway calls pass resolved credentials into mocked adapters without persisting the raw value.
- **SC-002**: Targeted tests prove missing or unresolved OpenAI credentials fail before adapter invocation and record `secret_reference_invalid`.
- **SC-003**: Targeted tests prove local OpenAI-compatible calls work without credentials when no reference is configured and the endpoint is allowlisted.
- **SC-004**: Redaction tests prove the raw fixture secret string does not appear in provider test results, gateway attempt summaries, docs, or API/UI schemas.
- **SC-005**: Full quality gates pass: Ruff, format check, mypy, and pytest coverage at or above 90 percent.

## Assumptions

- Existing secret provider implementations (`static`, `env`, and secret manager placeholder) remain the source of truth for secret resolution.
- Existing provider connection storage already supports ordered `credential_secret_reference_ids`; no schema migration is required.
- No real provider credentials or real provider endpoints are required for local or CI validation.
- OpenAI-compatible local endpoints can be no-auth in local QA, but still must pass the local endpoint allowlist before any call.
- Credential rotation fallback across multiple references is out of scope until an explicit rotation policy is designed.

## Clarifications

- Q: How should multiple provider credential references be selected? -> A: Use the first configured reference in stored order as administrator priority; do not try fallback references during the same call. (autopilot)
- Q: How should local OpenAI-compatible providers behave when no credential reference is configured? -> A: Allow no-auth calls only for allowlisted local endpoints; resolve and send a credential when a reference is configured. (autopilot)

## Constitution Impact

- **Durable By Default**: Probe and gateway failures persist safe diagnostic evidence, health state, and attempt records.
- **Immutable State And Memory**: Gateway operations and physical attempts remain append-oriented; no memory behavior changes.
- **Contract-First Agent Coordination**: Provider resolver, probe, adapter, and gateway contracts are documented before implementation.
- **Security With Practical Development Ergonomics**: Local QA uses static fake secrets while exercising the same resolver path.
- **Operability Is A Product Requirement**: Operators receive normalized credential failure categories and safe summaries.
- **Tenant Isolation And Fair Scheduling**: Runtime calls preserve existing tenant-visible connection and retry/breaker scopes.
- **Version-Pinned Execution**: Gateway calls still occur after prompt/profile/model pins resolve.
- **Secret Hygiene And Controlled Tool Access**: Raw credentials stay outside persisted records, logs, docs, and UI.

## Testing Instructions

- Run focused provider tests listed in `testing-instructions.md`.
- Run QA validation from `specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml`.
- Run full quality gates with Ruff, format check, mypy, and coverage.

## PR Review Guidance

- Confirm credential resolution happens in probe and runtime paths, not at provider save time.
- Confirm OpenAI missing credentials fail closed before adapter invocation.
- Confirm local provider no-auth behavior is limited to allowlisted local endpoints.
- Confirm docs and tests never include real provider credentials.
- Confirm safe diagnostic summaries do not include request headers, provider response bodies, raw prompts, raw completions, or raw secret values.

## Documentation Impact

- Update `README.md` and `docs/quickstart.md` with QA025 credential-resolution validation.
- Add QA025 guide, UI guide, non-developer manual QA user guide, PR notes, and testing instructions.
