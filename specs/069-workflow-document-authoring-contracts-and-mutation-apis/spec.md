# Feature Specification: Workflow Document Authoring Contracts And Mutation APIs

**Feature Branch**: `codex/069-workflow-document-authoring-contracts-and-mutation-apis`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Workflow Document Authoring Contracts And Mutation APIs. The backend workflow registry already stores full WorkflowDraftDocument records, but the React workflow builder save route only persists limited metadata. Authorized admins need browser-facing JSON contracts and mutation endpoints that allow safe creation and editing of full workflow documents, including roles, prompt/profile references, skill references, contracts, nodes, edges, join policies, approval gates, subworkflow references, test requirements, and editor annotations."

## Clarifications

### Session 2026-05-09

- Q: Should Spec 069 prioritize full document saves, patch-style section mutations, or both? -> A: Full document save is required first; section patches are optional only when they reuse identical backend validation, revision, idempotency, authorization, and audit behavior. (autopilot)
- Q: Should workflow document saves carry raw prompt template bodies for agent bindings? -> A: No. Spec 069 stores prompt/profile references only; raw prompt text remains limited to authorized prompt editing surfaces. (autopilot)
- Q: What scope should idempotency keys use? -> A: Idempotency is scoped to tenant, principal, draft, revision intent, route family, and request payload hash so key reuse with a different target or payload is rejected. (autopilot)
- Q: How should stale browser saves recover? -> A: Reject stale saves without mutation and return current safe revision context plus section-level recovery hints; browser-side automatic merge is out of scope for Spec 069. (autopilot)
- Q: Where should the React-facing mutation contract live? -> A: Extend the existing React Admin workflow builder/admin JSON route family and generated Pydantic-to-TypeScript contract flow instead of adding a second admin app or raw JSON editor. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save Complete Workflow Documents (Priority: P1)

An authorized tenant admin editing a workflow draft can save a complete workflow document from the browser, including metadata, roles, prompt/profile references, skill references, contracts, graph nodes and edges, join policies, approval gates, subworkflow references, test requirements, and editor annotations.

**Why this priority**: This is the enabling contract for every later workflow setup UI. Without a browser-facing full document save, later graph, prompt/profile, and evidence controls would still lose data or require raw API calls.

**Independent Test**: Create a workflow draft through the React-facing workflow route, submit a complete safe document payload, reload the draft, and verify every supported section round-trips from the stored draft document.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin and an existing draft revision token, **When** the admin saves a complete workflow document with valid roles, contracts, graph topology, joins, prompts, profiles, skills, approval gates, subworkflows, required tests, and annotations, **Then** the system persists the complete document and returns the next safe editor state with an updated revision token.
2. **Given** a valid saved document with multiple sections, **When** the admin reloads the React workflow builder, **Then** the React-facing draft detail response includes each editable section and safe section summary needed to keep the browser state consistent.
3. **Given** an authorized platform admin editing a platform-scoped workflow, **When** the admin saves a platform-scoped document, **Then** the system accepts only scope-compatible references and records an audit summary that does not expose raw prompt text, secrets, provider payloads, or private runtime data.

---

### User Story 2 - Recover From Stale Or Conflicting Saves (Priority: P2)

An authorized admin who saves from an outdated browser tab receives a stale conflict response with safe recovery details instead of overwriting newer workflow draft changes.

**Why this priority**: Full document editing increases concurrent edit risk. Revision tokens and clear conflict recovery are required before later UI controls encourage multi-section editing.

**Independent Test**: Save a draft twice from the same base revision, then verify the second save is rejected as stale and includes the current revision token plus safe section-level conflict guidance.

**Acceptance Scenarios**:

1. **Given** two browser sessions loaded at the same draft revision, **When** one session saves successfully and the second session submits its stale revision token, **Then** the stale save is rejected without mutating the draft and the response includes a safe recovery envelope.
2. **Given** a stale conflict response, **When** the browser displays recovery information, **Then** the response points to affected sections and fields without revealing raw secrets, raw prompts outside authorized edit fields, completions, provider payloads, stack traces, or unauthorized tenant labels.
3. **Given** an idempotency key for a previously successful save, **When** the same payload is submitted again by the same authorized principal in the same tenant scope, **Then** the system returns the prior safe mutation result without creating duplicate revisions or audit records.

---

### User Story 3 - Diagnose Invalid Workflow Document Sections (Priority: P3)

An authorized admin who submits an invalid document receives validation findings mapped to workflow setup sections and field paths that the React UI can use to focus the right editor control.

**Why this priority**: Later visual controls need backend-owned validation results that are specific enough to guide correction and safe enough to render in the browser.

**Independent Test**: Submit invalid documents with duplicate keys, missing graph references, scope mismatches, unsafe text, and oversized payloads, then verify safe findings map to stable sections and field paths.

**Acceptance Scenarios**:

