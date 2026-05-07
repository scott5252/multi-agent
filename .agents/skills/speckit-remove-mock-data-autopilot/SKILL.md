---
name: "speckit-remove-mock-data-autopilot"
description: "Run the live-data and transitional-label cleanup roadmap in remove_mock_data_specs.md as an autonomous Spec Kit sequence for specs 048 through 059, with mandatory QA, Playwright UI/API/database verification, and multi-agent-curl-test validation after every spec."
compatibility: "Requires this multi-agent repo, remove_mock_data_specs.md, completed React UI specs 026-047 context, Spec Kit skills, specs/_autopilot/shared policy and validation bases, PostgreSQL/Docker, uv, Playwright, and the multi-agent-curl-test skill."
metadata:
  author: "multi-agent-project"
---

# Speckit Remove Mock Data Autopilot

Use this skill when the user asks to run, prepare, or resume the live-data
cleanup roadmap from `remove_mock_data_specs.md` through Spec Kit.

This skill is intentionally sequential: create, implement, and validate one
spec at a time from `048` through `059`. Never run these specs in parallel.

This is an autonomous Codex runbook, not a standalone background daemon. When
the user invokes it, Codex must keep working through the queue until every spec
passes validation or a stop condition is reached.

## Required Inputs

Default values:

- Roadmap file: `remove_mock_data_specs.md`
- Spec range: `048..059`
- Queue output: `specs/_autopilot/remove-mock-data-roadmap`
- Required post-spec curl skill: `multi-agent-curl-test`

Accept overrides only if the user explicitly provides them.

## Preparation

1. Load `remove_mock_data_specs.md`.
2. Run the extractor to build or refresh per-spec prompt bundles:

```bash
uv run python .agents/skills/speckit-remove-mock-data-autopilot/scripts/extract_remove_mock_data_specs.py \
  --roadmap remove_mock_data_specs.md \
  --output specs/_autopilot/remove-mock-data-roadmap
```

3. Read the generated `specs/_autopilot/remove-mock-data-roadmap/queue.json`.
4. Confirm every spec from `048` through `059` has these phase prompt files:
   `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, and
   `implement.md`.
5. Dry-run every generated validation manifest before starting Spec `048`:

```bash
set -e
for f in specs/_autopilot/remove-mock-data-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
  uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
done
```

6. Confirm the prior React UI roadmaps are complete before starting:
   - `specs/_autopilot/react-ui-roadmap/queue.json` exists when available.
   - `specs/_autopilot/react-ui2-roadmap/queue.json` exists and has
     `next_spec` set to `null` when status data is present.
   - Specs `026` through `047` exist with completed QA artifacts, especially
     `specs/047-jinja-infrastructure-decommission`.
   Stop before Spec `048` if this prerequisite is not true.
7. Read the active constitution, current git status, `AGENTS.md`, the completed
   React/Jinja decommission artifacts from Specs `026` through `047`, the
   current database/mock-data inventory from `remove_mock_data_specs.md`, and
   `curl_testing.md` before starting.

The extractor writes deterministic feature directories such as
`specs/048-live-data-inventory-and-mock-guardrails`, branches such as
`codex/048-live-data-inventory-and-mock-guardrails`, QA env names such as
`.env.qa048`, and validation manifests extending
`specs/_autopilot/shared/validation.base.yml`.

## Queue State Bookkeeping

Treat `specs/_autopilot/remove-mock-data-roadmap/queue.json` as the durable
queue state, not merely a generated manifest.

- Update the active spec entry in `queue.json` at every phase boundary:
  `specify`, `clarify`, `plan`, `tasks`, `analyze`, and `implement`.
- Update `queue.json` immediately after all validation passes: set the active
  spec `status` and `validation` to `completed`, set every completed phase to
  `completed`, and advance `next_spec` to the next pending spec.
- If a phase, validation command, Playwright flow, post-UI API/database check,
  curl test, or stop condition fails, set that spec's `status` to `blocked` or
  `in_progress` as appropriate, keep `next_spec` pointing at that spec, and
  record the detailed blocker in that spec's `status.json`.
- Keep `queue.json` and each spec's `status.json` consistent before moving to
  another spec. If they disagree on resume, trust the richer `status.json`
  evidence only after checking artifacts and validation output, then reconcile
  `queue.json` before continuing.
- Validate queue edits with
  `jq . specs/_autopilot/remove-mock-data-roadmap/queue.json` before starting
  the next phase or spec.

## Per-Spec Loop

For each generated spec entry in ascending order:

1. Set `.specify/feature.json` to the active feature only through the normal
   Spec Kit phase flow; do not hand-edit it unless recovering from an
   interrupted run and the file points at the wrong already-created feature
   directory.
2. Use the existing Spec Kit phase skills in this order:
   `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`,
   `speckit-analyze`, and `speckit-implement`.
3. Do not skip a phase. Load and use the generated phase prompt file for the
   current phase and current spec number.
4. For `/speckit.specify`, use the generated `specify.md` content exactly,
   including `SPECIFY_FEATURE_DIRECTORY` and `GIT_BRANCH_NAME`.
5. For clarification, run in autonomous mode:
   - Prefer the roadmap's recommended defaults.
   - Auto-answer only low-risk questions directly covered by
     `remove_mock_data_specs.md`, current spec artifacts, or established repo
     patterns.
   - Record every auto-choice in `spec.md` under `## Clarifications` with
     `(autopilot)` in the answer.
   - Stop and ask the user when the answer changes tenant isolation, role
     boundaries, secret handling, destructive data behavior, production
     provider calls, irreversible migration behavior, live-data deletion,
     credential readiness semantics, compatibility route behavior, or
     approval/resume semantics.
