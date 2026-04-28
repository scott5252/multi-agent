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
