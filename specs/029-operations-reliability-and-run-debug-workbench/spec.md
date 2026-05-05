# Feature Specification: Operations, Reliability, And Run Debug Workbench

**Feature Branch**: `codex/029-operations-reliability-and-run-debug-workbench`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Create a feature specification for a React operations, reliability, and run debug workbench. Platform operators need one intuitive workspace to understand health, dependencies, capacity, queue pressure, database pool pressure, model provider health, Telegram/channel status, workflow graph execution state, parallel branches, join decisions, per-node run steps, governed tool calls, connector readiness, Telegram alias routing and delivery attempts, ModelGateway operations, live credential diagnostic categories, reliability breaker state, retries, dead letters, latency, throughput, error rate, redacted logs, run timelines, lineage, replay links, and safe exports. Tenant admins may see only explicitly authorized tenant-scoped views. The experience must guide non-technical admins from symptom to likely cause without raw data exposure."

## Clarifications

### Session 2026-05-04

- Q: Which roles can see platform-wide operations and reliability data? -> A: Platform administrators and auditors can see platform-wide summaries; tenant administrators see only tenant-scoped views where existing policies explicitly authorize them (autopilot).
- Q: What default time range should the workbench use? -> A: Default to the last 60 minutes, with backend-approved time range filters that match existing operations, reliability, provider, usage, and run-inspection patterns (autopilot).
- Q: How should refresh behavior work? -> A: Use manual refresh for the whole workbench plus safe short polling only for health and pressure panels that already have safe aggregate summaries (autopilot).
- Q: How dense should charts and tables be for non-technical admins? -> A: Use dense, scan-friendly tables and compact trend cards, but pair degraded states with plain-language likely-cause guidance and clear next destinations (autopilot).
- Q: How should logs be filtered and displayed? -> A: Use backend-owned filters for severity, subsystem, time range, tenant scope, run reference, and correlation reference; display redacted summaries only, never raw log lines or stack traces (autopilot).
- Q: Which cross-links should the workbench expose? -> A: Link to existing authorized run inspection, reliability, operations, provider, usage, Telegram/channel, skill tool diagnostics, audit/debugging, and Jinja fallback destinations until React parity is complete (autopilot).
- Q: How should workbench exports behave? -> A: Use safe export snapshots with artifact references, scope, expiry, redaction summary, and audit reference metadata; do not stream raw evidence into the React page (autopilot).
- Q: How should degraded or unavailable dependencies appear? -> A: Render degraded cards and partial-data states with freshness, affected section, likely cause category, and remediation link rather than hiding the section (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Triage Platform Health And Pressure (Priority: P1)

Platform operators can open one operations workbench that summarizes platform health, dependency readiness, capacity, queue pressure, database pool pressure, provider health, channel status, connector readiness, latency, throughput, error rate, breaker posture, and redacted operational signals. The workspace guides the operator from a visible symptom to the most likely affected subsystem and recommended next safe destination.

**Why this priority**: Operators need a single reliable first stop during incidents or reviews before drilling into run-specific or queue-specific details.

**Independent Test**: Open the workbench as a platform operator, verify platform-wide cards and guided cause summaries render with safe links, then verify unauthorized users and tenant-only principals cannot see platform-only data.

**Acceptance Scenarios**:

1. **Given** a platform operator with authorized access, **When** they open the workbench, **Then** the page shows health, dependencies, capacity, queue pressure, database pressure, model provider health, channel status, connector readiness, reliability state, and safe trend summaries.
2. **Given** a platform operator sees a degraded dependency, **When** they inspect the guided summary, **Then** the page explains the affected subsystem, likely cause category, severity, freshness, and safe next action without exposing raw logs or credentials.
3. **Given** an unauthenticated request, **When** it opens the workbench route or data endpoint, **Then** the request fails closed without rendering health, queue, provider, channel, or run data.
4. **Given** a tenant administrator without platform scope, **When** they open the platform workbench view, **Then** platform-only summaries are hidden or denied while explicitly authorized tenant-scoped status remains available.

---

### User Story 2 - Debug Runs, Graphs, Tools, And Deliveries (Priority: P2)

Authorized administrators can inspect a run-centric debug view that connects workflow graph state, parallel branches, join decisions, run steps, lineage, replay links, governed tool calls, connector readiness, ModelGateway operations, credential diagnostic categories, Telegram alias routing, and delivery attempts into a safe timeline.

**Why this priority**: Run failures are difficult for non-technical admins to understand when graph, model, tool, delivery, and reliability evidence is split across several pages.

**Independent Test**: Load a deterministic run debug fixture as a platform operator and as a tenant admin for the owning tenant, then verify timeline, graph branch, join, tool, gateway, delivery, lineage, and replay summaries appear only when authorized and never expose raw prompts, completions, provider responses, tool payloads, or private messages.

**Acceptance Scenarios**:

1. **Given** an authorized operator reviews a failed run, **When** they open the run debug workbench, **Then** the page shows a chronological timeline with steps, graph nodes, branch states, join decisions, handoffs, retries, tool calls, gateway attempts, delivery attempts, and safe evidence references.
2. **Given** a run includes parallel branches, **When** the operator reviews branch state, **Then** the page distinguishes completed, waiting, failed, joined, and manually paused branches with safe reasons and next actions.
3. **Given** a run includes governed tool calls and model gateway attempts, **When** the operator expands diagnostics, **Then** the page shows connector readiness, policy outcome, provider health, credential diagnostic category, retry category, and redacted attempt evidence without raw external payloads.
4. **Given** a tenant admin requests a run outside their tenant, **When** they open the run debug view, **Then** the response is denied and does not reveal the other tenant name, run title, timeline, delivery identity, or provider details.

---

### User Story 3 - Recover, Export, And Hand Off Safely (Priority: P3)

Operators can review reliability controls, retries, dead letters, replay links, compensation state, and safe exports from the same workbench so they can recover from known issues or hand off evidence without leaking protected data.

**Why this priority**: Recovery workflows and evidence handoffs must be safe and consistent before operators use the React workbench during real incidents.

**Independent Test**: Use deterministic reliability fixtures to review breaker state, retry schedules, dead letters, replay links, and export snapshots, then verify safe confirmation, export artifact references, tenant isolation, and redaction behavior.

**Acceptance Scenarios**:

1. **Given** a breaker is open or half-open, **When** an operator reviews reliability controls, **Then** the workbench shows safe status, impacted domain, cooldown, recent error category, allowed next actions, and audit reference metadata.
2. **Given** retries or dead letters exist, **When** an operator inspects recovery queues, **Then** the page shows bounded counts, age, reason category, safe destination links, and confirmation requirements for any replay-oriented action.
3. **Given** an operator requests an export, **When** the backend prepares evidence, **Then** the page displays a safe export snapshot with artifact reference, expiry, scope, redaction summary, and audit reference without local filesystem paths or raw payload content.
4. **Given** the workbench data is partially unavailable, **When** the page renders, **Then** it shows partial-data state, stale timestamp, affected section, and safe remediation without hiding still-available authorized data.

### Edge Cases

- A dependency probe is stale while other sections are fresh.
- Queue pressure is high but worker capacity data is unavailable.
- Database pool pressure is unavailable or partially sampled.
- A model provider is unhealthy while local providers remain available.
- A Telegram/channel delivery attempt is missing safe destination metadata.
- A connector readiness summary is denied by policy.
- A run graph has parallel branches with mixed success, failure, and waiting states.
- A join decision is manual, timed out, or blocked by a failed branch.
- A run step references a side-effect intent that is pending approval.
- A governed tool call is blocked by tenant, tool, outbound, credential, or side-effect policy.
- A ModelGateway attempt has an invalid secret reference category.
- A retry schedule references a dead-lettered item.
- A replay link is expired or unauthorized.
- A log excerpt has no safe summary.
- A safe export is requested for a cross-tenant or unauthorized scope.
- A tenant admin requests platform-only dependency, provider, or queue summaries.
- Auth0-shaped principal tests and local-principal browser flows produce different authorization results.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workbench MUST provide a protected operations route and data contract that can be requested only after existing authentication, role, scope, and tenant checks pass.
- **FR-002**: The workbench MUST show platform-wide health, dependency readiness, capacity, queue pressure, database pool pressure, model provider health, channel status, connector readiness, latency, throughput, error-rate, and reliability summaries to authorized platform operators.
- **FR-003**: The workbench MUST provide tenant-scoped status views only for explicitly authorized tenant administrators and MUST hide or deny platform-only summaries for tenant-only principals.
- **FR-004**: The workbench MUST guide non-technical admins from each degraded symptom to a safe likely-cause category, affected subsystem, freshness timestamp, severity, and next destination.
- **FR-005**: The workbench MUST default to a last-60-minutes view and MUST expose only backend-approved time range filters.
- **FR-006**: The workbench MUST support manual full-page refresh and safe short polling for health and pressure panels that already have redacted aggregate summaries.
- **FR-007**: Workbench tables and trend cards MUST remain scan-friendly for repeated operations use while degraded states include plain-language likely-cause guidance.
- **FR-008**: Log and evidence filters MUST be backend-owned and MUST include only safe severity, subsystem, time range, tenant scope, run reference, and correlation reference options.
- **FR-009**: Run debug views MUST summarize workflow graph execution state, branch state, join decisions, run steps, handoffs, approvals, timeline events, lineage, replay links, and manual pause states using safe labels.
- **FR-010**: Run debug views MUST summarize governed tool calls, connector readiness, policy outcomes, side-effect disposition, and external-tool result categories without exposing raw tool payloads.
- **FR-011**: Run debug views MUST summarize ModelGateway operations, provider attempt categories, live credential diagnostic categories, retry/breaker categories, usage linkage, and redacted attempt evidence without exposing provider authorization headers, raw prompts, raw completions, or raw provider responses.
- **FR-012**: Channel diagnostics MUST summarize Telegram alias routing, linked identity status, webhook receipt state, notification attempts, delivery attempts, and safe failure categories without exposing private channel messages, raw update payloads, link tokens, or full external identifiers.
- **FR-013**: Reliability sections MUST show breaker state, retry schedules, quotas, leases, fairness/admission pressure, dead letters, compensation state, and safe replay/remediation links with confirmation metadata where an action could affect state.
- **FR-014**: Logs and evidence snippets MUST be redacted before reaching React and MUST show only safe summaries, categories, timestamps, correlation references, trace identifiers, and audit reference IDs.
- **FR-015**: Export flows MUST return safe export snapshots with artifact references, scope, redaction summary, expiry, progress/status, and audit reference metadata; they MUST NOT expose local filesystem paths or raw exported content.
- **FR-016**: Workbench contracts MUST use the shared React admin data/form patterns from Spec 028 for envelopes, states, filters, tables, actions, mutation results, confirmation prompts, and export snapshots.
- **FR-017**: The workbench MUST preserve existing Jinja operations, reliability, run inspection, provider, Telegram, skill tool diagnostics, and audit/debugging routes as fallbacks until React parity is proven by a later migration hardening spec.
- **FR-018**: The feature MUST include Auth0-backed route tests for principal and scope behavior and local-principal Playwright flows for browser login, platform view, tenant view, denied view, run debug view, and safe export behavior.
- **FR-019**: The feature MUST include redaction tests proving secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, private channel messages, raw Telegram updates, raw external tool payloads, raw provider responses, stack traces, local filesystem paths, and unauthorized tenant labels do not reach workbench contracts or screenshots.

### Key Entities *(include if feature involves data)*

- **Operations Workbench Envelope**: Authorized page contract containing scope, freshness, summary cards, degraded symptoms, likely-cause guidance, filters, actions, and evidence references.
- **Health And Pressure Summary**: Safe summary of health, dependency readiness, capacity, queues, database pressure, provider state, channel status, connector readiness, throughput, latency, and error-rate signals.
- **Run Debug Timeline**: Ordered safe view of run steps, graph nodes, branch outcomes, join decisions, handoffs, approvals, retries, tool calls, gateway attempts, deliveries, and lineage references.
- **Graph Branch Summary**: Safe branch and join state for parallel workflow execution, including waiting, completed, failed, joined, paused, and manual-resolution categories.
- **Gateway Attempt Summary**: Safe provider/model attempt metadata, retry category, breaker category, credential diagnostic category, usage linkage, and redacted evidence reference.
- **Tool Call Summary**: Safe governed tool execution metadata, connector readiness, policy outcome, side-effect classification, and normalized result category.
- **Channel Delivery Summary**: Safe Telegram/channel alias, receipt, notification, and delivery attempt metadata with private identifiers redacted.
- **Reliability Recovery Summary**: Safe breaker, retry, quota, lease, dead-letter, compensation, replay, and confirmation metadata.
- **Workbench Export Snapshot**: Safe artifact reference and audit metadata for exported workbench evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authorized platform operators can identify the highest-severity degraded subsystem and at least one safe next destination from the workbench in under 60 seconds using deterministic QA fixtures.
- **SC-002**: 100% of unauthorized and cross-tenant workbench, run debug, action, and export requests fail closed without leaking protected tenant labels, run titles, delivery identities, provider details, or raw evidence.
- **SC-003**: Deterministic run debug evidence displays graph branch state, join decisions, run steps, governed tool calls, ModelGateway attempts, Telegram/channel delivery attempts, lineage, replay links, and safe audit references in one page.
- **SC-004**: Reliability fixture tests cover open breaker, retry, dead-letter, replay confirmation, partial-data, and export snapshot states.
- **SC-005**: Redaction tests prove no raw secrets, credential values, prompts, completions, memory contents, private channel messages, raw provider responses, raw Telegram updates, raw tool payloads, stack traces, local paths, or unauthorized tenant labels appear in API responses or Playwright screenshots.
- **SC-006**: Required QA docs, full Spec QA, backend quality gates, frontend quality gates, generated contract checks, and Playwright validation pass before Spec 030 begins.

## Assumptions

- The workbench is additive and does not retire existing Jinja operations, reliability, run inspection, provider, Telegram, tool diagnostics, or audit/debugging pages.
- Deterministic QA fixtures can summarize existing operational domains without calling real providers, Telegram, credential stores, or external tools.
- Platform operators may see platform-wide summaries; tenant admins may see only explicitly authorized tenant-scoped summaries and run evidence.
- Existing backend repositories and services remain authoritative for health, reliability, runtime, provider, channel, gateway, tool, audit, and usage data.
- Safe export flows return artifact references and redaction summaries, not raw exported contents.
