# Research: Prompt Library And Agent Runtime Profiles

## Prompt Template Syntax

Decision: Support only literal `{{variable_name}}` placeholders, with variable
names matching `[A-Za-z_][A-Za-z0-9_]*`.

Rationale: The feature needs deterministic validation, safe fixture previews,
and no template code execution. A small parser is easier to audit, test, and
explain to non-developer admins than a full template engine.

Alternatives considered: Jinja2 templates were rejected because filters, loops,
conditionals, and expressions enlarge the safety surface. Python `format`
strings were rejected because braces are harder for admins to read and validate
without accidental formatting semantics.

## Variable Schema

Decision: Store declared variables as structured records with name, purpose,
required flag, allowed value category, sample guidance, and safety
classification.

Rationale: Structured declarations let validation compare declared variables
against template usage, make UI forms understandable, and allow future policy
checks without parsing free text.

Alternatives considered: JSON Schema for prompt variables was rejected for the
initial scope because admins need simple named placeholders, not nested runtime
payload validation. Free-form markdown documentation was rejected because it
cannot drive publish gates.

## Safe Fixture Previews

Decision: Persist sanitized, non-sensitive fixture value sets on prompt drafts
and render previews from those fixture sets only.

Rationale: Repeatable browser previews help reviewers reproduce validation and
publication decisions. Sanitizing before storage prevents unsafe samples from
landing in draft records or audit summaries.

Alternatives considered: One-time preview-only input was rejected by the
clarified requirements. Live run-data previews were rejected because they risk
exposing unauthorized run content and make preview behavior non-deterministic.

## Prompt Publish Lifecycle

Decision: Keep editable prompt authoring in draft revisions and create
immutable `prompt_versions` on publish. Retire published versions from new use
without mutating the content snapshot.

Rationale: Immutable prompt versions are required for workflow bundle pinning,
run replay, audit review, and safe retirement. Draft revisions provide
optimistic concurrency and preserve authoring history without altering
published facts.

Alternatives considered: In-place mutable prompt rows were rejected because
they would corrupt historical run meaning. Soft-copying content into Spec 007
prompt references was rejected because prompt content ownership belongs in the
prompt library.

## Spec 007 Prompt Reference Integration

Decision: Treat `prompt_versions.prompt_version_id` as the canonical target
for Spec 007 `PromptReferenceVersion.prompt_version_id`, while Spec 007 keeps
its existing workflow/agent/step scoping and resolution precedence.

Rationale: This preserves established model-skill routing behavior while
adding real prompt version governance behind the referenced ids. The prompt
library validates existence, status, digest, and authorization before a prompt
reference can be created or activated.

Alternatives considered: Replacing Spec 007 prompt references was rejected
because routing scope and run resolution are already modeled there. Duplicating
prompt lifecycle inside model-skill config was rejected because prompt authors
need a dedicated library UI and lifecycle.

## Runtime Profile Resolution

Decision: Resolve agent/sub-agent runtime profiles by exact key and scope, with
tenant active profile winning over authorized platform active profile for the
same key.

Rationale: Tenant overrides are explicit and predictable, while platform
profiles provide reusable defaults only when no tenant profile exists. This
matches clarified requirements and avoids ambiguous active profile conflicts.

Alternatives considered: Platform-first precedence was rejected because it
would weaken tenant customization. Multiple active profiles for the same key
were rejected because workflow validation and runtime provenance need one clear
winner.

## Tenant Allowlist Grants

Decision: Grant platform prompt/profile versions to tenants with explicit
per-version allowlist rows.

Rationale: Per-version grants avoid accidental exposure of future platform
prompt/profile versions and keep tenant visibility auditable.

Alternatives considered: Lineage-level grants and key-level grants were
rejected because they would inherit future versions by default. Global platform
visibility was rejected because tenant selection must fail closed.

## Workflow Registry Validation

Decision: Add validation hooks that check prompt references, agent keys,
sub-agent keys, profile compatibility, retired state, grant visibility, memory
policy, model routing hints, skill requirements, tool expectations, output
contracts, and test-suite requirements.

Rationale: Workflow registry publication is the right gate to catch missing or
incompatible prompt/profile dependencies before workflows can be published or
accepted for execution.

Alternatives considered: Runtime-only validation was rejected because errors
would surface too late and could start side effects. UI-only validation was
rejected because API-created drafts must be governed by the same rules.

