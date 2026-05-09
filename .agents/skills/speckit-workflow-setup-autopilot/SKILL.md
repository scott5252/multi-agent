---
name: speckit-workflow-setup-autopilot
description: Run the custom workflow setup UI roadmap in docs/workflow_setup_specs.md as an autonomous Spec Kit sequence for specs 069 through 073, generating durable specs/_autopilot entries, implementing each spec without per-spec pauses, updating curl_testing.md for new or changed APIs, running API/database/frontend quality checks, and validating the browser UI with Playwright after every spec.
---

# Speckit Workflow Setup Autopilot

Use this skill when the user asks to prepare, run, or resume the Custom
Workflow Setup UI roadmap from `docs/workflow_setup_specs.md`.

This skill is intentionally sequential: create, implement, and validate one
spec at a time from `069` through `073`. Never run these specs in parallel.

This is an autonomous Codex runbook, not a standalone background daemon. When
the user invokes it, Codex must keep working through the queue until every spec
passes validation or a hard stop condition is reached. Do not pause after each
completed spec for user confirmation.

Do not create git commits, do not stage changes, and do not push branches while
running this skill. The user will handle git after the roadmap run.

## Required Inputs

Default values:

- Roadmap file: `docs/workflow_setup_specs.md`
- React UI2 context file: `docs/react_ui2.md`
- Spec range: `069..073`
- Queue output: `specs/_autopilot/workflow-setup-roadmap`
- Required post-spec curl skill: `multi-agent-curl-test`
- API regression source: `curl_testing.md`

Accept overrides only if the user explicitly provides them.

## Preparation

1. Load `docs/workflow_setup_specs.md` and `docs/react_ui2.md`. The workflow
   setup roadmap lives in `docs/`; do not fall back to a repo-root
   `workflow_setup_specs.md`.
2. Confirm Docker is available before any long run begins. On macOS, attempt to
   start Docker Desktop and wait for the daemon if it is not already running:

```bash
if ! docker info >/dev/null 2>&1; then
  command -v open >/dev/null 2>&1 && open -a Docker || true
  for i in $(seq 1 60); do
    docker info >/dev/null 2>&1 && break
    sleep 5
  done
fi
docker info >/dev/null
docker compose up -d postgres
```

   Stop before Spec `069` if Docker cannot be started; the QA, Playwright, and
   curl validations require PostgreSQL.
3. Run the extractor to build or refresh per-spec prompt bundles:

```bash
uv run python .agents/skills/speckit-workflow-setup-autopilot/scripts/extract_workflow_setup_specs.py \
  --roadmap docs/workflow_setup_specs.md \
  --output specs/_autopilot/workflow-setup-roadmap
```

4. Read the generated
   `specs/_autopilot/workflow-setup-roadmap/queue.json`.
5. Confirm every spec from `069` through `073` has these phase prompt files:
   `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, and
   `implement.md`.
6. Dry-run every generated validation manifest before starting Spec `069`:

```bash
set -e
for f in specs/_autopilot/workflow-setup-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
  uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
