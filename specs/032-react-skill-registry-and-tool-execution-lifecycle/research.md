# Research: React Skill Registry And Tool Execution Lifecycle

## Decision 1: Compose From Existing Skill Registry And Gateway Services

**Decision**: Build a React-specific lifecycle aggregation layer over existing Spec 014/014-v2 skill registry services and Spec 021 SkillExecutionGateway diagnostics rather than creating new lifecycle rules.

**Rationale**: Existing services already own package validation, immutable publication, tenant grants, installations, credential readiness, smoke tests, binding eligibility, quarantine, audit, redaction, connector adapters, and gateway policy decisions. React should clarify workflows and render safe evidence, not duplicate domain policy in the browser.

**Alternatives Considered**:

- Browser-side composition from raw package, installation, and diagnostic endpoints: rejected because it risks policy drift and unsafe raw payload exposure.
- New persistence model for React lifecycle state: rejected because existing package, installation, readiness, job, and audit models remain authoritative.

## Decision 2: Guided Wizards With Backend-Owned Step State

**Decision**: Use guided wizards for platform publication and tenant installation, with backend-owned step metadata, readiness state, actions, revision tokens, and safe recovery hints.

**Rationale**: Non-technical administrators need clear next actions across many states: manifest candidate, validation, smoke-test evidence, tenant grants, credential references, readiness, eligibility, and quarantine. Backend-owned steps prevent the browser from inventing workflow state.

**Alternatives Considered**:

- One dense package table with action buttons: rejected because it hides readiness blockers and recovery steps.
- Separate unrelated pages for every lifecycle action: rejected because the roadmap asks for a coherent lifecycle experience.

## Decision 3: Upload Precedence And No Raw Manifest Echo

**Decision**: When paste and upload are both provided, upload wins. After submit, React receives only safe manifest summaries, digests, findings, and evidence references.

**Rationale**: This avoids ambiguous candidate state and prevents raw manifest text from becoming browser or screenshot evidence.

**Alternatives Considered**:

- Merge paste and upload content: rejected because conflicting manifests could produce unclear validation.
- Echo raw manifest after submit for convenience: rejected because manifests may contain unsafe documentation, tool payload samples, or accidental secrets.

## Decision 4: Explicit Queued Smoke Tests And Diagnostics

**Decision**: Smoke tests, connector diagnostics, readiness refreshes, and approved staging probes are explicit queued actions with safe last-known status and no unbounded polling.

**Rationale**: These actions can touch credentials, connector policies, fairness quotas, job stores, gateway policy, and audit. Queued state is durable and observable without tying the browser to synchronous external work.

**Alternatives Considered**:

- Run diagnostics synchronously in the request: rejected due to latency, failure, and side-effect ambiguity.
- Refresh continuously in the browser: rejected because it can create load and noisy audit without user intent.

## Decision 5: Authorized Credential Reference Picker

**Decision**: Credential configuration uses backend-authorized reference options for the active tenant or platform scope only.

**Rationale**: The browser should help admins select safe references, not expose credential stores, resolved values, or cross-tenant labels. Existing credential readiness and policy services remain authoritative.

**Alternatives Considered**:

- Free-form secret entry in React: rejected because raw secrets must not enter browser contracts.
- Show all platform references to tenant admins: rejected because credential reference metadata can itself be sensitive.

## Decision 6: Read-Only Binding Eligibility Preview

**Decision**: Binding eligibility previews use backend-owned workflow, profile, package, and tenant context choices and return read-only policy decisions.

**Rationale**: Admins need to understand whether an installed skill can bind to a workflow or profile, but preview must not execute tools, resolve live credentials, contact Telegram, call models, or perform connector side effects in local/CI validation.

**Alternatives Considered**:

- Browser-side eligibility rules: rejected because policy logic would drift from runtime publish gates.
- Live tool dry run for eligibility: rejected because it violates the read-only preview guarantee.

## Decision 7: SkillExecutionGateway Diagnostics As Safe Summaries

**Decision**: The React lifecycle page displays SkillExecutionGateway diagnostics as safe summaries: policy decision, side-effect posture, credential status, outbound policy, connector readiness, attempt evidence reference, and remediation.

**Rationale**: Specs 021 and runtime skill tools depend on governed gateway execution. Admins need explainability without raw connector outputs or private channel content.

**Alternatives Considered**:

- Embed raw gateway attempt payloads in React: rejected due to connector, credential, and private-message risks.
- Hide gateway diagnostics from tenant admins entirely: rejected because tenant readiness and workflow binding require understandable evidence.

## Decision 8: Browser-First QA With Contract Backstops

**Decision**: QA032 primary validation is Playwright/browser-first for lifecycle flows, with curl/API checks retained for protected contracts, denied states, and setup.

**Rationale**: Spec 014-v2 explicitly closed a UI workflow gap. The main acceptance path must prove non-technical administrators can complete lifecycle actions in the browser and capture redaction-safe screenshots.

**Alternatives Considered**:

- API-only QA: rejected because it would not prove the browser lifecycle.
- Manual-only browser QA: rejected because protected contracts and redaction rules need deterministic automated checks.
