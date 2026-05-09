# Feature Specification: Durable Agent Interaction Evidence And Replay Graph

**Feature Branch**: `codex/068-durable-agent-interaction-evidence-and-replay-graph`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "Add durable Agent Interaction Evidence for high-fidelity runtime communication graphs. The feature must record safe summaries of agent-to-agent delegation, context transfer, result return, join contribution, approval pause/resume, and handoff interactions during workflow runs. Each interaction record must be tenant-scoped, linked to workflow run, source node, target node, runtime step, timeline event, optional artifact references, status, timestamps, idempotency key, provenance, safe summary, classification, and digest metadata. The graph UI must be able to render a replay path from these records. The system must not store or render raw prompts, completions, memory contents, provider responses, credentials, authorization headers, private channel payloads, raw tool outputs, or stack traces. Worker retry/resume must not duplicate interaction evidence. Cross-tenant access must fail closed."

## User Scenarios & Testing

### User Story 1 - Record Safe Runtime Interactions (Priority: P1)

When a workflow run executes, the platform records durable, safe interaction evidence for communication between graph nodes.

**Why this priority**: Spec 067 can infer a runtime graph from steps and timeline events, but replay needs explicit source/target interaction records for delegation, context transfer, result return, joins, approvals, and handoffs.

**Independent Test**: Execute or seed a deterministic run and verify the repository records tenant-scoped interaction evidence with idempotency keys, safe summaries, classifications, digests, timestamps, provenance, and no raw payload fields.

**Acceptance Scenarios**:

1. **Given** a role node sends output to downstream nodes, **When** evidence is recorded, **Then** each downstream interaction stores source node, target node, runtime step, status, safe summary, classification, digest, and idempotency key.
2. **Given** a join node evaluates branch contributions, **When** the join completes or pauses, **Then** interaction evidence records branch contribution summaries without raw branch payloads.
3. **Given** a worker retries or resumes a run, **When** the same interaction is recorded again with the same idempotency key, **Then** the existing evidence is returned and no duplicate row is created.

---

### User Story 2 - Inspect Replay Path In Runtime Graph (Priority: P2)

An authorized admin opens the runtime graph and sees a replay path derived from durable interaction evidence.

**Why this priority**: Operators need to understand communication flow without inspecting raw timeline JSON or stitching together handoff records by hand.

**Independent Test**: Seed interaction evidence for a run, request the runtime graph, and verify nodes and edges include replay evidence references, sequence-aware summaries, evidence counts, and safe selected detail content.

**Acceptance Scenarios**:

1. **Given** a run has durable interaction evidence, **When** the admin requests `/admin/runs/{workflow_run_id}/agent-graph`, **Then** the graph includes interaction references on matching edges and provenance evidence counts.
2. **Given** an admin selects a replayed edge, **When** the detail panel renders, **Then** it lists ordered safe interaction summaries, status, timestamps, and references only.
3. **Given** interaction evidence cannot map to a topology edge, **When** the graph is generated, **Then** the graph reports partial replay evidence without inventing nodes or edges.

---

### User Story 3 - Survive Worker Retry And Resume (Priority: P3)

The interaction evidence path remains stable when the worker retries, resumes, or encounters a paused run.

**Why this priority**: Duplicate replay evidence would make run investigation misleading and can grow without bound during retries.

**Independent Test**: Record the same interaction twice with the same idempotency key, resume a partially executed graph, and verify evidence counts remain stable while new genuinely distinct interactions get increasing sequence numbers.

**Acceptance Scenarios**:

1. **Given** a worker repeats a completed node finalization, **When** the same interaction evidence idempotency key is reused, **Then** only one evidence row exists.
2. **Given** an approval node pauses execution, **When** the graph is replayed, **Then** the replay path includes an approval pause interaction linked to the paused run step.
3. **Given** a manual-resolution join pauses execution, **When** evidence is inspected, **Then** branch contribution and manual-resolution interactions remain ordered and safe.

---

### User Story 4 - Exclude Sensitive Payloads (Priority: P4)

The system proves that durable interaction evidence excludes protected raw content.

**Why this priority**: Interaction evidence is intentionally durable and graph-visible; it must be stricter than transient debug output.

**Independent Test**: Attempt to record payloads containing raw prompt, completion, provider response, credential, channel payload, memory content, raw tool output, or stack trace markers and verify persisted records contain only safe summaries, redacted structured metadata, digests, and classifications.

**Acceptance Scenarios**:

1. **Given** a source payload has sensitive key names, **When** evidence is recorded, **Then** the persisted structured metadata redacts sensitive values and stores digests instead.
2. **Given** a cross-tenant user requests a graph with interaction evidence, **When** authorization fails, **Then** no topology, evidence count, source/target node, or summary is returned.
3. **Given** QA screenshots and exported safe responses are scanned, **When** protected marker strings are searched, **Then** zero raw prompt, completion, credential, provider response, private payload, memory, raw tool output, or stack trace markers appear.

### Edge Cases