1. **Given** a document with duplicate role, node, or edge keys, **When** the admin saves it, **Then** the save is rejected with section and field-path findings for the duplicates.
2. **Given** a document whose edges or role node references point to missing nodes, **When** the admin saves it, **Then** the save is rejected with graph findings that identify the missing references without persisting the invalid topology.
3. **Given** a document with tenant/platform scope mismatches or cross-tenant references, **When** the admin saves it, **Then** the save is rejected fail-closed and the response contains only authorized, redacted diagnostic summaries.

### Edge Cases

- Stale revision tokens must never overwrite a newer draft revision.
- Missing idempotency keys on mutating requests must produce a safe validation error or a documented mutation failure rather than an ambiguous write.
- Reused idempotency keys with a different payload must be rejected rather than replaying an unrelated prior mutation.
- Cross-tenant draft identifiers, prompt/profile references, skill installation references, subworkflow references, or test evidence references must fail closed.
- Tenant admins must not save platform-scoped workflow documents unless their principal is authorized for that scope.
- Platform admins must not accidentally convert tenant-owned drafts into platform-owned drafts through the React save contract.
- Duplicate role keys, node keys, edge keys, contract keys, join keys, skill binding keys, approval gate keys, and test requirement keys must be reported before persistence.
- Edge endpoints, role node references, join inbound references, approval gate references, and subworkflow aliases must point to valid document entries.
- Documents without an entry node or with no terminal path must receive validation findings that map to graph setup.
- Unsafe strings, raw secret-like values, private channel content, stack traces, or local filesystem paths in editable summaries must be rejected or redacted before response rendering, audit capture, exports, screenshots, or QA artifacts.
- Oversized documents or oversized sections must fail with a safe size finding and must not partially persist.
- Existing lower-level workflow APIs must continue to behave as supported while the React-facing route gains full document capabilities.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose React-facing workflow editor contracts that represent the complete editable workflow draft document and safe section summaries for metadata, roles, prompt/profile references, skill references, contracts, nodes, edges, joins, approval gates, subworkflows, required tests, and editor annotations.
- **FR-002**: The system MUST allow authorized admins to save a complete workflow draft document through a React-facing mutation using a revision token and idempotency key.
- **FR-002a**: The system MUST treat full document save as the required mutation contract for Spec 069 and MUST make any optional section patch behavior conform to the same backend validation, revision, idempotency, authorization, and audit guarantees.
- **FR-003**: The system MUST persist full document changes for all supported workflow sections rather than limiting React saves to display name and description.
- **FR-004**: The system MUST preserve existing lower-level workflow registry APIs and avoid breaking supported non-React workflow document save flows.
- **FR-005**: The system MUST validate submitted documents with backend-owned workflow registry validation before accepting a save.
- **FR-006**: The system MUST map validation findings to stable setup sections and field paths that the browser can use to focus the relevant editor area.
- **FR-007**: The system MUST reject stale revision tokens without mutating the draft and MUST return the current safe revision context for recovery.
- **FR-008**: The system MUST make repeated requests with the same idempotency key and same payload safe from duplicate revisions and duplicate audit summaries.
- **FR-009**: The system MUST reject idempotency key reuse when the associated request payload, principal, tenant scope, or draft target differs from the original mutation.
- **FR-009a**: The system MUST scope idempotency to tenant, principal, draft, revision intent, route family, and request payload hash.
- **FR-010**: The system MUST enforce tenant and platform scope rules for draft ownership, prompt/profile references, skill references, subworkflow references, and test evidence references.
- **FR-011**: The system MUST fail closed for cross-tenant draft saves and cross-tenant references.
- **FR-012**: The system MUST return redaction-safe problem details and mutation summaries that never include raw secrets, credential values, provider authorization headers, raw completions, memory contents, private messages, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-013**: The system MUST allow raw prompt text only in authorized prompt editing surfaces, not in general workflow save diagnostics, audit summaries, screenshots, exports, or validation problem details.
- **FR-014**: The system MUST capture audit summaries for successful and rejected workflow document mutation attempts using safe section names, changed-section counts, principal, tenant scope, draft identifiers, and validation outcome summaries.
- **FR-015**: The system MUST expose enough generated TypeScript contract information for the React workflow builder API client to type complete document editor load, save, conflict, and validation responses.
- **FR-016**: The system MUST document the React-facing mutation contract and the expected validation, stale conflict, idempotency, authorization, and redaction behavior.
- **FR-017**: The system MUST include deterministic local-principal QA coverage for authorized saves, stale conflicts, cross-tenant denials, invalid graph references, duplicate keys, unsafe strings, oversized documents, and generated TypeScript freshness.
- **FR-018**: The system MUST include curl regression coverage for any new or changed public/admin JSON route family introduced by this feature.

### Key Entities *(include if feature involves data)*