done
```

7. Confirm prerequisites before starting:
   - `specs/068-durable-agent-interaction-evidence-and-replay-graph` exists.
   - `specs/_autopilot/graphical-ui-roadmap/queue.json` exists and has
     `next_spec` set to `null` when status data is present.
   - `docs/react_ui2.md`, `curl_testing.md`, and the `multi-agent-curl-test`
     skill are present.
   Stop before Spec `069` only if these prerequisites are missing or clearly
   incomplete for the current repository state.
8. Read the active constitution, current git status, `AGENTS.md`,
   `docs/workflow_setup_specs.md`, `docs/react_ui2.md`, `curl_testing.md`,
   completed specs `040`, `050`, `065`, `066`, `067`, and `068` when present,
   and current workflow registry, workflow builder, governance, test bench,
   runtime, generated-contract, and React Admin implementations before
   starting.

The extractor writes deterministic feature directories such as
`specs/069-workflow-document-authoring-contracts-and-mutation-apis`, branches
such as
`codex/069-workflow-document-authoring-contracts-and-mutation-apis`, QA env
names such as `.env.qa069`, and validation manifests extending
`specs/_autopilot/shared/validation.base.yml`.

## Queue State Bookkeeping

Treat `specs/_autopilot/workflow-setup-roadmap/queue.json` as durable queue
state, not merely a generated manifest.

- Update the active spec entry in `queue.json` at every phase boundary:
  `specify`, `clarify`, `plan`, `tasks`, `analyze`, and `implement`.
- Update `queue.json` immediately after all validation passes: set the active
  spec `status` and `validation` to `completed`, set every completed phase to
  `completed`, and advance `next_spec` to the next pending spec.
- If a phase, validation command, Playwright flow, API/curl regression update,
  curl test, or stop condition fails, set that spec's `status` to `blocked` or
  `in_progress` as appropriate, keep `next_spec` pointing at that spec, and
  record the detailed blocker in that spec's `status.json`.
- Keep `queue.json` and each spec's `status.json` consistent before moving to
  another spec. If they disagree on resume, trust the richer `status.json`
  evidence only after checking artifacts and validation output, then reconcile
  `queue.json` before continuing.
- Validate queue edits with
  `jq . specs/_autopilot/workflow-setup-roadmap/queue.json` before starting
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
   - Prefer the roadmap's recommended defaults and established repo patterns.
   - Auto-answer low-risk questions directly covered by
     `docs/workflow_setup_specs.md`, `docs/react_ui2.md`, current spec
     artifacts, completed prior specs, or existing workflow registry,
     governance, test bench, runtime, generated-contract, React Admin, and
     Playwright patterns.
   - Record every auto-choice in `spec.md` under `## Clarifications` with
     `(autopilot)` in the answer.
   - Stop and ask the user only when the answer changes tenant isolation, role
     boundaries, secret handling, destructive data behavior, production
     provider calls, real external side effects, irreversible migration
     behavior, approval/resume semantics, raw prompt/completion exposure, raw
     test transcript exposure, credential readiness behavior, or publish-gate
     trust semantics.
6. Run planning and task generation using the generated `plan.md` and
   `tasks.md` phase prompts. Keep tasks file-specific, dependency ordered, and
   explicit about Auth0-shaped backend tests, `AUTH_MODE=local_principal`
   Playwright validation, deterministic QA/model mocks, generated TypeScript
   updates, frontend tests, UI accessibility checks, curl_testing updates, and
   multi-agent curl regression.
7. Run analysis after tasks:
   - Treat CRITICAL findings as blockers.
   - Auto-remediate CRITICAL/HIGH findings only when the fix is local to
     `spec.md`, `plan.md`, or `tasks.md` and follows explicit roadmap/default
     guidance.
   - Rerun analysis after remediation, up to two loops.
   - Do not implement with remaining CRITICAL findings.
8. Implement only the active spec's tasks. Mark tasks complete as they land.
   Keep the custom workflow setup experience browser-first, backend-authorized,
   tenant-scoped, redaction-safe, keyboard-accessible, reload-persistent, and
   deterministic in local QA.
9. If the spec adds, removes, renames, or behaviorally changes any public JSON,
   admin JSON, workflow, prompt/profile, test-bench, runtime, design-review,
   operations, or workflow setup API, update `curl_testing.md` in the same spec
   before validation. Add commands that can run in the dedicated
   `multi_agent_curl_test` database with local-principal auth and deterministic
   data setup. If a changed API breaks an existing curl command, update the
   command and expected response so it reflects the new supported contract.
10. Update `status.json` after each completed phase with the phase name, spec
    number, artifact paths, curl_testing changes, UI evidence, and any blocker
    or remediation applied.
11. Update the matching phase in `queue.json` to `completed` after each phase
    completes. Do not leave a completed phase as `pending`.

## Workflow Setup Implementation Rules

- Use backend-owned JSON contracts generated from Pydantic schemas for every
  React workflow setup mutation. Do not move authorization, tenant scoping,
  workflow validation, prompt/profile validation, credential readiness, publish
  readiness, redaction, or audit decisions into browser-only logic.
- Build on the existing React Admin shell, workflow registry, workflow builder,
  governance, test bench, operations, runtime graph, interaction replay, and
  generated TypeScript patterns. Do not create a second admin app or an
  alternate raw-JSON workflow editor.
- A clean tenant must be able to create and publish a custom multi-agent
  workflow through visible UI controls only. After login, QA guides and
  Playwright journeys must navigate through links, nav items, buttons, menus,
  tabs, row actions, and in-page links rather than hand-editing browser URLs.
