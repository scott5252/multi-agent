# Contract: Minimal Admin Web Views

The feature adds server-rendered admin pages that reuse the existing
`web_admin` template pattern. These views are intentionally small: they expose
the same configuration, preview, history, rollback, and provenance behavior as
the APIs for administrators, auditors, workflow owners, and maintainers.

## `/admin/config/model-routing`

Lists active tenant default, workflow overrides, agent overrides, and step
overrides visible to the signed-in principal.

**Required controls**:

- Filter by tenant, workflow, agent, step, status, and model provider.
- Create or edit a routing version with required reason.
- Preview resolved model for workflow, agent, and step.
- Link to version history and rollback action when authorized.

**Required safety states**:

- Missing global default is shown as a blocking state.
- Inactive or unavailable model references are shown as blocking validation.
- Cross-tenant or unauthorized scopes fail closed with the same safe not-found
  behavior as the API.

## `/admin/config/model-routing/history`

Shows configuration history for model routing and prompt references.

**Required fields**:

- Active version
- Prior version
- Actor
- Timestamp
- Reason
- Affected scope
- Redacted diff summary
- Rollback eligibility

## `/admin/config/skills-tools`

Lists skill bindings, allowed tool policies, outbound domain policies, secret
references, and credential requirements.

**Required controls**:

- Filter by tenant, workflow, agent, step, skill, tool, action category, and
  status.
- Create or edit skill binding with exact skill version.
- Create or edit allowed tool policy with operation categories.
- Create or edit outbound domain policy with normalized domain patterns.
- Create or edit credential requirement using secret reference or delegated
  credential metadata.
- Preview allow/deny outcome for sample skill and tool requests.

**Required safety states**:

- Missing policy previews deny by default.
- Domain preview explains matched policy version ids.
- Credential preview identifies missing, inactive, expired, revoked, or
  out-of-scope references without exposing secret values.

## `/admin/config/runs/{workflow_run_id}/provenance`

Shows the pinned configuration and first-use runtime decisions for a run.

**Required fields**:

- Run-level `ResolvedExecutionConfiguration` digest.
- Model and prompt versions pinned at acceptance or first use.
- Skill binding, tool policy, outbound domain, secret-reference, and
  credential requirement versions evaluated.
- Allow and deny decisions with safe reasons.
- Migration records when present.
- Links to configuration history visible to the viewer.

## View Model Rules

- View models are generated from API/domain response schemas rather than raw
  ORM rows.
- Raw prompts, raw secrets, credential values, provider tokens, and
  unauthorized run content are never rendered.
- Rollback forms require current active version id, target prior version id,
  explicit reason, and CSRF/session protection under existing admin auth.
- Preview forms must never perform model calls, DNS lookups, HTTP requests, or
  external tool calls.
