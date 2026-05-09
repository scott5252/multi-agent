---
name: "speckit-graphical-ui"
description: "Run the graphical agent workflow UI roadmap in graphical_ui.md as an autonomous Spec Kit sequence for specs 065 through 068, generating durable _autopilot entries, implementing each spec without per-spec pauses, updating curl_testing.md for new or changed APIs, running multi-agent-curl-test after every spec, and validating UI behavior with Playwright after every spec."
compatibility: "Requires this multi-agent repo, graphical_ui.md, completed specs 060-064 context when available, Spec Kit skills, specs/_autopilot/shared policy and validation bases, PostgreSQL/Docker, uv, Playwright, curl_testing.md, and the multi-agent-curl-test skill."
metadata:
  author: "multi-agent-project"
---

# Speckit Graphical UI

Use this skill when the user asks to run, prepare, or resume the Graphical
Agent Workflow UI roadmap from `graphical_ui.md`.

This skill is intentionally sequential: create, implement, and validate one
spec at a time from `065` through `068`. Never run these specs in parallel.

This is an autonomous Codex runbook, not a standalone background daemon. When
the user invokes it, Codex must keep working through the queue until every spec
passes validation or a hard stop condition is reached. Do not pause after each
spec for user confirmation.

Do not create git commits, do not stage changes, and do not push branches while
running this skill. The user will handle git after the overnight run.

## Required Inputs

Default values:

- Roadmap file: `graphical_ui.md`
- Spec range: `065..068`
- Queue output: `specs/_autopilot/graphical-ui-roadmap`
- Required post-spec curl skill: `multi-agent-curl-test`
- API regression source: `curl_testing.md`

Accept overrides only if the user explicitly provides them.

## Preparation

1. Load `graphical_ui.md`.
2. Confirm Docker is available before any overnight work begins. On macOS,
   attempt to start Docker Desktop and wait for the daemon if it is not already
   running:

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

   Stop before Spec `065` if Docker cannot be started; the QA and curl
   validations require PostgreSQL.
3. Run the extractor to build or refresh per-spec prompt bundles:

```bash
uv run python .agents/skills/speckit-graphical-ui/scripts/extract_graphical_ui_specs.py \
  --roadmap graphical_ui.md \
  --output specs/_autopilot/graphical-ui-roadmap
```

4. Read the generated
   `specs/_autopilot/graphical-ui-roadmap/queue.json`.
5. Confirm every spec from `065` through `068` has these phase prompt files:
   `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, and
   `implement.md`.
6. Dry-run every generated validation manifest before starting Spec `065`:

```bash
set -e
for f in specs/_autopilot/graphical-ui-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
  uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
done
```

7. Confirm prerequisites before starting:
   - `specs/064-design-reviewer-template-test-bench-and-publish-gates` exists
     when the Design Reviewer scenario roadmap has already been implemented.
   - `specs/_autopilot/scenario-enhancement-roadmap/queue.json` exists and has
     `next_spec` set to `null` when status data is present.
   - `curl_testing.md` exists and the `multi-agent-curl-test` skill is present.
   Stop before Spec `065` only if these prerequisites are missing or clearly
   incomplete for the current repository state.
8. Read the active constitution, current git status, `AGENTS.md`,
   `graphical_ui.md`, `curl_testing.md`, completed specs `060` through `064`
   when present, the workflow builder implementation, the operations/run-debug
   implementation, and current runtime graph/run-step/timeline services before
   starting.

The extractor writes deterministic feature directories such as
`specs/065-agent-communication-graph-contracts-and-projections`, branches such
as `codex/065-agent-communication-graph-contracts-and-projections`, QA env
names such as `.env.qa065`, and validation manifests extending
`specs/_autopilot/shared/validation.base.yml`.

## Queue State Bookkeeping

Treat `specs/_autopilot/graphical-ui-roadmap/queue.json` as the durable queue
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
  `jq . specs/_autopilot/graphical-ui-roadmap/queue.json` before starting the
  next phase or spec.

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
   - Auto-answer low-risk questions directly covered by `graphical_ui.md`,
     current spec artifacts, completed prior specs, or existing workflow
     registry/runtime/operations/React/Admin/test patterns.
   - Record every auto-choice in `spec.md` under `## Clarifications` with
     `(autopilot)` in the answer.
   - Stop and ask the user only when the answer changes tenant isolation, role
     boundaries, secret handling, destructive data behavior, production
     provider calls, real external side effects, irreversible migration
     behavior, manual-resolution semantics, approval/exception policy, raw
     artifact/prompt/completion exposure, or whether Spec `068` should create
     durable interaction evidence despite existing runtime evidence being
     sufficient.
