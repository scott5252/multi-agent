---
name: "speckit-scenario-enhance"
description: "Run the Design Reviewer Scenario Enhancement roadmap in scenario_enhancement.md as an autonomous Spec Kit sequence for specs 060 through 064, generating durable _autopilot entries, implementing each spec without per-spec pauses, updating curl_testing.md for new or changed APIs, and running multi-agent-curl-test after every spec."
compatibility: "Requires this multi-agent repo, scenario_enhancement.md, completed specs 048-059 context, Spec Kit skills, specs/_autopilot/shared policy and validation bases, PostgreSQL/Docker, uv, Playwright, curl_testing.md, and the multi-agent-curl-test skill."
metadata:
  author: "multi-agent-project"
---

# Speckit Scenario Enhance

Use this skill when the user asks to run, prepare, or resume the Design
Reviewer Scenario Enhancement roadmap from `scenario_enhancement.md`.

This skill is intentionally sequential: create, implement, and validate one
spec at a time from `060` through `064`. Never run these specs in parallel.

This is an autonomous Codex runbook, not a standalone background daemon. When
the user invokes it, Codex must keep working through the queue until every spec
passes validation or a hard stop condition is reached. Do not pause after each
spec for user confirmation.

Do not create git commits, do not stage changes, and do not push branches while
running this skill. The user will handle git after the overnight run.

## Required Inputs

Default values:

- Roadmap file: `scenario_enhancement.md`
- Spec range: `060..064`
- Queue output: `specs/_autopilot/scenario-enhancement-roadmap`
- Required post-spec curl skill: `multi-agent-curl-test`
- API regression source: `curl_testing.md`

Accept overrides only if the user explicitly provides them.

## Preparation

1. Load `scenario_enhancement.md`.
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

   Stop before Spec `060` if Docker cannot be started; the QA and curl
   validations require PostgreSQL.
3. Run the extractor to build or refresh per-spec prompt bundles:

```bash
uv run python .agents/skills/speckit-scenario-enhance/scripts/extract_scenario_enhancement_specs.py \
  --roadmap scenario_enhancement.md \
  --output specs/_autopilot/scenario-enhancement-roadmap
```

4. Read the generated
   `specs/_autopilot/scenario-enhancement-roadmap/queue.json`.
5. Confirm every spec from `060` through `064` has these phase prompt files:
   `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, and
   `implement.md`.
6. Dry-run every generated validation manifest before starting Spec `060`:

```bash
set -e
for f in specs/_autopilot/scenario-enhancement-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
  uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
done
```

7. Confirm prerequisites before starting:
   - `specs/059-admin-ui-transitional-react-label-removal` exists.
   - `specs/_autopilot/remove-mock-data-roadmap/queue.json` exists and has
     `next_spec` set to `null` when status data is present.
   - `curl_testing.md` exists and the `multi-agent-curl-test` skill is present.
   Stop before Spec `060` only if these prerequisites are missing or clearly
   incomplete.
8. Read the active constitution, current git status, `AGENTS.md`,
   `scenario_enhancement.md`, `curl_testing.md`, the completed specs `048`
   through `059`, and the current runtime/model-provider/workflow/test-bench
   implementation before starting.

The extractor writes deterministic feature directories such as
`specs/060-design-review-domain-foundation`, branches such as
`codex/060-design-review-domain-foundation`, QA env names such as `.env.qa060`,
and validation manifests extending
`specs/_autopilot/shared/validation.base.yml`.

## Queue State Bookkeeping

Treat `specs/_autopilot/scenario-enhancement-roadmap/queue.json` as the durable
queue state, not merely a generated manifest.

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
  `jq . specs/_autopilot/scenario-enhancement-roadmap/queue.json` before
  starting the next phase or spec.

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
     `scenario_enhancement.md`, current spec artifacts, completed prior specs,
     or existing domain/service/router/test patterns.
   - Record every auto-choice in `spec.md` under `## Clarifications` with
     `(autopilot)` in the answer.
   - Stop and ask the user only when the answer changes tenant isolation, role
     boundaries, secret handling, destructive data behavior, production
     provider calls, real external side effects, irreversible migration
     behavior, manual-resolution semantics, approval/exception policy, or raw
     artifact/prompt/completion exposure.