6. Run planning and task generation using the generated `plan.md` and
   `tasks.md` phase prompts. Keep tasks file-specific, dependency ordered, and
   explicit about Auth0-shaped backend tests, local-principal Playwright
   validation, live seeded data, and empty database behavior.
7. Run analysis after tasks:
   - Treat CRITICAL findings as blockers.
   - Auto-remediate CRITICAL/HIGH findings only when the fix is local to
     `spec.md`, `plan.md`, or `tasks.md` and follows explicit roadmap/default
     guidance.
   - Rerun analysis after remediation, up to two loops.
   - Do not implement with remaining CRITICAL findings.
8. Implement only the active spec's tasks. Mark tasks complete as they land.
   Remove deterministic production data only from the active spec's bounded
   surface. Preserve test fixtures under test-only paths.
9. Update `status.json` after each completed phase with the phase name, spec
   number, artifact paths, and any blocker or remediation applied.
10. Update the matching phase in `queue.json` to `completed` after each phase
    completes. Do not leave a completed phase as `pending`.

## Live Data Rules

- Production React routes must return live repository-backed data, computed
  system metadata, or truthful empty/denied/unavailable states only.
- Do not replace backend fixture data with frontend fixture data.
- Do not hide fixed data behind a new service abstraction. The service must
  read persisted state or explicitly report empty/unavailable state.
- Test fixtures may remain under `tests/`, `frontend/admin/src/test`, and
  documented QA seed helpers, but production routes cannot import or mirror
  them.
- QA seed data must be created through documented setup flows, domain services,
  repositories, migrations intended for QA, or public/admin APIs. It must not
  be returned by production builders unless it is actually persisted.
- Every route must be validated in both an empty live database state and a
  seeded live database state when the spec touches route data.

## Playwright And Backend Persistence Rules

Playwright validation is mandatory after every spec and must exercise the UI,
not only load a page.

- Reconcile the generated Playwright flow with the actual implemented UI before
  running validation.
- For domain specs with safe mutations, the Playwright flow must perform at
  least one user-visible action that writes through the backend API or domain
  service, such as saving a workflow draft, creating an export, creating a test
  suite/case/run, updating readiness/configuration, creating an invitation, or
  updating a channel/preference setting.
- After the Playwright action, verify persistence through a backend API first
  and a direct QA database query when the API cannot expose the needed evidence
  safely. Record the exact API or database check in the spec's `status.json`
  and QA evidence.
- For non-mutating specs, such as inventory, scanner, or terminology cleanup,
  Playwright must still exercise representative navigation and the validation
  must verify route/bootstrap JSON or database state proves the UI is not using
  forbidden fixed data.