- **Workflow Document Editor State**: The safe browser contract for an editable draft, including the complete workflow draft document, section summaries, revision token, available references, validation status, and field-path metadata.
- **Workflow Document Save Request**: A mutation payload containing the target draft, revision token, idempotency key, complete document data, and optional client edit metadata.
- **Workflow Document Mutation Result**: A safe mutation response containing success or failure status, updated revision token when applicable, changed section summaries, validation findings, recovery guidance, and audit summary references.
- **Section Validation Finding**: A backend-owned diagnostic mapped to a setup section, field path, severity, code, message, and optional safe remediation hint.
- **Stale Conflict Recovery Envelope**: A safe response returned when submitted revision tokens are outdated, including current revision context and affected sections without exposing unauthorized data.
- **Mutation Audit Summary**: A redaction-safe audit record summary for accepted, rejected, stale, or denied document mutations.
- **Generated React Contract**: The generated TypeScript representation of the Pydantic contracts consumed by the React workflow builder API client.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized tenant admin can save and reload a complete workflow document through the React-facing API with all supported document sections preserved.
- **SC-002**: Stale save attempts are rejected 100 percent of the time in tests and never create a newer workflow draft revision.
- **SC-003**: Invalid workflow documents in focused tests return section and field-path findings for duplicate keys, missing graph references, missing entry node, scope mismatch, unsafe text, and oversized payloads.
- **SC-004**: Cross-tenant or unauthorized workflow document saves are denied in automated tests without exposing unauthorized tenant labels or raw document payloads.
- **SC-005**: Generated TypeScript contract freshness checks pass after the new React-facing schemas are added.
- **SC-006**: Focused backend, contract, frontend type, QA document, Playwright smoke, curl regression, ruff, format, mypy, and relevant pytest validation pass for Spec 069 before Spec 070 begins.
- **SC-007**: Documentation enables a reviewer to verify the save, stale conflict, validation mapping, redaction, and curl coverage without direct database editing or hand-configuring browser URLs.

## Assumptions

- The canonical persisted workflow draft document remains `WorkflowDraftDocument`; this feature adds safer React-facing editor contracts rather than creating a second workflow document model.
- Full document saves are the default mutation shape for Spec 069. Narrow section patch routes may be added only if needed for usability or idempotency, and must reuse the same validation, authorization, stale conflict, and audit guarantees.
- Existing workflow registry validation, reference validation, publish-gate checks, and audit helpers are reused where possible.
- Prompt/profile creation and rich per-agent binding UI are implemented in Spec 071; Spec 069 only provides document fields and contracts that can store prompt/profile references safely.
- Graph and role authoring controls are implemented in Spec 070; Spec 069 proves the React-facing route can round-trip complete role, node, edge, contract, join, and annotation changes.
- Test evidence setup UI is implemented in Spec 072; Spec 069 provides document support for required test requirements and safe validation mappings.
- Local QA uses `AUTH_MODE=local_principal`, deterministic seed data, fake secret references, and mocked provider/model/tool paths.

## Constitution Impact

- **Durable By Default**: Revision tokens, idempotency keys, and stale conflict recovery are required so browser saves are resumable and safe after interruptions.
- **Immutable State And Memory**: Saves create explicit draft revisions instead of mutating opaque browser state as the source of truth.
- **Contract-First Agent Coordination**: Complete workflow document contracts and generated TypeScript types are required before later browser controls depend on the API.
- **Security With Practical Development Ergonomics**: Auth0-shaped authorization and local-principal QA must both exercise tenant and platform scope checks.
- **Operability Is A Product Requirement**: Audit summaries, validation findings, and safe problem details are required for diagnosing workflow setup failures.
- **Tenant Isolation And Fair Scheduling**: Tenant and platform scope must be explicit on every mutation and reference check.
- **Secret Hygiene And Controlled Tool Access**: Secrets, credential values, provider payloads, and raw tool data must never appear in responses, audit summaries, QA artifacts, or docs.
- **Version-Pinned Execution**: Workflow document revisions remain the authoring source for later published version bundles and runtime pinning.

## Testing Instructions

- Add focused backend route and contract tests for complete document save, stale conflict, idempotency replay, idempotency mismatch, invalid graph references, duplicate keys, missing entry node, unsafe text, oversized documents, cross-tenant denial, tenant/platform scope mismatch, and redaction-safe errors.
- Add generated contract freshness checks and frontend API client/type coverage for the new editor contracts.
- Add Spec 069 QA docs, QA environment, and Playwright smoke evidence using local-principal auth.
- Update `curl_testing.md` for any new or behaviorally changed route family and run the `multi-agent-curl-test` regression after spec-specific validation passes.

## Documentation Impact

- Add or update Spec 069 QA guide, UI walkthrough, user guide, quickstart, and contract documentation.
- Document the React-facing full document save request, successful response, validation failure response, stale conflict response, idempotency behavior, authorization behavior, and redaction rules.
- Keep API calls as validation aids; browser setup guidance must continue to prefer visible React Admin navigation after login.

## PR Review Guidance

- Verify that React saves persist full workflow document sections and do not regress existing lower-level workflow APIs.
- Review tenant isolation, platform scope, stale conflict, idempotency, redaction, audit summary, generated TypeScript, and curl coverage before approving.
- Confirm no production path synthesizes fake workflows, fake agents, fake prompts, fake profiles, fake evidence, fake runs, or sample runtime records.