6. Run planning and task generation using the generated `plan.md` and
   `tasks.md` phase prompts. Keep tasks file-specific, dependency ordered, and
   explicit about Auth0-shaped backend tests, local-principal Playwright
   validation, deterministic QA/model mocks, curl_testing updates, and
   multi-agent curl regression.
7. Run analysis after tasks:
   - Treat CRITICAL findings as blockers.
   - Auto-remediate CRITICAL/HIGH findings only when the fix is local to
     `spec.md`, `plan.md`, or `tasks.md` and follows explicit roadmap/default
     guidance.
   - Rerun analysis after remediation, up to two loops.
   - Do not implement with remaining CRITICAL findings.
8. Implement only the active spec's tasks. Mark tasks complete as they land.
   Keep the design-review scenario additive, tenant-scoped, redaction-safe,
   and deterministic in local QA unless a spec explicitly uses mocked
   model-gateway responses.
9. If the spec adds, removes, renames, or behaviorally changes any public JSON,
   admin JSON, health, runtime, workflow, test-bench, governance, or design
   review API, update `curl_testing.md` in the same spec before validation.
   Add commands that can run in the dedicated `multi_agent_curl_test`
   database with local-principal auth and deterministic data setup. If a
   changed API breaks an existing curl command, update the command and expected
   response so it reflects the new supported contract.
10. Update `status.json` after each completed phase with the phase name, spec
    number, artifact paths, curl_testing changes, and any blocker or
    remediation applied.
11. Update the matching phase in `queue.json` to `completed` after each phase
    completes. Do not leave a completed phase as `pending`.

## Scenario Implementation Rules

- Do not introduce cyclic workflow graph execution. The coordinator must launch
  one acyclic runtime workflow run per review round.
- Do not store, render, log, export, or include in QA artifacts raw prompts,
  completions, secrets, provider authorization headers, private channel
  payloads, memory contents, unauthorized payloads, or raw external tool
  payloads.
- Production Admin routes must use live backend data, safe summaries, artifact
  references, and truthful empty/denied/unavailable states. Do not render mock
  design-review sessions, reviewer rows, quorum decisions, or handoffs.
- Model-backed role execution must fail closed when prompt/profile/provider
  pins, credentials, provider policy, output validation, redaction, or tenant
  scope is invalid. Deterministic execution must remain available for QA and
  test bench.
- Coordinator idempotency must prevent duplicate sessions, rounds, revisions,
  manual decisions, and handoffs during retries.
- Manual-resolution actions must be auditable and must not silently override
  blocking reviewer issues.
- Reusable Design Reviewer Council templates and QA evidence must be explicit
  durable setup, not hidden fixture behavior.

## Validation After Every Spec

Validation is mandatory before starting the next spec.

1. Ensure implementation produced:
   - `qaNNN.md`
   - `qaNNN_ui.md`
   - `.env.qaNNN`
   - `qaNNN_user_guide.md`
   - PR notes or reviewer notes requested by tasks
2. Reconcile the generated validation manifest with the actual route(s), UI
   actions, and API/database checks from the implementation. If the generated
   Playwright route hint is stale or too shallow, update only that spec's
   `validation.yml` before running validation.
3. Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

4. Run API/database/quality validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/NNN-slug/validation.yml
```

5. Run Playwright UI validation with database setup and app processes:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/NNN-slug/validation.yml --start-processes
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
    set `next_spec` to the next pending spec number. When Spec `064`
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
- A model-backed executor path would store or expose raw prompts, completions,
  secrets, provider payloads, private data, or memory contents outside governed
  artifacts.
- Coordinator idempotency or manual-resolution behavior is ambiguous.
- A production Admin route would synthesize fake design-review sessions,
  reviewer evidence, quorum decisions, or handoffs.
- A new or changed API cannot be represented safely in `curl_testing.md`.
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
curl-test artifact directory, `curl_testing.md`, and the current
design-review scenario artifacts before doing more work.