- If Playwright fails, diagnose and fix the active spec, rerun Playwright, and
  rerun any downstream API/database check affected by the fix.
- Do not start the next spec while a route only proves browser-rendered state
  without API/database-backed evidence.

## Validation After Every Spec

Validation is mandatory before starting the next spec.

1. Ensure implementation produced:
   - `qaNNN.md`
   - `qaNNN_ui.md`
   - `.env.qaNNN`
   - `qaNNN_user_guide.md`
   - PR notes or reviewer notes requested by tasks
2. Reconcile the generated validation manifest with the actual route(s),
   UI actions, and post-UI persistence checks from the implementation. If the
   generated Playwright route hint is stale or too shallow, update only that
   spec's `validation.yml` before running validation.
3. Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

4. Run API/database/quality validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/NNN-slug/validation.yml
```

5. Run Playwright UI validation with database setup and app processes:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/NNN-slug/validation.yml --start-processes
```

The shared validation base backs up `.env`, copies the spec QA env, runs
`uv sync`, starts PostgreSQL, drops/recreates only the allowed QA database,
applies Alembic migrations, seeds local tenants, starts API and worker
processes, and captures Playwright screenshots.

6. Verify the Playwright action updated or reflected the backend via API or QA
   database evidence. Prefer an HTTP API assertion against the same route/data
   the UI uses; use a direct SQL query only for redaction-safe internal
   evidence. Save the command, result summary, and evidence path in
   `status.json`.
7. Run the `multi-agent-curl-test` skill after the spec-specific UI/API
   validation has passed:

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/qaNNN-after-spec
```

The curl test owns its separate `multi_agent_curl_test` database and restarts
the API server on its own. Do not run it inside `run_spec_qa.py` while that
script's managed API process is still active.

8. If any validation fails, diagnose the failure, fix the active spec only, and
   rerun the failed command plus any downstream validation affected by the fix.
   Continue the repair loop until validation passes or a stop condition is
   reached.
9. Do not start the next spec until QA docs, API/database/quality validation,
   Playwright validation, post-UI API/database verification, and
   `multi-agent-curl-test` all pass for the active spec.
10. Update the generated `status.json` with completed phases, validation
    commands, Playwright screenshots, post-UI API/database evidence, curl-test
    artifact directory, and any blocker.
11. Update `queue.json` before moving on: set the active spec `status` and
    `validation` to `completed`, ensure all phase values are `completed`, and
    set `next_spec` to the next pending spec number. When Spec `059`
    completes, set `next_spec` to `null`.

## Stop Conditions

Stop the overnight run and report clearly when any of these happen:

- Security, tenant isolation, audit, redaction, credential, secret, production
  resource, or external side-effect behavior is ambiguous.
- A command would reset or mutate a database other than the active QA database
  or the dedicated `multi_agent_curl_test` database owned by
  `multi-agent-curl-test`.
- A spec requires real Auth0, Telegram, provider, credential, connector, or
  outbound calls that are not explicitly mocked or approved in its artifacts.
- A production route still returns deterministic fixture/demo data and the
  correct repository/service source is ambiguous.
- A Playwright action cannot safely prove backend API/database persistence.
- A visible UI route cannot be exercised because selectors or flows are unclear
  after one focused repair pass.
- `multi-agent-curl-test` fails after the active-spec repair attempt.
- Analysis still has CRITICAL findings after two remediation loops.
- QA docs, backend quality gates, frontend quality gates, scanners,
  API/database checks, or Playwright fail after a focused repair attempt.
- Existing unrelated user changes block implementation.

## Progress Reporting

Keep a concise status trail:

- Current spec number/title and active phase.
- Auto-clarifications selected.
- Analysis findings remediated or left outstanding.
- Completed task count.
- Removed or retained deterministic data surfaces.
- Empty-state and seeded-data evidence paths.
- Playwright commands, UI actions exercised, screenshots, and post-UI
  API/database verification.
- `multi-agent-curl-test` command result and artifact directory.
- Next spec to run or exact blocker.

When resuming, read `queue.json`, `status.json`, `.specify/feature.json`, git
status, the active feature's `tasks.md`, latest Playwright output, latest
curl-test artifact directory, and the current live-data inventory before doing
more work.
