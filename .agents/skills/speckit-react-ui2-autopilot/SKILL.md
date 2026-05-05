---
name: "speckit-react-ui2-autopilot"
description: "Run the React UI full Jinja removal roadmap in react_ui2.md as an autonomous Spec Kit sequence for specs 038 through 047, using each spec's specify, clarify, plan, tasks, analyze, implement prompts and validating with QA/database setup plus Playwright after every implemented spec."
compatibility: "Requires this multi-agent repo, react_ui2.md, completed or available specs 026-037 context, Spec Kit skills, specs/_autopilot/shared policy and validation bases, PostgreSQL/Docker, uv, and Playwright."
metadata:
  author: "multi-agent-project"
---

# Speckit React UI2 Autopilot

Use this skill when the user asks to run, prepare, or resume the React
TypeScript full Jinja removal roadmap from `react_ui2.md` through Spec Kit.

This skill is intentionally sequential: create, implement, and validate one
spec at a time from `038` through `047`. Never run these specs in parallel.

This is an autonomous Codex runbook, not a standalone background daemon. When
the user invokes it, Codex must keep working through the queue until every spec
passes validation or a stop condition is reached.

## Required Inputs

Default values:

- Roadmap file: `react_ui2.md`
- Spec range: `038..047`
- Queue output: `specs/_autopilot/react-ui2-roadmap`

Accept overrides only if the user explicitly provides them.

## Preparation

1. Load `react_ui2.md`.
2. Run the extractor to build or refresh per-spec prompt bundles:

```bash
uv run python .agents/skills/speckit-react-ui2-autopilot/scripts/extract_react_ui2_specs.py \
  --roadmap react_ui2.md \
  --output specs/_autopilot/react-ui2-roadmap
```

3. Read the generated `specs/_autopilot/react-ui2-roadmap/queue.json`.
4. Confirm every spec from `038` through `047` has these phase prompt files:
   `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, and
   `implement.md`.
5. Dry-run every generated validation manifest before starting Spec `038`:

```bash
set -e
for f in specs/_autopilot/react-ui2-roadmap/*/validation.yml; do
  uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
  uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
done
```

6. Read the active constitution, the completed React UI artifacts from Specs
   `026` through `037`, the current Jinja inventory state, and git status before
   starting.

The extractor writes deterministic feature directories such as
`specs/038-jinja-surface-inventory-and-deletion-plan`, branches such as
`codex/038-jinja-surface-inventory-and-deletion-plan`, QA env names such as
`.env.qa038`, and validation manifests extending
`specs/_autopilot/shared/validation.base.yml`.

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
   - Auto-answer only low-risk questions directly covered by `react_ui2.md`,
     current spec artifacts, or established repo patterns.
   - Record every auto-choice in `spec.md` under `## Clarifications` with
     `(autopilot)` in the answer.
   - Stop and ask the user when the answer changes tenant isolation, role
     boundaries, secret handling, destructive data behavior, production
     provider calls, irreversible migration behavior, legacy route retirement,
     dependency deletion, or approval/resume semantics.
6. Run planning and task generation using the generated `plan.md` and
   `tasks.md` phase prompts. Keep tasks file-specific, dependency ordered, and
   explicit about Auth0-shaped backend tests plus `AUTH_MODE=local_principal`
   Playwright validation.
7. Run analysis after tasks:
   - Treat CRITICAL findings as blockers.
   - Auto-remediate CRITICAL/HIGH findings only when the fix is local to
     `spec.md`, `plan.md`, or `tasks.md` and follows explicit roadmap/default
     guidance.
   - Rerun analysis after remediation, up to two loops.
   - Do not implement with remaining CRITICAL findings.
8. Implement only the active spec's tasks. Mark tasks complete as they land.
   Keep API/JSON routes used by React. Remove or convert only browser-rendering
   Jinja routes that the active spec proves safe to retire.
9. Update `status.json` after each completed phase with the phase name, spec
   number, artifact paths, and any blocker or remediation applied.

## Jinja Removal Rules

- Do not delete templates in Spec `038`; inventory and classify first.
- For Specs `039` through `046`, delete only the bounded Jinja templates,
  Jinja-only static assets, or browser-rendering handlers proven obsolete by
  the active spec's parity evidence.
- Every old browser route must be tested after its template is removed.
- Prefer authenticated redirects that preserve tenant id, route parameters,
  filters, saved-filter intent, and safe breadcrumbs.
- A route that cannot safely redirect must return a non-Jinja safe problem or
  documented retirement response without exposing whether unauthorized data
  exists.
- Do not remove `jinja2`, `Jinja2Templates`, `TemplateResponse`, template
  providers, or global fallback flags until Spec `047` and only after import
  scanners plus the full test suite prove no runtime path requires them.

## Validation After Every Spec

Validation is mandatory before starting the next spec.

1. Ensure implementation produced:
   - `qaNNN.md`
   - `qaNNN_ui.md`
   - `.env.qaNNN`
   - `qaNNN_user_guide.md`
   - PR notes or reviewer notes requested by tasks
2. Reconcile the generated validation manifest with the actual React route(s)
   from the implementation. If the generated Playwright route hint is stale,
   update only that spec's `validation.yml` before running validation.
3. Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

4. Run API/database/quality validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/NNN-slug/validation.yml
```

5. Run Playwright UI validation with database setup and app processes:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/NNN-slug/validation.yml --start-processes
```

The shared validation base backs up `.env`, copies the spec QA env, runs
`uv sync`, starts PostgreSQL, drops/recreates only the allowed QA database,
applies Alembic migrations, seeds local tenants, starts API and worker
processes, and captures Playwright screenshots.

6. If validation fails, diagnose the failure, fix the active spec only, and
   rerun the failed command before proceeding. Continue the repair loop until
   validation passes or a stop condition is reached.
7. Do not start the next spec until QA docs, API/database/quality validation,
   and Playwright validation all pass for the active spec.
8. Update the generated `status.json` with completed phases, validation
   commands, evidence paths, and any blocker.

## Stop Conditions

Stop the overnight run and report clearly when any of these happen:

- Security, tenant isolation, audit, redaction, credential, secret, production
  resource, or external side-effect behavior is ambiguous.
- A command would reset or mutate a database other than the active QA database.
- A spec requires real Auth0, Telegram, provider, credential, or connector calls
  that are not explicitly mocked or approved in its artifacts.
- A template, route, helper, static asset, or dependency would be deleted
  without deletion-grade parity evidence.
- A legacy direct link cannot safely redirect or retire.
- Analysis still has CRITICAL findings after two remediation loops.
- QA docs, backend quality gates, frontend quality gates, route/import
  scanners, or Playwright fail after a focused repair attempt.
- Existing unrelated user changes block implementation.

## Progress Reporting

Keep a concise status trail:

- Current spec number/title and active phase.
- Auto-clarifications selected.
- Analysis findings remediated or left outstanding.
- Completed task count.
- Deleted or retained Jinja surfaces and evidence paths.
- Validation commands and Playwright screenshots.
- Next spec to run or exact blocker.

When resuming, read `queue.json`, `status.json`, `.specify/feature.json`, git
status, the active feature's `tasks.md`, and the current inventory/deletion
evidence before doing more work.
