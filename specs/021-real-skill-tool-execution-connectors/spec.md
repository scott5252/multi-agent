# Feature Specification: Real Skill Tool Execution Connectors

**Feature Branch**: `codex/021-real-skill-tool-execution-connectors`
**Created**: 2026-05-04
**Status**: Draft
**Input**: User description: "Add a governed runtime tool execution layer and first-party read-only skill adapters for the Daily Intelligence Briefing scenario. The platform must execute approved skill tools for Google Calendar event reads, Gmail message reads, web/news search, weather forecast lookup, and commute or traffic lookup through installed skill versions. Tool calls must resolve only delegated credential or secret-reference metadata, enforce model-skill tool policy and outbound policy, block unsafe side effects by default, store redacted request/response summaries, and return structured outputs matching workflow contracts. The feature must support mock fixtures for local QA and approved live probes for staging."

## Autopilot Clarifications

- Q: Should live provider calls be enabled during local QA? -> A: No. Local QA defaults to mock fixtures; live calls require an explicit live-probe mode, tenant-scoped installation, delegated credential or secret-reference metadata, and policy allow decisions. (autopilot)
- Q: How should external provider payloads be persisted? -> A: Persist only redacted request and response summaries plus optional artifact references; raw external payloads are never stored inline. (autopilot)
- Q: Are any write-capable or side-effecting tools in scope? -> A: No. Calendar, Gmail, news, weather, and commute adapters are read-only for this feature, and unsafe side effects are blocked by default. (autopilot)

## User Scenarios & Testing

### User Story 1 - Execute Approved Read-Only Skill Tools (Priority: P1)

Runtime graph role nodes can request Daily Intelligence Briefing tools and receive structured, contract-shaped results only when the skill version, tenant installation, tool policy, outbound policy, and credential metadata all permit execution.

**Why this priority**: Without a governed execution gateway, the workflow graph can describe tools but cannot safely call them.

**Independent Test**: Submit mock-mode tool requests for calendar, Gmail, news, weather, and commute tools with tenant context and verify structured outputs, redacted summaries, and policy decisions without contacting external providers.

**Acceptance Scenarios**:

1. **Given** an installed skill version with an allowed read-only calendar tool, **When** a graph role node requests today's events in mock mode, **Then** the gateway returns normalized event records, records a redacted summary, and exposes no raw secret values.
2. **Given** a Gmail read request with allowed credential metadata and outbound domain, **When** the adapter executes, **Then** the gateway returns normalized message summaries and persists only safe summaries.
3. **Given** a request for an unsupported or uninstalled tool, **When** the gateway evaluates the call, **Then** execution is denied before adapter invocation with an auditable policy reason.

---

### User Story 2 - Enforce Credentials, Outbound Policy, And Side-Effect Blocks (Priority: P2)

Administrators and runtime operators can trust that skill tool execution fails closed when credential references are missing, tenant mismatched, domains are blocked, or side effects are requested.

**Why this priority**: Connector execution expands the security perimeter and must preserve tenant isolation and secret hygiene.

**Independent Test**: Run denied credential, blocked outbound, cross-tenant, and side-effect cases and verify no adapter call occurs, no provider payload is recorded, and the audit summary explains the denial.

**Acceptance Scenarios**:

1. **Given** a calendar request with no delegated credential metadata, **When** the gateway evaluates the request, **Then** it denies execution and records a credential-required decision.
2. **Given** a news request for a blocked outbound domain, **When** the gateway evaluates outbound policy, **Then** it denies execution before network or fixture provider selection.
3. **Given** a write-capable side-effect request, **When** policy does not explicitly allow side effects, **Then** execution is blocked by default.

---

### User Story 3 - Diagnose Skill Execution From The Admin Console (Priority: P3)

Platform admins can inspect skill tool readiness and run safe mock diagnostics for Daily Briefing connectors from a server-rendered admin page.

**Why this priority**: Operators need browser-visible evidence that connector readiness, policy decisions, and redaction behavior work before enabling staging probes.

**Independent Test**: Log in as a local platform admin, open the Skill Tool Diagnostics page, run mock diagnostic rows, and capture screenshots showing connector readiness and redacted summaries.

**Acceptance Scenarios**:

1. **Given** a platform admin session, **When** the admin opens `/admin/skill-execution/ui/diagnostics`, **Then** the page lists calendar, Gmail, news, weather, and commute tools with mode, policy status, and latest safe summaries.
2. **Given** mock fixture mode, **When** the admin runs diagnostics, **Then** each connector displays a structured preview without raw credential values.
3. **Given** an unauthenticated request, **When** the diagnostics page is opened directly, **Then** the existing admin authorization flow protects the route.

### Edge Cases

- Tenant ID on the tool request does not match the credential reference tenant.
- Skill package version is installed but does not expose the requested tool name.
- Adapter fixture is missing or malformed.
- Adapter exceeds the configured timeout.
- Provider response contains emails, access tokens, URLs with sensitive query parameters, or long raw text.
- Live-probe mode is requested in local environment.
- Outbound policy allows the provider domain but the tool policy denies the specific operation.
- Tool response is valid but does not satisfy the workflow contract schema.

## Requirements

### Functional Requirements

