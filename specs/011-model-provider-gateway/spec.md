# Feature Specification: Model Provider Gateway

**Feature Branch**: `011-model-provider-gateway`  
**Created**: 2026-04-28  
**Status**: Draft  
**Input**: User description: "Add model provider connection management and a runtime model gateway. Platform admins must be able to configure OpenAI LLM connections and local open-source LLM connections, including provider type, display name, base URL when applicable, model ids, capability metadata, cost metadata, timeout policy, tenant visibility, and secret references for credentials. The Web UI must be updated to support these new features. The system must test connections through safe probes, store last test result and health state, and create or update tenant-visible model provider catalog entries that model routing can select. Runtime workers and test bench runs must call a ModelGateway abstraction instead of provider SDKs directly. The gateway must capture latency, normalized errors, model selection trace metadata, token usage metadata when available, retry/breaker inputs, and safe audit summaries. Raw API keys, provider tokens, prompts, completions, and local endpoint secrets must never be logged or stored in connection records. Require platform-admin-only mutation by default, tenant-scoped read visibility, at least 90 percent coverage, docs, PR review notes, testing instructions, and README updates."

## Clarifications

### Session 2026-04-28

- Q: What network boundary must local open-source provider base URLs satisfy? → A: Administrator-managed allowlist
- Q: What API contract must local open-source providers expose for probes and runtime calls? → A: OpenAI-compatible chat completions
- Q: Which provider connection health states may model routing select? → A: Healthy only
- Q: How should tenant-visible model identifier collisions be handled? → A: Block colliding publication
- Q: What tenant visibility shapes must model provider catalog entries support? → A: Platform defaults plus tenant allowlist

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Provider Connections (Priority: P1)

As a platform administrator, I need to create and maintain OpenAI and local open-source model provider connections through the admin experience so that tenants can use approved model endpoints with clear metadata, visibility, and credential references.

**Why this priority**: Provider connections are the source of tenant-visible model catalog entries. Without secure configuration and visibility controls, routing cannot safely select models for execution.

**Independent Test**: Can be fully tested by signing in as a platform administrator, creating an OpenAI connection and a local open-source connection with model, capability, cost, timeout, tenant visibility, and secret-reference metadata, then confirming tenant-scoped users can view only the entries visible to their tenant and cannot mutate them.

**Acceptance Scenarios**:

1. **Given** a platform administrator has valid connection metadata and credential references, **When** they save an OpenAI provider connection, **Then** the connection is stored with provider type, display name, model identifiers, capability metadata, cost metadata, timeout policy, tenant visibility, and credential references without exposing secret values.
2. **Given** a platform administrator has a local model endpoint, **When** they save a local open-source provider connection, **Then** the connection requires the applicable endpoint location, model identifiers, capability metadata, cost metadata, timeout policy, tenant visibility, and credential references without exposing endpoint secrets.
3. **Given** a tenant-scoped administrator or viewer opens model provider configuration, **When** they review available connections, **Then** they only see connections and catalog entries visible to their tenant and cannot create, update, activate, deactivate, or test provider connections unless they also have platform administrator authority.
4. **Given** a non-platform administrator attempts to mutate a provider connection directly, **When** the request is evaluated, **Then** the platform denies the mutation, preserves the prior configuration, and records a safe audit event.

---

### User Story 2 - Test Connections And Publish Catalog Entries (Priority: P2)

As a platform administrator, I need to safely test configured provider connections and publish tenant-visible model catalog entries so that model routing can select only known, reviewable model options.

**Why this priority**: A connection that cannot be tested or reflected into the catalog creates operational uncertainty. Safe test evidence and health state are needed before routing relies on a provider connection.

**Independent Test**: Can be fully tested by running connection tests for configured OpenAI and local provider connections, reviewing stored last-test results and health state, and confirming tenant-visible model provider catalog entries are created or updated for each visible model.

**Acceptance Scenarios**:

1. **Given** a configured provider connection, **When** a platform administrator runs a test, **Then** the system performs a safe probe, records the result, latency, timestamp, normalized outcome, and health state, and does not store raw prompts, completions, API keys, provider tokens, or endpoint secrets.
2. **Given** a connection test succeeds, **When** the connection is active, **Then** tenant-visible model provider catalog entries are created or updated with model identifiers, provider type, display name, capability metadata, cost metadata, health state, and tenant visibility.
3. **Given** a connection test fails because of authorization, timeout, unavailable endpoint, invalid model, rate limiting, malformed response, or another provider problem, **When** the result is recorded, **Then** the failure is normalized into a safe category that administrators can act on without exposing sensitive request or response content.
4. **Given** a connection is deactivated or loses tenant visibility, **When** catalog entries are refreshed, **Then** model routing no longer treats the affected model entries as selectable for tenants that should not see them.

---

### User Story 3 - Invoke Models Through The Gateway (Priority: P3)

As an operator or workflow maintainer, I need runtime workers and test bench runs to use a shared model gateway for every model call so that provider behavior, tracing, usage, failures, retries, and audit summaries are consistent.

**Why this priority**: Connection management only becomes reliable when execution uses the configured catalog and captures uniform operational evidence. Direct provider-specific calls would bypass governance and observability.

**Independent Test**: Can be fully tested by running a workflow and a test bench execution that require model calls, confirming both use the shared gateway path, and reviewing safe invocation metadata for latency, selected model trace, normalized errors, token usage when available, retry and breaker inputs, and audit summaries.

**Acceptance Scenarios**:

1. **Given** a runtime worker needs a model-backed response, **When** it invokes the selected model, **Then** the call is made through the shared model gateway using a tenant-visible catalog entry and connection metadata.
2. **Given** a test bench run needs a model-backed response, **When** it invokes the selected model, **Then** the call uses the same gateway behavior and produces the same classes of safe metadata as production runtime workers.
3. **Given** a provider returns token usage metadata, **When** the gateway records invocation evidence, **Then** token usage is captured in normalized metadata; if usage is unavailable, the record clearly marks it unavailable without failing an otherwise successful call.
4. **Given** a provider call fails or times out, **When** the gateway reports the failure, **Then** the system records a normalized error category, retry and breaker inputs, latency, selected model trace metadata, and a safe audit summary without storing raw prompts, completions, credentials, or endpoint secrets.

---

### User Story 4 - Review Delivery Evidence And Safe Operations (Priority: P4)

As a reviewer, auditor, or maintainer, I need documentation, review notes, testing instructions, and coverage evidence so that I can verify provider setup, gateway invocation, tenant visibility, and sensitive-data protections before release.

**Why this priority**: Review evidence is necessary for production readiness, especially because this feature touches credentials, tenant visibility, runtime execution, health state, cost metadata, and audit trails.

**Independent Test**: Can be fully tested by reviewing the submitted documentation, PR review notes, testing instructions, and coverage report, then following the instructions to verify provider configuration, safe probes, catalog updates, gateway calls, authorization, tenant visibility, and secret hygiene.

**Acceptance Scenarios**:

1. **Given** the feature is submitted for review, **When** a maintainer opens the PR review notes, **Then** the notes identify model provider configuration, safe probes, catalog publication, gateway invocation, tenant visibility, authorization, retry and breaker inputs, usage metadata, audit summaries, and known risks.
2. **Given** a reviewer follows the testing instructions, **When** they exercise OpenAI and local provider setup, connection tests, catalog visibility, runtime calls, and test bench calls, **Then** the instructions are sufficient to verify the feature without additional verbal guidance.
3. **Given** a security reviewer searches connection records, catalog entries, logs, audit summaries, and gateway metadata, **When** they inspect stored data, **Then** raw API keys, provider tokens, prompts, completions, and local endpoint secrets are absent.

### Edge Cases

