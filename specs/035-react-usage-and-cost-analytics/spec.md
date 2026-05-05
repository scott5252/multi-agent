# Feature Specification: React Usage And Cost Analytics

**Feature Branch**: `codex/035-react-usage-and-cost-analytics`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for React Usage and Cost Analytics. Platform admins and tenant admins need modern dashboards to understand token usage, model cost estimates, confirmed versus estimated usage, latency, unavailable usage, provider/model/workflow/agent/prompt rollups, graph node attribution, gateway operation attempts, physical attempts, governed tool attribution, event drilldowns, and audited CSV exports. The UI must be understandable for non-technical admins, must respect platform versus tenant visibility, and must never expose raw prompts, completions, secrets, memory content, provider credentials, credential reference internals, raw tool payloads, or unauthorized run content."

## Clarifications

### Session 2026-05-05

- Q: What default date range should the dashboard use? A: Use the last 7 days by default, with administrators able to review safe backend-provided range options. (autopilot)
- Q: What grouping should appear first? A: Use daily grouping first, then allow backend-owned grouping options for provider, model, workflow, agent, prompt, graph node, gateway operation, physical attempt, and governed tool attribution. (autopilot)
- Q: Which primary views should the page include? A: Show summary cards, a trend view, a rollup table, and a bounded event drilldown as the primary experience. (autopilot)
- Q: How should confirmed versus estimated usage be shown? A: Use clear confirmed, estimated, partial, and unavailable badges on cards, trend buckets, rollups, drilldowns, and exports. (autopilot)
- Q: How should exports behave? A: Export the active safe filter snapshot, return status and audit evidence, and never export unauthorized rows or unsafe raw content. (autopilot)
- Q: What can tenant administrators see? A: Tenant administrators see only their active tenant's dashboard, rollups, events, exports, and audit summaries. (autopilot)
- Q: What cost precision should reviewers see? A: Use backend-owned currency formatting with enough decimal precision to distinguish small model costs while keeping non-technical summaries readable. (autopilot)
- Q: What happens when no data or partial data exists? A: Show empty, partial, unavailable, and denied states with safe explanation and next action guidance. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Usage And Cost Health (Priority: P1)

Platform and tenant administrators need a clear dashboard that explains recent token usage, cost estimates, latency, confirmed versus estimated status, and unavailable usage without requiring them to understand provider internals.

**Why this priority**: Usage and cost visibility is the primary value of the feature; administrators must be able to identify spend and data-quality issues before exports or deeper drilldowns matter.

**Independent Test**: Sign in as a platform administrator and as an Acme tenant administrator, open the usage analytics workspace, and verify each scope shows summary cards, a daily trend, rollups, confidence badges, latency, unavailable usage, and safe explanatory copy.

**Acceptance Scenarios**:

1. **Given** usage records exist for multiple providers, models, workflows, agents, prompts, graph nodes, and governed tools, **When** a platform administrator opens the dashboard, **Then** they see platform-wide totals, cost estimates, latency, unavailable usage, and confidence labels for the selected date range.
2. **Given** Acme and Globex usage records exist, **When** an Acme tenant administrator opens the dashboard, **Then** they see only Acme totals and no Globex rows, labels, event references, or export links.
3. **Given** some usage records are estimated while others are confirmed, **When** the administrator reviews totals and trends, **Then** the dashboard labels estimated and confirmed amounts separately and explains the safe meaning of each label.
4. **Given** usage data is delayed or partially unavailable, **When** the administrator opens the dashboard, **Then** the page shows partial-data states, last-known safe totals, and unavailable usage counts without exposing raw run payloads.

---

### User Story 2 - Compare Rollups And Attribution (Priority: P2)

Administrators need to compare usage and cost by provider, model, workflow, agent, prompt, graph node, gateway operation, physical attempt, and governed tool attribution so they can find the source of cost or latency changes.

**Why this priority**: Rollups turn aggregate numbers into actionable operational decisions, especially for tenant support, gateway tuning, and workflow optimization.

**Independent Test**: Use the default dashboard filters, switch grouping dimensions, and verify each rollup table updates with safe labels, totals, latency, unavailable usage, attribution summaries, and bounded row counts.