- Every graph canvas or topology editor must have keyboard-readable node and
  edge lists with equivalent safe information. Verify desktop and mobile
  screenshots for nonblank rendering, stable framing, no text overlap, and
  usable controls.
- Preserve truthful empty, denied, partial, loading, stale, dirty, conflict,
  validation, blocked-publish, and error states. No production UI may invent
  fake workflows, fake agents, fake prompts, fake profiles, fake evidence, fake
  runs, or sample runtime records.
- Raw secrets, credential values, provider authorization headers, raw prompts
  outside authorized edit forms, raw completions, memory contents, raw run
  payloads, private channel messages, raw tool payloads, raw test transcripts,
  link tokens after creation, local filesystem paths, stack traces, and
  unauthorized tenant labels must never appear in React UI, redirects, exports,
  screenshots, QA artifacts, logs, docs, or audit summaries.
- Publish readiness must remain backend-owned and must reject stale, missing,
  failed, cross-tenant, or synthetic validation and test evidence.
- The final Spec `073` Playwright journey must prove a user can create a custom
  workflow with at least three agents, create or select prompts/profiles for
  each agent, build a graph with a join node, create required evidence,
  validate, publish, launch or select the workflow, and inspect runtime graph
  evidence.

## Validation After Every Spec

Validation is mandatory before starting the next spec.

1. Ensure implementation produced:
   - `qaNNN.md`
   - `qaNNN_ui.md`
   - `.env.qaNNN`
   - `qaNNN_user_guide.md`
   - PR notes or reviewer notes requested by tasks
2. Reconcile the generated validation manifest with the actual route(s), UI
   actions, API/database checks, seeded workflow/prompt/profile/test evidence,
   and browser journeys from the implementation. If the generated Playwright
   route hint is stale or too shallow, update only that spec's `validation.yml`
   before running validation.
3. Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

4. Run API/database/backend/frontend quality validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/NNN-slug/validation.yml
```

   The generated validation manifests include frontend quality commands for
   Admin React work: generated TypeScript freshness, `npm ci`,
   `npm run typecheck`, `npm test`, and `npm run build` under
   `frontend/admin`.
5. Run Playwright UI validation with database setup and app processes:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/NNN-slug/validation.yml --start-processes
```

   Every spec must have at least one Playwright flow. Specs `070` through `073`
   must strengthen the generated smoke flow into UI journeys that exercise the
   newly implemented workflow setup controls, desktop and mobile screenshots,
   keyboard-readable alternatives, persisted reload, and no-overlap checks.
6. Verify API coverage before the curl regression:
   - If the spec introduced new APIs, confirm `curl_testing.md` contains a
     sequential setup command and at least one success-path command for each
     new route family.
   - If an API contract changed, confirm the old curl command has been updated
     or replaced with the new supported contract and expected status/body.
   - Record the route family, `curl_testing.md` section, and evidence summary
     in `status.json`.
7. Run the `multi-agent-curl-test` skill after the spec-specific UI/API
   validation has passed. Ensure PostgreSQL is running first because the curl
   runner owns database recreation but does not start the Docker service:

```bash
if ! docker info >/dev/null 2>&1; then
  command -v open >/dev/null 2>&1 && open -a Docker || true
  for i in $(seq 1 60); do
    docker info >/dev/null 2>&1 && break
    sleep 5
  done
fi
docker info >/dev/null
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/qaNNN-after-spec
```

   The curl test owns its separate `multi_agent_curl_test` database and
   restarts the API server on its own. Do not run it inside `run_spec_qa.py`
   while that script's managed API process is still active.
8. If any validation fails, diagnose the failure, fix the active spec only, and
   rerun the failed command plus any downstream validation affected by the fix.
   Continue the repair loop until validation passes or a stop condition is
   reached.
9. Do not start the next spec until QA docs, API/database/backend/frontend
   validation, Playwright UI validation, curl_testing coverage review, and
   `multi-agent-curl-test` all pass for the active spec.
10. Update the generated `status.json` with completed phases, validation
    commands, Playwright screenshots, curl_testing coverage evidence,
    curl-test artifact directory, and any blocker.
