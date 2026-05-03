# Research: Agent And Workflow Test Bench

## Decision: Use A Safe Sandbox Service For Test Runs

**Decision**: Implement a `testing.agent_bench` sandbox service that accepts a
suite, cases, target metadata, and safe execution mode, then produces durable
run and step results. The sandbox records model/provider choices, prompt/profile
references, skill references, usage, latency, contract validation, assertions,
blocked side effects, redacted transcript summaries, and artifact metadata.

**Rationale**: The bench crosses prompts, profiles, workflows, model routing,
skills, tools, and publish gates. A narrow domain service keeps policy and
diagnostic behavior testable without overloading API routers or existing
workflow runtime services.

**Alternatives considered**: Directly invoking full workflow runtime for every
test was rejected for the first slice because mock modes, deterministic
assertions, and side-effect blocking need explicit QA controls. Storing run
logic in the router was rejected because it weakens reuse by workers and tests.

## Decision: Default QA To Mock Model And Mock Tools

**Decision**: Use deterministic mock model output and mock tool results by
default. Add a mocked-provider gateway path for tests that need model-gateway
metadata without real credentials. Real dependency probe mode requires explicit
approved metadata and is blocked in QA unless a safe probe record is present.

**Rationale**: The policy forbids real credentials, production hosts, and
external side effects during autopilot validation. Deterministic mocks make
assertions reliable while still exercising contracts, redaction, usage capture,
and publish gate semantics.

**Alternatives considered**: Always calling the real model gateway was rejected
because validation would depend on external credentials and non-deterministic
output. Hand-waving real probes without persisted approval was rejected by the
constitution and autopilot policy.

## Decision: Store Payload Metadata In PostgreSQL And Large Payloads In Storage

**Decision**: Persist suite/case/run metadata, checksums, safe summaries, and
artifact references in PostgreSQL. Store large fixtures, transcripts,
evaluator evidence, and result artifacts through the existing storage provider
under `.data/qa015-artifacts` for QA.

**Rationale**: This preserves PostgreSQL as the transactional source of truth
without turning it into a blob store, and it gives reviewers deterministic
artifact references to inspect.

**Alternatives considered**: Storing complete transcripts and fixture payloads
in JSONB was rejected because it risks leaking sensitive payloads and violates
tiered storage guidance. Storing only files without DB metadata was rejected
because audit and access control need a durable index.

## Decision: Deterministic Assertions Are Typed Path Comparisons

**Decision**: Represent deterministic assertions as typed checks over
structured outputs: `equals`, `contains`, `matches_regex`, `json_schema`,
`status_is`, `latency_under_ms`, and `usage_under_tokens`.

**Rationale**: Typed assertions make tests independently evaluable, easy to
display in failure diagnostics, and safe to store as JSONB. They also avoid
embedding arbitrary Python or SQL in tenant-created tests.

**Alternatives considered**: Arbitrary expression evaluation was rejected for
security and portability. Plain text expected-output matching was rejected
because the feature requires contract shapes and structured diagnostics.

## Decision: Evaluator Assertions Use Governed Gateway Metadata

**Decision**: Evaluator assertions invoke a governed gateway path only through
safe, redacted inputs and deterministic mocked-provider behavior in tests. The
result records evaluator prompt reference, model/provider summary, threshold,
redacted rationale summary, and pass/fail contribution.

**Rationale**: This matches existing model gateway governance while keeping QA
deterministic and secret-free.

**Alternatives considered**: Free-form evaluator prompt text sent directly to
providers was rejected because it bypasses prompt/version governance and
redaction. Excluding evaluator assertions was rejected because the feature
explicitly requires them.

## Decision: Publication Gates Use Current Passing Suite Evidence

**Decision**: Add a helper that summarizes required test suites by target type,
target id, and candidate version. Publication is blocked when required suites
are missing, stale, failed, or not tied to the current candidate target
version.

**Rationale**: Existing workflow publish gate behavior already accepts a
`RequiredTestSummary`. The test bench can feed that summary and add richer
diagnostics without replacing the existing gate.

**Alternatives considered**: Storing gate status on workflow drafts only was
rejected because evidence must be recalculated when suites, cases, or candidate
versions change. Treating any past passing run as valid was rejected because it
allows stale regressions.

## Decision: Browser UI Is Server-Rendered

**Decision**: Use the existing server-rendered admin shell with templates for
suite list/detail/forms, case forms, run launch, result diagnostics, and gate
status.

**Rationale**: This matches existing admin features, works with local-principal
QA, and keeps non-developer browser validation straightforward.

**Alternatives considered**: A new frontend application was rejected as scope
growth. API-only implementation was rejected because validation requires
browser UI flows and screenshots.

## Decision: Tenant Isolation Is Enforced At Repository And Service Boundaries

**Decision**: Every query and mutation carries tenant id and role context. The
repository filters by tenant, while the service turns cross-tenant direct links
into safe not-found/denied outcomes.

**Rationale**: The bench contains sensitive prompts, profiles, workflow
diagnostics, and artifacts, so cross-tenant detail leaks are high risk.

**Alternatives considered**: UI-only filtering was rejected because API routes
and direct links would still leak records. Global suite ids without tenant
checks were rejected by constitution policy.