**Acceptance Scenarios**:

1. **Given** the default last-seven-day range is selected, **When** an administrator chooses a provider or model grouping, **Then** the rollup table shows token totals, cost estimates, request counts, latency, unavailable usage, and confidence status by safe provider/model label.
2. **Given** a workflow graph run generated usage across multiple nodes, **When** the administrator switches to graph node attribution, **Then** the dashboard shows safe node labels and usage totals without raw node input, prompt, completion, or memory content.
3. **Given** gateway operations include logical and physical attempts, **When** the administrator reviews gateway attribution, **Then** the dashboard distinguishes gateway operations from physical attempts and shows retry/attempt summaries safely.
4. **Given** governed tool execution contributes cost or latency evidence, **When** the administrator reviews tool attribution, **Then** the dashboard shows connector/tool safe summaries without raw tool request or response payloads.

---

### User Story 3 - Drill Down And Export Evidence (Priority: P3)

Administrators need bounded event drilldowns and audited CSV exports for safe reviewer evidence, tenant support, and cost review handoffs.

**Why this priority**: Drilldowns and exports support investigation and governance after the dashboard and rollups identify a question.

**Independent Test**: Open the event drilldown from a rollup row, verify safe event details, create an export for the active filter snapshot, and confirm export status plus audit evidence are visible without unsafe data.

**Acceptance Scenarios**:

1. **Given** a rollup row has related usage events, **When** an administrator opens the drilldown, **Then** they see bounded safe event rows with timestamps, status, provider/model/workflow/agent/prompt labels, attempts, latency, usage amounts, cost estimates, and audit references.
2. **Given** the active filters include date range, tenant scope, group dimension, confidence status, and provider/model filters, **When** an administrator creates a CSV export, **Then** the export captures that safe filter snapshot and returns an audited export reference.
3. **Given** a tenant administrator requests an export, **When** the export is created, **Then** the export includes only tenant-authorized rows and records safe audit evidence for the request.
4. **Given** export generation is unavailable, **When** an administrator requests an export, **Then** the UI shows a safe unavailable state and no raw data is rendered or written to reviewer evidence.

### Edge Cases

- Usage exists for a provider but pricing metadata is missing or stale.
- A provider reports token counts but not cost estimates.
- A model gateway operation has multiple physical attempts with mixed success and failure.
- Usage records reference a workflow, agent, prompt, or graph node that has since been archived.
- Usage is attributed to a governed tool but the connector is no longer installed.
- A tenant administrator attempts to open a platform-wide or other-tenant rollup.
- A selected date range has no usage records.
- Export generation succeeds but artifact retrieval is delayed.
- Audit persistence is unavailable when an export or drilldown action is requested.
- A usage event has safe metadata but its underlying run content is not authorized for the viewer.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a protected usage analytics workspace for platform administrators and tenant administrators.
- **FR-002**: The system MUST default analytics to the last 7 days with daily grouping.
- **FR-003**: The system MUST provide backend-owned filter metadata for date range, grouping dimension, tenant scope, provider, model, workflow, agent, prompt, confidence status, and usage availability.
- **FR-004**: The system MUST show summary cards for token usage, cost estimate, request/event count, latency, unavailable usage, and confirmed versus estimated coverage.
- **FR-005**: The system MUST show a trend view that separates confirmed usage, estimated usage, cost estimates, latency, and unavailable usage.
- **FR-006**: The system MUST show rollups by provider, model, workflow, agent, sub-agent, prompt, execution mode, principal, graph node, gateway operation, physical attempt, and governed tool attribution.
- **FR-007**: The system MUST show safe labels and summaries for all rollup rows instead of raw prompts, completions, memory content, tool payloads, credential internals, or unauthorized run data.
- **FR-008**: The system MUST distinguish model gateway operations from physical provider attempts and explain retry/attempt attribution.
- **FR-009**: The system MUST label usage and cost values as confirmed, estimated, partial, or unavailable using backend-owned confidence status.
- **FR-010**: The system MUST provide bounded event drilldowns with safe event summaries, timestamps, usage amounts, latency, provider/model labels, workflow/agent/prompt labels, attempt summaries, and audit references.
- **FR-011**: The system MUST provide audited CSV export creation for the active safe filter snapshot.
- **FR-012**: Export summaries MUST show export status, requested filters, safe artifact references, requester, tenant scope, row count, and audit reference.
- **FR-013**: Platform administrators MUST be able to review authorized platform-wide and tenant-specific usage analytics.
- **FR-014**: Tenant administrators MUST see only their active tenant's usage, rollups, events, exports, and audit summaries.
- **FR-015**: Cross-tenant and platform-only requests from tenant administrators MUST fail closed with safe denial messaging and audit evidence.
- **FR-016**: If usage data, pricing metadata, export generation, or audit persistence is unavailable, the workspace MUST show safe partial, empty, denied, or dependency-unavailable states.
- **FR-017**: The workspace MUST be validated in both Auth0-backed production-style principal mode and `AUTH_MODE=local_principal` mode.
- **FR-018**: QA guides, screenshots, JSON evidence, and exports MUST exclude raw prompts, completions, secrets, memory content, provider credentials, credential reference internals, raw tool payloads, unauthorized run content, local filesystem paths, and fake QA secret values.
- **FR-019**: The workspace MUST preserve existing server-rendered usage analytics fallbacks until React migration parity is explicitly proven by a later spec.