- **FR-001**: System MUST expose a SkillExecutionGateway boundary that accepts typed tool execution requests with tenant, actor, workflow run, role node, skill package version, tool name, execution mode, and contract metadata.
- **FR-002**: System MUST support first-party read-only adapters for `google_calendar.events.read`, `gmail.messages.read`, `news.search`, `weather.forecast.read`, and `commute.lookup`.
- **FR-003**: System MUST evaluate skill installation/version eligibility before adapter invocation.
- **FR-004**: System MUST evaluate model-skill tool policy before adapter invocation.
- **FR-005**: System MUST evaluate outbound allowlist policy before adapter invocation.
- **FR-006**: System MUST resolve only delegated credential metadata or secret-reference identifiers and MUST NOT materialize or persist raw secret values in gateway summaries.
- **FR-007**: System MUST block unsafe side effects by default unless an explicit policy allows the exact side-effecting operation.
- **FR-008**: System MUST support mock fixture execution for local QA without external provider calls.
- **FR-009**: System MUST support approved live probes for staging only when environment, policy, credential reference, and outbound allowlist checks all pass.
- **FR-010**: System MUST return structured outputs matching workflow contract expectations for calendar events, Gmail messages, news items, weather forecast, and commute conditions.
- **FR-011**: System MUST persist redacted request summaries, response summaries, execution status, adapter identity, latency, and policy decision metadata.
- **FR-012**: System MUST store large or raw provider evidence outside inline database/audit payloads and reference it only through artifact metadata when explicitly allowed.
- **FR-013**: System MUST expose an admin diagnostics page for safe connector readiness and mock execution evidence.
- **FR-014**: System MUST provide API contracts and tests for successful mock calls, denied credentials, blocked outbound domains, tenant isolation, and no raw secret leakage.
- **FR-015**: System MUST integrate with graph role-node execution so runtime nodes can request approved skill tools through the gateway rather than calling adapters directly.

### Key Entities

- **SkillToolExecutionRequest**: Tenant-scoped request to execute a named installed skill tool in mock or live-probe mode.
- **SkillToolExecutionResult**: Contract-shaped result with status, safe output payload, redacted summaries, policy decisions, and optional artifact references.
- **SkillToolAdapter**: Runtime implementation for one read-only tool family with declared operation identity, required credential kind, outbound domains, and fixture support.
- **CredentialResolutionSummary**: Redacted proof that a delegated credential or secret reference exists for the tenant without exposing the underlying value.
- **ToolPolicyDecision**: Allow or deny record for skill installation, tool policy, outbound policy, side-effect policy, and environment mode.
- **SkillToolDiagnosticRecord**: Admin-facing projection of connector readiness, last mock result, and last denial reason.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All five Daily Briefing tool adapters return contract-valid mock outputs in automated tests without external network calls.
- **SC-002**: Denied credential, blocked outbound, cross-tenant, uninstalled tool, and side-effect cases prevent adapter invocation in automated tests.
- **SC-003**: Redaction tests verify no access-token-like values, secret references with values, raw email bodies, or sensitive URL query strings appear in persisted summaries.
- **SC-004**: Admin diagnostics page is reachable through local-principal login and displays all five tool families with redacted mock evidence.
- **SC-005**: Quality gates pass with `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and the project coverage command.

## Assumptions

- Existing skill registry, model-skill configuration, delegated credential metadata, audit/redaction helpers, reliability controls, and admin shell are reused.
- This feature introduces read-only runtime adapters and mock/live-probe boundaries, not full production OAuth onboarding flows.
- Local QA never requires real Google, Gmail, news, weather, or traffic credentials.
- Live probes are for staging-style validation and use references to credentials managed outside workflow definitions.
- PostgreSQL remains the system of record for execution metadata; artifact storage is used only for oversized evidence references.

## Constitution Impact

- **Durable By Default**: Gateway records execution status, policy decisions, and safe summaries so runs can resume or explain prior tool outcomes.
- **Immutable State And Memory**: Execution summaries are append-only evidence records; adapter outputs do not mutate shared memory directly.
- **Contract-First Agent Coordination**: Each adapter returns explicit contract-shaped outputs used by workflow graph nodes.
- **Security With Practical Development Ergonomics**: Local QA uses deterministic mock fixtures while preserving authorization, tenant context, policy checks, and redaction.
- **Operability Is A Product Requirement**: Gateway metrics, safe audit summaries, and admin diagnostics are in scope.
- **Tenant Isolation And Fair Scheduling**: Every request carries tenant context and denies cross-tenant credential metadata.
- **Version-Pinned Execution**: Requests include skill package/version and policy identifiers for runtime provenance.
- **Secret Hygiene And Controlled Tool Access**: Raw secrets are not resolved into persisted payloads; outbound and tool access are policy controlled.
- **Tiered Storage For Large Payloads**: Raw provider payloads are not stored inline; oversized evidence uses artifact references only when allowed.

## Testing Instructions

- Run targeted unit tests for the skill execution gateway, adapters, redaction, and diagnostics.
- Run contract tests for the skill execution API surface and workflow runtime integration.
- Run integration tests for the admin diagnostics route through local-principal authentication.
- Run the generated QA validation plan and capture Playwright screenshots.

## PR Review Guidance

- Confirm adapter implementations cannot bypass gateway policy checks.
- Verify denied requests happen before credential resolution that would expose raw secrets or contact a provider.
- Inspect persisted summaries for secret, email body, and sensitive URL leakage.
- Confirm mock mode is deterministic and live-probe mode is gated by environment plus policy.
- Confirm graph runtime integration depends on typed gateway contracts, not direct adapter imports.

## Documentation Impact

- Add feature quickstart and QA guide under `specs/021-real-skill-tool-execution-connectors/`.
- Update platform docs with the SkillExecutionGateway boundary, Daily Briefing connector contracts, diagnostics route, and local QA workflow.
- Update README and quickstart references if validation commands or admin navigation change.