- A provider connection is saved without required provider-specific metadata, such as a local endpoint location for a local provider; the system rejects the change with a safe, actionable validation message.
- A local open-source provider base URL does not match the administrator-managed endpoint allowlist; the system rejects the connection or test request before any network probe is attempted.
- A provider connection references a missing, inactive, expired, revoked, or tenant-inappropriate credential reference; tests and runtime selection fail closed without exposing credential values.
- A model identifier is duplicated within a connection or would collide with an existing tenant-visible catalog entry for the same tenant scope and model identifier; the system blocks save or publication until the administrator changes the model identifier, visibility, or connection.
- A safe probe times out, is rate limited, receives an unexpected response, or reaches a local endpoint that is unavailable; the last test result and health state remain reviewable with normalized categories.
- A provider supplies no token usage metadata; the gateway records usage as unavailable while still capturing latency, model selection trace metadata, and safe audit summaries.
- A platform administrator changes tenant visibility while runs are queued or active; future routing decisions follow the updated visibility while prior run evidence remains intact.
- A provider connection is deactivated after catalog entries have already been published; affected entries become unselectable without deleting historical evidence.
- A tenant-scoped user attempts to view a provider connection outside their tenant visibility; the platform fails closed without revealing whether the hidden connection exists.
- A local endpoint URL, header, token, or secret-bearing connection detail appears in a provider error; stored records and logs retain only safe summaries.
- Runtime or test bench code attempts to call a provider outside the shared gateway path; delivery is not considered complete until the bypass is removed or blocked by tests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST allow platform administrators to create, view, update, activate, deactivate, and test model provider connections for OpenAI and local open-source providers.
- **FR-002**: Provider connection mutation MUST be platform-admin-only by default; tenant-scoped users MUST have read visibility only for connections and catalog entries visible to their tenant through platform-default visibility or an explicit tenant allowlist entry.
- **FR-003**: The admin web experience MUST support listing, creating, editing, activating, deactivating, testing, and reviewing model provider connections and their tenant-visible catalog entries.
- **FR-004**: Each provider connection MUST capture provider type, display name, applicable endpoint location, model identifiers, capability metadata, cost metadata, timeout policy, tenant visibility, active state, health state, last test result, and credential secret references.
- **FR-005**: Provider connections MUST store secret references and safe metadata only; raw API keys, provider tokens, local endpoint secrets, prompts, and completions MUST NOT be stored in provider connection records.
- **FR-006**: Provider connection validation MUST reject missing required fields, malformed endpoint locations, local provider base URLs that do not match an administrator-managed allowlist of permitted hosts, CIDRs, and schemes, local provider configurations that do not expose an OpenAI-compatible chat-completions API, duplicate model identifiers within a connection, tenant-visible catalog collisions on tenant scope plus model identifier, unsupported provider types, invalid timeout policies, and tenant visibility that the actor is not authorized to grant.
- **FR-007**: Connection tests MUST use safe probes that avoid customer prompts and avoid storing raw provider responses, completions, credentials, or secret-bearing endpoint details; local provider probes MUST use the configured OpenAI-compatible chat-completions contract.
- **FR-008**: Each connection test MUST store a last-test result that includes timestamp, actor or system source, outcome, normalized reason category, latency, tested model or scope, and safe diagnostic summary.
- **FR-009**: Each provider connection MUST expose a health state derived from the latest relevant test and administrative status so administrators can distinguish healthy, degraded, failing, untested, disabled, and unavailable connections.
- **FR-010**: Successful active provider connections MUST create or update tenant-visible model provider catalog entries for configured model identifiers and visibility scopes; visibility scopes MUST support platform-visible defaults and explicit tenant allowlists, and only entries governed by a connection whose latest relevant test produced a healthy state are selectable for routing.
- **FR-011**: Catalog entries produced by provider connections MUST include provider type, display name, model identifier, capability metadata, cost metadata, tenant visibility scope, availability status, health state, and a reference to the governing connection without exposing secrets.
- **FR-012**: Model routing MUST be able to select only catalog entries that are active, tenant-visible, healthy from the latest relevant successful test, and available for the requested model-backed execution context.
- **FR-013**: Runtime workers MUST make model provider calls through the shared model gateway rather than direct provider-specific integration paths.
- **FR-014**: Test bench runs MUST make model provider calls through the same shared model gateway used by runtime workers.
- **FR-015**: The model gateway MUST use the resolved tenant-visible catalog entry and provider connection metadata when invoking a model; local provider invocations MUST use the configured OpenAI-compatible chat-completions contract.
- **FR-016**: The model gateway MUST capture latency, normalized error category, model selection trace metadata, token usage metadata when the provider makes it available, retry inputs, breaker inputs, and safe audit summaries for every invocation attempt.
- **FR-017**: Normalized gateway errors MUST distinguish at least authorization failure, invalid model, timeout, rate limit, provider unavailable, malformed provider response, policy or visibility denial, and unknown provider failure.
- **FR-018**: Retry and breaker inputs captured by the gateway MUST be sufficient for operations review while excluding raw prompts, completions, credentials, provider tokens, API keys, and local endpoint secrets.
- **FR-019**: Timeout policy from the provider connection MUST govern both safe connection tests and runtime gateway invocation attempts unless a stricter runtime policy already applies.
- **FR-020**: Gateway audit summaries MUST identify tenant, run or test bench context when available, selected provider connection, selected model, result category, latency, usage availability, and retry or breaker signal without exposing protected content or secrets.
- **FR-021**: Administrative provider connection changes, connection tests, catalog publication changes, denied mutations, and gateway failures MUST create safe audit evidence visible to authorized reviewers.
- **FR-022**: The platform MUST fail closed when connection metadata, tenant visibility, catalog availability, credential references, or healthy latest-test state cannot be verified for a model selection.
- **FR-023**: The delivered feature MUST include tests demonstrating at least 90 percent coverage for submitted provider connection, safe probe, catalog publication, tenant visibility, authorization, gateway invocation, metadata capture, error normalization, and secret hygiene behavior.
- **FR-024**: The delivered feature MUST include PR review notes covering provider setup, local provider endpoint safety, safe probes, catalog publication, gateway usage, usage metadata, retry and breaker inputs, tenant visibility, authorization, audit summaries, and known risks.
- **FR-025**: The delivered feature MUST include testing instructions that allow reviewers to verify OpenAI connection setup, local provider setup, connection test success and failure, health state, catalog entry creation and update, tenant visibility, runtime gateway calls, test bench gateway calls, normalized errors, usage metadata, timeout policy, and secret hygiene.
- **FR-026**: The delivered feature MUST update the README and supporting documentation with user-facing guidance for configuring provider connections, testing them safely, understanding catalog visibility, using the runtime gateway, reviewing health state, and verifying sensitive-data protections.