- A workflow run has interaction evidence but no matching published topology edge.
- A workflow run has a source step but target step has not yet started.
- A worker retries after a successful handoff and repeats the same idempotency key.
- A paused approval node has no decision yet.
- A join receives a mix of succeeded and failed branch contributions.
- A run has artifact references but the user is only authorized to see safe artifact metadata.
- A platform operator has allowed scope and filters by tenant.
- A tenant admin from another tenant requests the same run graph.
- Evidence payloads include sensitive key names, large strings, binary-like values, or stack trace markers.
- A narrow mobile viewport shows replay evidence lists.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST persist tenant-scoped runtime interaction evidence for workflow run communication that cannot be faithfully reconstructed from run steps and timeline events alone.
- **FR-002**: Each interaction evidence record MUST include workflow run ID, source node key, optional target node key, optional source and target run step IDs, interaction kind, status, sequence, safe summary, classification, payload digest, provenance, artifact references, timestamps, and idempotency key.
- **FR-003**: Interaction kinds MUST cover delegation, context transfer, result return, join contribution, approval pause, approval resume, handoff, tool call, checkpoint, manual resolution, and run completion where applicable.
- **FR-004**: Recording evidence with the same tenant, workflow run, and idempotency key MUST be idempotent and MUST NOT create duplicate evidence rows.
- **FR-005**: The runtime graph projection MUST load authorized interaction evidence and attach mapped records to matching graph edges or graph-level partial replay evidence.
- **FR-006**: Runtime graph provenance MUST expose safe interaction evidence counts and replay availability without leaking unauthorized content.
- **FR-007**: Selected node or edge details MUST display safe interaction summaries, statuses, timestamps, classifications, artifact reference IDs, and safe links only.
- **FR-008**: Cross-tenant and unauthorized access MUST fail closed before interaction evidence is loaded or exposed.
- **FR-009**: Worker execution paths MUST record interaction evidence for successful handoffs, result returns, join contributions, approval pauses, manual-resolution pauses, and terminal completion.
- **FR-010**: Worker retry and resume behavior MUST reuse deterministic idempotency keys for the same interaction.
- **FR-011**: Persisted interaction evidence MUST redact sensitive structured metadata and MUST store digests instead of raw protected values.
- **FR-012**: The system MUST NOT store or render raw prompts, completions, memory contents, provider responses, credentials, authorization headers, private channel payloads, raw tool outputs, or stack traces.
- **FR-013**: Interaction evidence MUST preserve existing runtime execution semantics, timeline behavior, workbench panels, exports, and Spec 067 graph behavior.
- **FR-014**: New or changed public/admin JSON route behavior MUST be covered by `curl_testing.md` and the multi-agent curl regression.
- **FR-015**: QA validation MUST include backend persistence/idempotency/redaction tests, runtime projection tests, frontend replay evidence tests, Playwright screenshots, QA docs, and deterministic local seed data.

### Key Entities

- **Runtime Interaction Evidence**: A durable safe-summary record of one communication or replay-relevant interaction during a workflow run.
- **Interaction Kind**: The normalized kind of communication, such as delegation, context transfer, result return, join contribution, approval pause, handoff, or run completion.
- **Replay Path**: Ordered interaction evidence associated with runtime graph edges and graph-level partial evidence.
- **Interaction Provenance**: Safe metadata linking an interaction to runtime step, timeline event, bundle, source, target, artifact references, and instrumentation source.
- **Interaction Classification**: A safe label describing the evidence content class, such as `safe-summary`, `redacted-summary`, or `artifact-reference`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Local QA records at least five durable interaction evidence rows for a seeded run and exposes them through runtime graph replay references.
- **SC-002**: Replaying the same seeded interaction twice leaves the evidence count unchanged for that idempotency key.
- **SC-003**: A runtime graph response includes interaction evidence counts and at least three mapped replay references without raw protected fields.
- **SC-004**: Cross-tenant runtime graph requests expose zero interaction evidence details.
- **SC-005**: Desktop and mobile Playwright screenshots show replay evidence without incoherent text overlap.
- **SC-006**: QA visible-copy scans find zero raw prompt, completion, provider response, credential, private channel, memory, raw tool output, or stack trace markers.
- **SC-007**: The multi-agent curl regression passes with the new interaction replay graph coverage.

## Assumptions

- Specs 065 through 067 are complete and the runtime graph projection route exists.
- Existing run steps and timeline events are sufficient for execution state, but insufficient for ordered source/target replay semantics.
- New persistence is limited to safe interaction evidence and does not store message-level transcripts or raw payloads.
- Interaction evidence is read-only from Admin UI surfaces.
- Existing artifact storage and workbench links remain the safe place for authorized artifact inspection.

## Clarifications

### Session 2026-05-09

- Q: Should Spec 068 add new durable persistence? -> A: (autopilot) Yes. Specs 065-067 prove runtime graph rendering works, but existing run steps and timeline events do not preserve explicit ordered source/target interaction semantics for high-fidelity replay.
- Q: What can be persisted in an interaction record? -> A: (autopilot) Persist only safe summaries, classifications, references, digests, sequence, status, timestamps, provenance, and redacted structured metadata; never raw prompts, completions, provider responses, credentials, private payloads, memory, raw tool output, or stack traces.
- Q: Where should replay evidence appear first? -> A: (autopilot) Reuse the existing Admin run inspection runtime graph and operations workbench `AgentGraphPanel`; do not add a separate visualization framework.
- Q: How should idempotency work? -> A: (autopilot) Use deterministic tenant/run/idempotency keys derived from workflow run, source node, target node, interaction kind, and stable step/evidence identifiers so retries and resumes return the existing row.
- Q: How should unmapped interaction evidence render? -> A: (autopilot) Keep it in graph-level partial replay evidence and provenance counts; do not synthesize production graph nodes or edges.
- Q: What validation is required? -> A: (autopilot) Validate persistence, idempotency, tenant isolation, redaction, graph replay projection, worker instrumentation, frontend replay details, Playwright desktop/mobile flows, curl coverage, and full post-roadmap stability gates.