### Key Entities

- **Usage Dashboard**: Scope-aware analytics page data containing summary cards, filters, trend points, rollups, drilldown previews, export metadata, and safe states.
- **Usage Summary Card**: A metric tile containing a label, value, unit, confidence status, comparison summary, and safe explanation.
- **Usage Trend Point**: A date-bucketed usage/cost/latency record with confirmed, estimated, and unavailable portions.
- **Usage Rollup Row**: A grouped usage summary by provider, model, workflow, agent, prompt, graph node, gateway operation, physical attempt, or governed tool.
- **Usage Event Drilldown Row**: A bounded event-level summary for reviewer investigation with safe labels, token/cost/latency values, attempt status, and audit reference.
- **Usage Export Request**: An audited request to create a CSV artifact from the active safe filter snapshot.
- **Usage Export Summary**: Export status and safe artifact metadata for a reviewer or administrator.
- **Usage Filter Metadata**: Backend-owned filter options, selected defaults, disabled reasons, and scope-aware visibility controls.
- **Usage Confidence Status**: Confirmed, estimated, partial, or unavailable status applied to metrics and rows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A platform administrator can identify total tokens, estimated cost, latency, unavailable usage, and confirmed-versus-estimated coverage for the default range in under 60 seconds.
- **SC-002**: A tenant administrator can complete the same review for their tenant without seeing another tenant's usage data.
- **SC-003**: Administrators can switch among at least six supported grouping dimensions and understand each rollup without raw identifiers or unsafe payloads.
- **SC-004**: Event drilldowns display no more than the bounded result size defined by the feature plan while still showing enough safe detail to investigate the selected rollup.
- **SC-005**: CSV export creation returns a status and audit reference for the active filter snapshot without exposing unauthorized rows.
- **SC-006**: Empty, partial, denied, and dependency-unavailable states are visible and actionable in local QA.
- **SC-007**: Automated validation proves both Auth0-shaped principal routing and local-principal browser login for the protected React usage routes.
- **SC-008**: Redaction scans over QA JSON evidence, screenshots, and export metadata find no fake secret values or unsafe raw content markers.

## Assumptions

- The first React analytics workspace uses the same usage and pricing semantics established by Spec 016.
- Usage analytics are read-mostly; export creation is the only mutation in scope.
- The default dashboard range is the last 7 days with daily grouping.
- Platform administrators can intentionally review authorized cross-tenant rollups.
- Tenant administrators are limited to their active tenant scope.
- Cost values may be estimated when pricing metadata or provider confirmation is incomplete.
- Drilldowns and exports prioritize safe metadata over raw event payloads.
- Existing server-rendered usage pages remain available as fallbacks until Spec 037.
- Local QA uses deterministic fixtures and does not call live providers.