## Run Pinning

Decision: Pin all workflow-declared prompt/profile references at run
acceptance. Allow first-use pinning only for dynamically selected agents or
sub-agents that were not declared upfront, and audit that decision before side
effects.

Rationale: This satisfies version-pinned execution while preserving a narrow,
auditable path for dynamic agent selection.

Alternatives considered: First-use pinning for every agent was rejected because
run behavior could drift after acceptance. Re-resolving active pointers on
resume was rejected because it breaks replay and incident analysis.

## Admin Browser Experience

Decision: Deliver server-rendered shared-shell pages for prompt library and
agent profile management, with optional JavaScript enhancements for repeated
fixture rows, validation preview refresh, and unsaved-change prompts.

Rationale: Existing admin features use FastAPI/Jinja2 shared-shell views. A
server-rendered approach keeps authorization, validation, and safe error
states centralized while remaining usable without custom frontend tooling.

Alternatives considered: API-only administration was rejected by the feature
requirements. A separate SPA was rejected for initial scope because the project
already has a shared admin shell and the feature is workflow/form heavy.

## Audit And Redaction

Decision: Use existing audit/debugging and redaction helpers for lifecycle
events, denied attempts, validation summaries, and preview summaries, adding
prompt/profile categories where needed.

Rationale: Centralized audit and redaction keeps behavior consistent with
model provider, workflow, memory, and runtime provenance features.

Alternatives considered: Feature-local audit logs were rejected because they
would fragment governance evidence. Storing full rendered previews in audit
records was rejected because rendered prompt text may include sensitive or
unauthorized fixture content.

## Version 2 Runtime Gateway Completion

The following decisions extend the completed prompt/profile implementation
without changing V1 authoring, lifecycle, UI, workflow validation, model-skill
prompt reference, tenant grant, immutable versioning, retirement, docs, or
migration behavior.

## Container-Managed Gateway Dependencies

Decision: Build `ModelProviderService`, `ModelGateway`,
`ProviderAdapterRegistry`, provider repository factories, provider secret
resolution, metrics/tracing/audit hooks, retry decision helpers, and breaker
decision helpers from the application `Container`.

Rationale: Runtime workers and admin probes need a single dependency graph that
owns repository construction, provider adapter lifecycle, secret resolution,
and observability. Container-managed factories prevent unmanaged HTTP clients
from being created per request and make worker startup fail closed when gateway
dependencies are incomplete.

Alternatives considered: Constructing gateway dependencies inside each worker
poll or API handler was rejected because it leaks lifecycle ownership and makes
client cleanup unreliable. A separate provider gateway process was rejected
because the existing Spec 011 gateway already lives inside this service.

## Worker Bootstrap Gateway Readiness

Decision: Extend worker bootstrap to expose gateway-ready dependencies before
workers accept model-backed runtime work.

Rationale: Workers are the boundary between durable run leases and provider
side effects. They must know at startup whether provider repositories,
adapter registry, secret resolver, retry/breaker helpers, and safe audit hooks
are available, rather than discovering missing pieces after a run is claimed.

Alternatives considered: Lazy creation after claiming a run was rejected
because a missing dependency could strand a leased run after acceptance.
Creating direct provider clients in orchestration workers was rejected because
adapters must be the only provider SDK/HTTP boundary.

## Runtime Gateway Invocation Ordering

Decision: Invoke `ModelGateway` only after prompt/profile pins are resolved at
run acceptance or dynamic first use, and before any model, tool, memory,
approval, handoff, artifact, or other side-effectful runtime work.

Rationale: Prompt/profile governance is useful only if the exact immutable
versions govern the provider call. Persisting operation identity and gateway
context first gives retry, replay, and audit a durable anchor before external
effects begin.

Alternatives considered: Invoking providers before pin persistence was rejected
because recovery could not prove which prompt/profile version governed the
call. Treating gateway invocation as an after-the-fact audit enrichment was
rejected because it would not prevent bypasses.

## Runtime Profile Contributions To Gateway Context

Decision: Runtime profiles contribute model routing hints, prompt/profile
provenance, memory policy context, tool policy expectations, and output
contract metadata to gateway invocation context, while model_skill_config
remains the authorization and routing decision owner.