11. Update `queue.json` before moving on: set the active spec `status` and
    `validation` to `completed`, ensure all phase values are `completed`, and
    set `next_spec` to the next pending spec number. When Spec `073`
    completes, set `next_spec` to `null`.

## Final Stability Gate

After Spec `073` completes, run a final whole-roadmap stability pass before
declaring the roadmap finished. Do not skip this gate even if every per-spec
validation already passed.

1. Confirm durable state says the roadmap is complete:

```bash
jq -e '.next_spec == null and all(.specs[]; .status == "completed" and .validation == "completed")' \
  specs/_autopilot/workflow-setup-roadmap/queue.json
```

2. Re-run QA document validation for every generated feature directory:

```bash
set -e
for d in specs/069-workflow-document-authoring-contracts-and-mutation-apis \
  specs/070-react-workflow-graph-and-agent-role-builder \
  specs/071-prompt-profile-creation-and-per-agent-binding-ui \
  specs/072-custom-workflow-test-evidence-and-publish-setup \
  specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch; do
  bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$d"
done
```

3. Re-run all generated API/database/frontend validation manifests:

```bash
set -e
for f in specs/_autopilot/workflow-setup-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f"
done
```

4. Re-run all generated Playwright UI validations:

```bash
set -e
for f in specs/_autopilot/workflow-setup-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_playwright_ui.py "$f" --start-processes
done
```

5. Run final repository-level backend, frontend, generated-contract, and curl
   regressions:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/frontend/generate_admin_react_types.py --check
(cd frontend/admin && npm ci)
(cd frontend/admin && npm run typecheck)
(cd frontend/admin && npm test)
(cd frontend/admin && npm run build)
if ! docker info >/dev/null 2>&1; then
  command -v open >/dev/null 2>&1 && open -a Docker || true
  for i in $(seq 1 60); do
    docker info >/dev/null 2>&1 && break
    sleep 5
  done
fi
docker info >/dev/null
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --output-dir .data/curl_test_runs/workflow-setup-final
```

6. Update `specs/_autopilot/workflow-setup-roadmap/status.json` with the final
   stability commands, Playwright output directories, curl-test artifact
   directory, and any remaining risk. Only report the run as complete when this
   gate passes.

## Stop Conditions

Stop the roadmap run and report clearly when any of these happen:

- Security, tenant isolation, audit, redaction, credential, secret, production
  resource, or external-side-effect behavior is ambiguous.
- A command would reset or mutate a database other than the active QA database
  or the dedicated `multi_agent_curl_test` database owned by
  `multi-agent-curl-test`.
- A spec requires real Auth0, Telegram, provider, credential, connector, model,
  or outbound calls that are not explicitly mocked or approved in its
  artifacts.
- A production Admin route would synthesize fake workflows, fake agents, fake
  prompts, fake profiles, fake evidence, fake runs, or sample interaction
  records.
- A new or changed API cannot be represented safely in `curl_testing.md`.
- Raw prompts, completions, secrets, credentials, provider payloads, test
  transcripts, private channel payloads, memory contents, stack traces, local
  filesystem paths, or unauthorized tenant labels would be exposed in UI,
  exports, screenshots, QA artifacts, logs, docs, or audit summaries.
- Publish readiness would rely on browser-only checks instead of backend-owned
  validation and evidence.
- `multi-agent-curl-test` fails after the active-spec repair attempt.
- Analysis still has CRITICAL findings after two remediation loops.
- QA docs, backend quality gates, frontend quality gates, API/database checks,
  or Playwright fail after a focused repair attempt.
- Existing unrelated user changes block implementation.

## Progress Reporting

Keep a concise status trail:

- Current spec number/title and active phase.
- Auto-clarifications selected.
- Analysis findings remediated or left outstanding.
- Completed task count.
- New or changed API routes and `curl_testing.md` coverage status.
- Browser controls exercised, Playwright commands, desktop/mobile screenshots,
  accessibility checks, and API/database evidence.
- `multi-agent-curl-test` command result and artifact directory.
- Next spec to run or exact blocker.

When resuming, read `queue.json`, root and per-spec `status.json`,
`.specify/feature.json`, git status, the active feature's `tasks.md`, latest
Playwright output, latest curl-test artifact directory, `curl_testing.md`,
`docs/workflow_setup_specs.md`, and the current workflow setup artifacts before
doing more work.