6. Run planning and task generation using the generated `plan.md` and
   `tasks.md` phase prompts. Keep tasks file-specific, dependency ordered, and
   explicit about Auth0-shaped backend tests, local-principal Playwright
   validation, deterministic QA/model mocks, generated TypeScript updates,
   curl_testing updates, and multi-agent curl regression.
7. Run analysis after tasks:
   - Treat CRITICAL findings as blockers.
   - Auto-remediate CRITICAL/HIGH findings only when the fix is local to
     `spec.md`, `plan.md`, or `tasks.md` and follows explicit roadmap/default
     guidance.
   - Rerun analysis after remediation, up to two loops.
   - Do not implement with remaining CRITICAL findings.
8. Implement only the active spec's tasks. Mark tasks complete as they land.
   Keep the graphical agent workflow UI additive, tenant-scoped,
   redaction-safe, keyboard-readable, and deterministic in local QA unless a
   spec explicitly uses mocked model-gateway responses.
9. If the spec adds, removes, renames, or behaviorally changes any public JSON,
   admin JSON, health, runtime, workflow, test-bench, governance, operations,
   or graphical agent workflow API, update `curl_testing.md` in the same spec
   before validation. Add commands that can run in the dedicated
   `multi_agent_curl_test` database with local-principal auth and deterministic
   data setup. If a changed API breaks an existing curl command, update the
   command and expected response so it reflects the new supported contract.
10. Update `status.json` after each completed phase with the phase name, spec
    number, artifact paths, curl_testing changes, and any blocker or
    remediation applied.
11. Update the matching phase in `queue.json` to `completed` after each phase
    completes. Do not leave a completed phase as `pending`.

## Graphical UI Implementation Rules

- Use backend-owned graph projections as the source of truth. Do not invent
  graph records, agent rows, runtime runs, messages, or sample agents on
  production routes.
- Extend existing React workflow builder, React Flow, operations workbench,
  run-debug, generated TypeScript, and Admin Shell patterns rather than adding
  a second visualization framework.
- The first design-time graph viewer remains read-only. Do not expand graph
  editing unless a later spec explicitly asks for editable communication edges.
- Every canvas graph must have a keyboard-readable node and edge list with
  equivalent safe information.
- Preserve truthful empty, denied, partial, loading, stale, and error states.
- Avoid overlapping text and nested cards in graph panels. Verify desktop and
  mobile Playwright screenshots for legibility.
- Do not store, render, log, export, or include in QA artifacts raw prompts,
  completions, secrets, provider authorization headers, private channel
  payloads, memory contents, unauthorized payloads, stack traces, or raw
  external tool payloads.
- Runtime graph support must be inferred from existing durable run steps,
  timeline events, handoffs, gateway attempts, tool summaries, delivery
  summaries, artifacts, and lineage before adding new persistence.
- Spec `068` is allowed to add durable interaction evidence only after Specs
  `065` through `067` prove existing runtime evidence is insufficient for the
  replay graph. If existing evidence is sufficient, record the decision in the
  Spec `068` artifacts and avoid unnecessary migrations or idle tables.
- New interaction evidence, if needed, must store safe summaries,
  classifications, references, digests, status, timing, provenance, and
  idempotency keys only.

## Validation After Every Spec

Validation is mandatory before starting the next spec.

1. Ensure implementation produced:
   - `qaNNN.md`
   - `qaNNN_ui.md`
   - `.env.qaNNN`
   - `qaNNN_user_guide.md`
   - PR notes or reviewer notes requested by tasks
2. Reconcile the generated validation manifest with the actual route(s), UI
   actions, API/database checks, and seeded graph/run evidence from the
   implementation. If the generated Playwright route hint is stale or too
   shallow, update only that spec's `validation.yml` before running validation.
3. Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

4. Run API/database/quality validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/NNN-slug/validation.yml
```

   The generated validation manifests must include frontend quality commands
   for any spec touching Admin React code: generated TypeScript freshness,
   `npm ci`, `npm run typecheck`, `npm test`, and `npm run build` under
   `frontend/admin`.
5. Run Playwright UI validation with database setup and app processes:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/NNN-slug/validation.yml --start-processes
```

The shared validation base backs up `.env`, copies the spec QA env, runs
`uv sync`, starts PostgreSQL, drops/recreates only the allowed QA database,
applies Alembic migrations, seeds local tenants, starts API and worker
processes, and captures Playwright screenshots.

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

The curl test owns its separate `multi_agent_curl_test` database and restarts
the API server on its own. Do not run it inside `run_spec_qa.py` while that
script's managed API process is still active.

8. If any validation fails, diagnose the failure, fix the active spec only, and
   rerun the failed command plus any downstream validation affected by the fix.
   Continue the repair loop until validation passes or a stop condition is
   reached.
9. Do not start the next spec until QA docs, API/database/quality validation,
   Playwright validation, curl_testing coverage review, and
   `multi-agent-curl-test` all pass for the active spec.
10. Update the generated `status.json` with completed phases, validation
    commands, Playwright screenshots, curl_testing coverage evidence,
    curl-test artifact directory, and any blocker.
11. Update `queue.json` before moving on: set the active spec `status` and
    `validation` to `completed`, ensure all phase values are `completed`, and
    set `next_spec` to the next pending spec number. When Spec `068`
    completes, set `next_spec` to `null`.

## Final Stability Gate

After Spec `068` completes, run a final whole-roadmap stability pass before
declaring the overnight run finished. Do not skip this gate even if every
per-spec validation already passed.

1. Confirm durable state says the roadmap is complete:

```bash
jq -e '.next_spec == null and all(.specs[]; .status == "completed" and .validation == "completed")' \
  specs/_autopilot/graphical-ui-roadmap/queue.json
```

2. Re-run QA document validation for every generated feature directory:

```bash
set -e
for d in specs/065-agent-communication-graph-contracts-and-projections \
  specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions \
  specs/067-runtime-agent-communication-graph-for-runs \
  specs/068-durable-agent-interaction-evidence-and-replay-graph; do
  bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$d"
done
```

3. Re-run all generated API/database/quality validation manifests:

```bash
set -e
for f in specs/_autopilot/graphical-ui-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f"
done
```

4. Re-run all generated Playwright validations:

```bash
set -e
for f in specs/_autopilot/graphical-ui-roadmap/*/validation.yml; do
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
  --output-dir .data/curl_test_runs/graphical-ui-final
```

6. Update `specs/_autopilot/graphical-ui-roadmap/status.json` with the final
   stability commands, Playwright output directories, curl-test artifact
   directory, and any remaining risk. Only report the run as complete when this
   gate passes.

## Stop Conditions

Stop the overnight run and report clearly when any of these happen:

- Security, tenant isolation, audit, redaction, credential, secret, production
  resource, or external side-effect behavior is ambiguous.
- A command would reset or mutate a database other than the active QA database
  or the dedicated `multi_agent_curl_test` database owned by
  `multi-agent-curl-test`.
- A spec requires real Auth0, Telegram, provider, credential, connector, model,
  or outbound calls that are not explicitly mocked or approved in its
  artifacts.
- A production Admin route would synthesize fake workflow graphs, fake agent
  runs, fake runtime evidence, or sample interaction records.
- A new or changed API cannot be represented safely in `curl_testing.md`.
- Spec `068` would add durable interaction persistence without evidence that
  existing run steps, timeline events, handoffs, artifacts, gateway attempts,
  and tool summaries are insufficient.
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
- Playwright commands, UI actions exercised, screenshots, and API/database
  evidence.
- `multi-agent-curl-test` command result and artifact directory.
- Next spec to run or exact blocker.

When resuming, read `queue.json`, `status.json`, `.specify/feature.json`, git
status, the active feature's `tasks.md`, latest Playwright output, latest
curl-test artifact directory, `curl_testing.md`, and the current graphical
agent workflow artifacts before doing more work.
