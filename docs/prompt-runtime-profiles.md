# Prompt Runtime Profiles

Spec `012` adds a governed prompt library and agent runtime profile layer for
the multi-agent platform.

## Prompt Library

Prompt admins create a lineage, save immutable draft revisions, validate
`{{variable_name}}` placeholders against declared variables, render previews
from sanitized fixture values, and publish immutable prompt versions. Published
versions can be retired from new use without changing historical content.
Platform prompt versions require explicit tenant grants before tenant selection.

## Agent Profiles

Agent runtime profiles describe the prompt references, model-routing hints,
memory scope policy, skill requirements, tool expectations, output contracts,
and test-suite requirements for one agent or sub-agent key. Tenant profiles win
over granted platform fallback profiles. Activation creates an immutable
profile version and resolution records the selected profile and prompt ids.

## Workflow And Runtime Integration

Workflow validation can call the prompt/profile adapter to resolve every role
to an active profile and produce prompt/profile pin metadata. Model-skill prompt
references validate prompt library version ids and digests before new use. Run
version bundles and runtime configuration digests include prompt library ids and
digests so accepted runs preserve provenance.

## Browser Admin UI

Shared-shell pages are available at:

- `/admin/prompt-runtime/prompts`
- `/admin/prompt-runtime/prompts/new`
- `/admin/prompt-runtime/profiles`
- `/admin/prompt-runtime/profiles/new`
- `/admin/prompt-runtime/profiles/resolve`

The pages expose scope-aware controls, disabled publish/activate states, safe
preview and validation panels, history timelines, and resolution guidance for
non-developer administrators.

## Audit And Safety

Prompt/profile lifecycle events use safe summaries and classify rendered
previews and template content as prompt content. Audit and metric helpers cover
validation, preview, publish, activate, retire, grant, workflow validation, and
runtime pinning outcomes. Raw secrets, credential values, unauthorized run
content, and unsafe rendered previews must not appear in logs, telemetry, audit
summaries, or admin pages.

## Review

Use [Prompt Runtime Profiles Testing](/Users/scottcornell/src/my-projects/multi-agent/docs/prompt-runtime-profiles-testing.md)
and [Spec 012 QA](/Users/scottcornell/src/my-projects/multi-agent/specs/012-prompt-runtime-profiles/qa012.md)
for reviewer evidence.