### Key Entities

- **Model Provider Connection**: An administrative record for a configured OpenAI or local open-source provider, including safe metadata, model identifiers, timeout policy, tenant visibility, health state, last test result, active state, and credential secret references.
- **Provider Model Definition**: A model identifier within a provider connection, including display information, capability metadata, cost metadata, and selection availability for one or more tenant scopes.
- **Catalog Uniqueness Rule**: The constraint that no two tenant-visible catalog entries may share the same tenant scope and model identifier at publication time.
- **Tenant Visibility Rule**: The rule that determines which tenants can read and route to a connection's catalog entries, either through platform-default visibility or an explicit tenant allowlist.
- **Connection Test Result**: The latest safe probe evidence for a provider connection, including outcome, normalized reason, latency, timestamp, tested model or scope, source, and safe diagnostic summary.
- **Connection Health State**: The current operational state of a provider connection derived from administrative status and test evidence.
- **Model Provider Catalog Entry**: A tenant-visible model option published from an active provider connection for model routing selection.
- **Model Gateway Invocation**: A runtime or test bench model attempt made through the shared gateway, with selection trace metadata, latency, outcome, normalized error when applicable, usage metadata when available, retry and breaker inputs, and safe audit summary.
- **Local Provider API Contract**: The OpenAI-compatible chat-completions interface that configured local open-source providers must expose for safe probes and runtime gateway calls.
- **Credential Secret Reference**: A safe pointer to credential material stored outside provider connection records, catalog entries, runtime metadata, logs, and audit summaries.
- **Safe Audit Summary**: Reviewable evidence about administrative or runtime behavior that preserves tenant, actor, connection, model, result, and timing context without protected prompts, completions, credentials, or endpoint secrets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Reviewer acceptance flow can configure and save both an OpenAI provider connection and a local open-source provider connection using the documented admin UI steps, with expected evidence captured in testing instructions.
- **SC-002**: 100 percent of provider connection mutations are denied for users who do not have platform administrator authority, while tenant-scoped readers see only connections and catalog entries visible to their tenant.
- **SC-003**: 100 percent of connection test attempts store a last-test result and health state with normalized outcome, latency, timestamp, and safe diagnostic summary.
- **SC-004**: 100 percent of active, tenant-visible configured models from connections with a healthy latest relevant test have matching model provider catalog entries that model routing can evaluate.
- **SC-005**: 100 percent of runtime worker model calls and test bench model calls in acceptance testing use the shared gateway path.
- **SC-006**: 100 percent of gateway invocation attempts capture latency, model selection trace metadata, outcome category, retry and breaker inputs, safe audit summary, and token usage metadata when available from the provider.
- **SC-007**: Security review finds zero raw API keys, provider tokens, prompts, completions, or local endpoint secrets in provider connection records, catalog entries, logs, audit summaries, or gateway metadata produced by this feature.
- **SC-008**: Admin browser-flow tests verify that provider connection health, last test result, tenant visibility, and catalog publication status are present on the list, detail, and catalog pages without relying on hidden state or manual database inspection.
- **SC-009**: Submitted provider connection management and gateway behavior demonstrates at least 90 percent test coverage.
- **SC-010**: PR review notes, testing instructions, README updates, and supporting documentation are present and sufficient for a maintainer to verify the feature without additional verbal explanation.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover OpenAI provider setup, local provider setup, required metadata validation, platform-admin-only mutation, tenant-scoped read visibility, safe probe success and failure, last-test result storage, health state, catalog entry creation and update, catalog visibility removal, runtime gateway calls, test bench gateway calls, normalized provider errors, timeout behavior, usage metadata capture, retry and breaker inputs, audit summaries, and sensitive-data search checks.
- **PR Review Guidance**: PR notes must call out provider configuration boundaries, endpoint and credential safety, tenant visibility, safe probe design, catalog publication rules, gateway-only invocation, model selection trace metadata, usage metadata behavior, normalized errors, retry and breaker signal handling, fail-closed paths, audit summaries, documentation, tests, and known risks.
- **Documentation Impact**: The feature requires updates to README and supporting docs covering how platform administrators configure provider connections, which fields are required for OpenAI and local providers, how safe tests work, how tenant visibility affects catalog entries, how routing selects catalog entries, what metadata the gateway records, and how sensitive data is excluded from records and logs.

## Assumptions

- The existing platform role model can identify platform administrators and tenant-scoped readers.
- Secret material is stored outside this feature; provider connection records keep only references and safe metadata.
- OpenAI and local open-source providers are the first supported provider types for this feature.
- Capability and cost metadata may be entered or corrected by platform administrators even when a provider can supply partial metadata.
- Safe probes use non-sensitive, provider-appropriate checks and do not use tenant or customer prompts.
- Existing model routing behavior can consume tenant-visible model provider catalog entries once this feature publishes them.
- Runtime workers and test bench runs already have a model selection step; this feature standardizes invocation and evidence capture after selection.
- Automatic cost optimization, provider benchmarking, multi-provider fallback strategy, and full secret-management workflows are out of scope unless represented through explicit connection metadata and existing routing behavior.
