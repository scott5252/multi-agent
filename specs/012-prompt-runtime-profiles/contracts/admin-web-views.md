# Admin Web View Contract: Prompt Library And Agent Runtime Profiles

## Navigation

Add shared admin shell items:

```text
Label: Prompt Library
Path: /admin/prompt-runtime/prompts
Surface policy: platform-admin and tenant-admin scoped mutation, authorized scoped read

Label: Agent Profiles
Path: /admin/prompt-runtime/profiles
Surface policy: platform-admin and tenant-admin scoped mutation, authorized scoped read
```

The navigation must use existing authorization-aware shell behavior. Users who
lack a surface cannot infer hidden prompt or profile assets from navigation,
counts, or error messages.

## Prompt Library Pages

### Prompt List

`GET /admin/prompt-runtime/prompts`

Shows prompt lineages and prompt versions visible to the active admin scope.

Required controls:

- Search by prompt name, slug, purpose, and version label.
- Filter by scope, tenant, status, validation state, author, grant state, and
  updated timestamp.
- Create prompt lineage.
- Open draft, latest published version, history, and grants when authorized.

Required columns:

- Display name
- Scope
- Latest draft revision
- Latest published version
- Status
- Validation state
- Tenant grant summary
- Updated timestamp

### Prompt Create And Edit

`GET /admin/prompt-runtime/prompts/new`

`GET /admin/prompt-runtime/prompts/{prompt_lineage_id}/edit`

Renders a guided form for non-developer administrators.

Required sections:

- Overview: scope, tenant, display name, slug, purpose, and usage notes.
- Prompt content: plain textarea with placeholder highlighting for
  `{{variable_name}}`.
- Variables: editable table with name, purpose, required flag, allowed value
  category, sample guidance, and validation messages.
- Fixture sets: sanitized sample values grouped by label, with unsafe values
  rejected before save.
- Validation: blocking and advisory findings with clear remediation.
- Preview: fixture selection and rendered safe preview.
- Publication: reason, last validation evidence, immutable publish action.
- Retirement: reason and impact summary for active published versions.

Required safe states:

- Publish button disabled until the latest revision has passing validation.
- Preview button disabled when required fixture values are missing or unsafe.
- Stale revision errors preserve the user's submitted fields and show reload
  guidance.
- Unsafe fixture errors identify the variable or fixture field without echoing
  secret-like content.
- Published prompt content is read-only; changing it requires a new draft.

### Prompt Detail

`GET /admin/prompt-runtime/prompts/versions/{prompt_version_id}`

Shows immutable prompt version metadata, content when authorized, variables,
validation evidence, tenant grants, retirement status, and references from
profiles, workflow bundles, Spec 007 prompt references, and runs.

Required safe states:

- Retired prompt versions are marked unavailable for new use but reviewable for
  authorized historical context.
- Unauthorized users receive safe not-found or safe forbidden behavior with no
  protected content leakage.

### Prompt History

`GET /admin/prompt-runtime/prompts/{prompt_lineage_id}/history`

Shows draft saves, validations, previews, publications, retirements, grants,
revocations, denied attempts, and safe audit summaries.

Required fields:

- Action
- Actor
- Timestamp
- Reason
- Prior version
- New version
- Outcome
- Safe diff or validation summary

## Agent Profile Pages

### Profile List

`GET /admin/prompt-runtime/profiles`

Shows runtime profile lineages visible to the active admin scope.

Required controls:

- Search by agent key, display name, purpose, prompt version, and model routing
  hint.
- Filter by scope, tenant, agent kind, active state, validation state, grant
  state, and updated timestamp.
- Create profile.
- Open draft, active version, history, grants, and resolution preview when
  authorized.

Required columns:

- Agent key
- Agent kind
- Scope
- Active profile version
- Validation state
- Prompt reference summary
- Model/memory/tool summary
- Tenant grant summary
- Updated timestamp

### Profile Create And Edit

`GET /admin/prompt-runtime/profiles/new`

`GET /admin/prompt-runtime/profiles/{agent_runtime_profile_id}/edit`

Renders a guided profile form.

Required sections:

- Overview: scope, tenant, agent key, agent kind, display name, and purpose.
- Prompt references: chooser showing only active, compatible, authorized prompt
  versions; retired or unauthorized versions cannot be selected for new use.
- Model routing hints: selector aligned with existing model-skill config
  scopes without overriding routing authorization.
- Memory scope policy: fields backed by existing memory policy options.
- Skill requirements: required skills, acceptable versions, and availability
  expectations.
- Tool policy expectations: expected tool permission categories and constraints.
- Output contract expectations: expected output shape and handoff obligations.
- Test-suite requirements: named test suites, required status, and evidence
  notes.
- Validation: section-by-section blocking and advisory findings.
- Activation: reason, expected previous active version, and stale validation
  checks.
- Retirement: reason and historical impact summary for active versions.

Required safe states:

- Activation is disabled until current draft validation passes.
- Missing prompt references, retired prompts, unauthorized platform prompts,
  incompatible memory policy, missing skill requirements, missing tool
  expectations, missing output contracts, and missing tests show blocking
  messages near the responsible section.
- Conflicting active profile attempts show the current active version and
  require a refresh or explicit expected previous version.

### Profile Detail

`GET /admin/prompt-runtime/profiles/versions/{agent_profile_version_id}`

Shows immutable profile version metadata, prompt references, model routing
hints, memory policy, skill requirements, tool expectations, output contract
expectations, test-suite requirements, validation evidence, tenant grants,
retirement status, workflow bundle references, and run pins.

### Profile Resolution Preview

`GET /admin/prompt-runtime/profiles/resolve`

Allows an authorized admin to choose tenant, agent key, and agent kind and see
which active profile would resolve for new use.

Required output:

- Selected profile version
- Source scope: tenant or platform fallback
- Considered profile versions
- Tenant grant status for platform fallback
- Blocking issues when no profile resolves

### Profile History

`GET /admin/prompt-runtime/profiles/{agent_runtime_profile_id}/history`

Shows draft saves, validations, activations, retirements, grants, revocations,
denied attempts, and safe audit summaries.

## Workflow Studio Integration

Workflow validation screens must surface prompt/profile findings in the same
plain-language validation panel used for existing workflow registry errors.

Required behavior:

- Every referenced agent key and sub-agent key shows the resolved profile
  version or a blocking issue.
- Every prompt reference shows the Spec 007 prompt reference version and the
  underlying prompt library version id when authorized.
- Missing, retired, unauthorized, wrong-scope, or incompatible references link
  to the relevant prompt/profile page only when the user is authorized.
- Published workflow bundle detail pages show pinned prompt/profile versions.

## View Model Rules

- View models are generated from service/API response schemas rather than raw
  ORM rows.
- Raw secrets, credential values, unauthorized run content, provider tokens,
  and unsafe rendered prompts are never rendered.
- Forms require CSRF/session protection under existing admin auth.
- Preview forms must never perform model calls, live run-data lookups, DNS
  lookups, HTTP requests, or external tool calls.
- Empty states are action-oriented for authorized users and non-revealing for
  unauthorized users.
- Pages remain usable without optional JavaScript; JavaScript may enhance
  fixture rows, validation refresh, and unsaved-change warnings only.