Rationale: Profiles explain the intended execution contract, but existing
model_skill_config, provider catalog visibility, tenant authorization, and
credential policy determine whether a provider route is allowed. Separating
profile hints from authorization prevents profile metadata from expanding
tenant or provider access.

Alternatives considered: Letting runtime profiles directly choose provider
connections was rejected because it bypasses Spec 007/011 authorization.
Ignoring profile hints at gateway time was rejected because provenance would
not show why a route was selected for the agent.

## Test Bench And Model-Backed Validation Parity

Decision: Profile test bench execution and model-backed workflow validation
must use the same `ModelGateway` path and safe attempt metadata as production
runtime calls whenever they call a model provider.

Rationale: Admins and reviewers use test bench results to trust production
behavior. Divergent provider paths would hide authorization, retry, breaker,
usage, latency, and audit differences until live runs.

Alternatives considered: Test-only direct providers were rejected because they
would create ungoverned prompts and credentials. Mock-only validation was
rejected for model-backed validation paths that intentionally execute provider
behavior.

## Reliability Mapping

Decision: Map normalized provider errors into existing retry and breaker
decisions: timeouts to timeout, rate limits to rate limited, provider
unavailable and malformed response to dependency unavailable, authorization or
visibility failures to non-retryable authorization/policy denial, and inactive
catalog or invalid model to non-retryable configuration/catalog failure.

Rationale: Spec 009 already provides retry budgets and circuit breaker
concepts. Reusing those helpers keeps provider reliability behavior consistent
with worker reliability and avoids duplicating policy engines.

Alternatives considered: Gateway-local retry logic was rejected because it
would fragment tenant retry budgets and breaker state. Treating all provider
errors as retryable was rejected because authorization, catalog, and credential
failures should fail closed.

## Idempotency And Recovery

Decision: Use one logical operation identity per gateway invocation, provider
probe, and catalog sync. Retries and restarts reuse that identity; each
physical attempt is recorded as a child attempt. Completed authoritative
outcomes are returned on duplicate submit, while ambiguous outcomes are
recovered or fail closed according to retry/breaker policy.

Rationale: Provider operations can be triggered by worker retries, process
restarts, admin resubmits, and catalog recovery. A logical operation record
separates the authoritative outcome from the physical attempts used to reach
or recover it.

Alternatives considered: Using only physical attempt rows was rejected because
duplicates cannot be suppressed reliably. Using provider request ids alone was
rejected because not all providers expose stable ids and local providers may
not support them.

## Admin Probe Controls

Decision: Reuse existing bounded-operation and rate-limit controls before
provider test probes launch provider activity. Probe limits apply by actor and
provider connection, with tenant and global backstops.

Rationale: Provider probes consume shared external or local capacity and may
touch credentials. Existing admin reliability controls already provide the
right safety model and audit expectations.

Alternatives considered: A probe-specific limiter was rejected because it
would duplicate operator policy. Allowing unbounded admin probes was rejected
because probes can become a shared-capacity denial vector.

## Direct Provider Call Guardrails

Decision: Add both static import/usage checks and runtime/integration detection
that fail when runtime, worker, test bench, workflow validation, agent, prompt,
or profile code calls provider SDKs or provider HTTP endpoints outside explicit
`ModelGateway` adapter modules.

Rationale: Static checks catch most regressions during review, while behavioral
tests prove representative model-backed execution paths actually pass through
the gateway and emit expected metadata.

Alternatives considered: Relying only on code review was rejected because
provider calls are easy to reintroduce in tests or validation paths. Relying
only on runtime detection was rejected because bypassing code should fail
before deployment.

## Gateway Observability And Safe Audit

Decision: Correlate prompt/profile pins, selected provider connection, model
id, tenant, workflow run, step, trace, idempotency identity, retry decision,
breaker decision, latency, usage availability, normalized outcome, and safe
summary fields in gateway attempt evidence.

Rationale: Incident review needs prompt/profile governance and provider route
evidence together. Safe summaries preserve debugging value while excluding
raw prompts, completions, credentials, provider tokens, API keys, local
endpoint secrets, unsafe preview content, and unauthorized run content.

Alternatives considered: Storing raw provider request/response payloads was
rejected for security and tenant isolation. Keeping prompt/profile and provider
evidence separate was rejected because auditors need to verify which immutable
governance inputs controlled each provider operation.
