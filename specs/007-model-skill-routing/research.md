# Research: Model Routing And Skill Configuration

## Decision: Use a dedicated configuration subsystem under `multi_agent_platform.config`

**Rationale**: Model routing, skill bindings, tool policies, outbound policies,
secret references, credential requirements, resolution previews, rollback, and
provenance have shared versioning and audit behavior. A focused domain package
keeps this logic out of FastAPI routers and runtime orchestration while giving
the runtime one resolver facade.

**Alternatives considered**: Embedding routing fields directly in workflow
registry records would blur immutable workflow publishing with operational
configuration. Resolving policies ad hoc from runtime nodes would duplicate
security logic and make deterministic tests fragile.

## Decision: Store immutable configuration versions plus active projections

**Rationale**: The spec requires reviewable history, rollback, and run
provenance. Immutable version rows preserve who changed what and why; active
projection rows make preview and runtime lookup fast without rewriting history.

**Alternatives considered**: Updating rows in place would make rollback and
audit evidence weak. Storing only event streams was rejected for initial scope
because runtime needs predictable indexed lookups.

## Decision: Keep tenant default model routing separate from prompt references

**Rationale**: The global LLM default is tenant-scoped, but prompt resolution
must use only step, agent, then workflow references. Keeping prompt references
as independent versioned records prevents accidental tenant-global prompts and
makes missing prompt failures explicit.

**Alternatives considered**: Bundling prompt ids inside model routing records
was rejected because it would let a tenant default supply prompts and would
make prompt-only rollback harder.

## Decision: Resolve models with override precedence and policies by intersection

**Rationale**: Model routing has an explicit specificity hierarchy: step,
agent, workflow, tenant default. Skill, tool, outbound, and credential policies
are security constraints, so broader policies must keep constraining narrower
ones. Cumulative intersection gives deterministic fail-closed behavior.

**Alternatives considered**: Last-write-wins policy overrides were rejected
because they allow a narrow policy to bypass tenant-wide restrictions.
Priority-weighted policy evaluation was rejected as harder to explain and test.

## Decision: Pin run-level configuration at acceptance and first-use decisions at use time

**Rationale**: Some configuration can be resolved when a run is accepted, while
tool destinations and credential contexts may only be known at runtime.
Pinning candidates at acceptance and exact step/tool decisions at first use
keeps resumed runs stable and preserves provenance without requiring full
static expansion of every possible tool request.

**Alternatives considered**: Pinning everything only at acceptance was rejected
because dynamic tool destinations and credential contexts may not exist yet.
Resolving everything against latest active configuration on resume was rejected
because it breaks replay and incident analysis.

## Decision: Rollback by reactivating prior versions, not by mutating history

**Rationale**: Rollback should affect future resolution while preserving the
bad version for audit and incident review. Reactivating a prior immutable
version through an audited rollback action satisfies operational recovery and
history requirements.

**Alternatives considered**: Deleting bad versions or editing them in place was
rejected because it would erase evidence. Automatically migrating in-flight
runs during rollback was rejected because it violates pinned execution unless
explicitly approved.

## Decision: Use safe secret references and delegated credential metadata only

**Rationale**: The constitution and spec require secret hygiene. Persisted
configuration, run provenance, logs, traces, and audits must store identifiers,
provider keys, status, scope, and redacted summaries, while raw secret values
remain in the configured secret manager.

**Alternatives considered**: Encrypted secret values in policy tables were
rejected because policy history and run provenance should not become secret
stores. Storing provider error bodies was rejected because they may leak
sensitive details.

## Decision: Normalize outbound destinations before policy matching

**Rationale**: Domain policies are only deterministic if hosts are normalized
before matching. Lowercase and IDNA-normalized hosts, explicit scheme/port
handling, rejected embedded credentials, and conservative wildcard semantics
make allow/deny outcomes repeatable and testable.

**Alternatives considered**: Raw string suffix matching was rejected because it
is error-prone for case, IDNA, credentials, and wildcard edge cases. Full URL
regular expressions were rejected for initial scope because they are hard to
review safely.

## Decision: Persist every runtime allow or deny decision before side effects

**Rationale**: Operators need evidence for both permitted and blocked model,
skill, tool, domain, credential, and secret-reference decisions. Persisting the
decision before calling the model or tool ensures denied actions are recorded
and allowed external side effects can be traced to policy versions.

**Alternatives considered**: Logging-only decisions were rejected because logs
are not authoritative provenance. Persisting only denials was rejected because
allowed tool use also needs reproducible evidence.

## Decision: Expose API endpoints plus minimal admin web views

**Rationale**: API endpoints support automation and contract tests, while
minimal admin views let administrators preview resolution, inspect history,
review run provenance, and perform rollback without database access. The
views can reuse existing FastAPI/server-rendered admin patterns.

**Alternatives considered**: API-only delivery was rejected by the clarified
spec. A full rich UI redesign was rejected as unnecessary for initial safe
configuration and review workflows.

## Decision: Make deterministic resolution the center of the test suite

**Rationale**: The highest-risk behavior is policy drift or ambiguous
resolution. Table-driven resolver tests, policy intersection tests, active
version ordering tests, and serialized snapshot tests make precedence and
pinning explicit and protect future refactors.

**Alternatives considered**: Relying mainly on end-to-end workflow tests would
miss edge cases and make failures harder to diagnose. Snapshotting raw DB rows
was rejected in favor of stable domain decision payloads.
