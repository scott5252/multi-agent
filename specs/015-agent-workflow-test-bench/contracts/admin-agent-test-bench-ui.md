# Contract: Admin Agent Test Bench UI

All pages use the existing shared admin shell, local-principal/Auth0
authorization, tenant-scope handling, breadcrumbs/navigation, flash messages,
safe empty/error states, and redaction rules.

## Global UI Rules

- UI routes live under `/admin/agent-tests/ui`.
- Mutation forms work through standard browser POST submits.
- Every page carries an explicit tenant scope label.
- Cross-tenant direct links render not found or absent without target detail.
- Same-tenant role failures render access denied without raw run data.
- Raw fixtures, prompts, provider messages, tool payloads, credential values,
  and unredacted transcripts never render in HTML, page source, screenshots, or
  error pages.
- Large artifacts render as safe metadata and links only when authorized.

## Suite Index

**GET** `/admin/agent-tests/ui`

Shows visible suites for the active tenant and platform scope.

**Required controls**:

- Create suite action.
- Filters for target type, target id, status, required-for-publish, and latest
  run status.
- Links to suite detail and latest run.

**Required states**:

- Empty state for no suites.
- Denied state for missing admin/auditor role.
- Redaction notice.

## Create Or Edit Suite

**GET** `/admin/agent-tests/ui/suites/new`  
**POST** `/admin/agent-tests/ui/suites`  
**GET** `/admin/agent-tests/ui/suites/{suite_id}/edit`  
**POST** `/admin/agent-tests/ui/suites/{suite_id}`

**Fields**:

- `tenant_id`
- `name`
- `description`
- `target_type`
- `target_id`
- `target_version`
- `default_safe_mode`
- `model_mode`
- `tool_mode`
- `pass_threshold`
- `required_for_publish`
- `revision`

**POST behavior**:

- Validates target reference and tenant access.
- Requires tenant admin or platform admin.
- Uses revision tokens for existing suites.
- Redirects to suite detail on success.
- Renders field errors on failure.

## Suite Detail

**GET** `/admin/agent-tests/ui/suites/{suite_id}`

Shows suite metadata, cases, assertions summary, latest runs, publish gate
status, and run launch form.

**Required controls**:

- Add case.
- Edit suite.
- Run suite.
- Archive or restore suite.
- Open run results.

**Required diagnostics**:

- Current target version.
- Required-for-publish status.
- Latest passing run for the current target version.
- Stale or missing evidence warning.

## Create Or Edit Case

**GET** `/admin/agent-tests/ui/suites/{suite_id}/cases/new`  
**POST** `/admin/agent-tests/ui/suites/{suite_id}/cases`  
**GET** `/admin/agent-tests/ui/suites/{suite_id}/cases/{case_id}/edit`  
**POST** `/admin/agent-tests/ui/suites/{suite_id}/cases/{case_id}`

**Fields**:

- `name`
- `description`
- `fixture_json`
- `expected_contract_shape`
- `deterministic_assertions`
- `evaluator_prompt_ref`
- `model_mode`
- `tool_mode`
- `pass_threshold`
- `order`
- `revision`

**POST behavior**:

- Parses fixture and contract JSON structurally.
- Redacts fixture summary before rendering.
- Rejects unsupported assertion comparators.
- Stores large fixture references when needed.
- Uses revision tokens for existing cases.

## Launch Run

**POST** `/admin/agent-tests/ui/suites/{suite_id}/runs`

**Fields**:

- `target_version`
- `safe_mode`
- `idempotency_key`
- `run_reason`

**POST behavior**:

- Requires tenant admin or platform admin.
- Rejects archived suites and suites with no active cases.
- Blocks approved real probe mode unless approval metadata exists.
- Creates a durable run and executes the safe sandbox path.
- Redirects to run detail.

## Run Detail

**GET** `/admin/agent-tests/ui/runs/{run_id}`

Shows run summary, pass/fail status, safe mode, target version, trace id,
usage, latency, redaction summary, blocked side effects, case/step timeline,
assertion diagnostics, contract validation diagnostics, artifact metadata, and
publication gate evidence.

**Required states**:

- Queued/running.
- Passed.
- Failed assertion.
- Contract failure.
- Blocked side effect.
- Error with safe reason.
- Artifact expired/unavailable.

## Publish Gate Status

**GET** `/admin/agent-tests/ui/suites/{suite_id}/publish-gate`

Shows whether the selected suite has current passing evidence for its target.

**Required content**:

- Required suite id/name.
- Current target version.
- Latest passing run id if current.
- Missing/stale/failing reason.
- Link to run suite.

## Browser Validation Flow

1. Log in through `/auth/local-login?redirect_to=/admin/agent-tests/ui`.
2. Create a suite for a workflow draft target.
3. Add one passing mock case and one failing assertion case.
4. Run the suite in mock model mode.
5. Open run detail and capture the pass/fail diagnostics.
6. Change to mocked provider mode and prove side effects are blocked.
7. Verify another tenant cannot see the suite, run, artifacts, or target names.
