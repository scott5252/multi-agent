---
description: "Generate required post-implementation QA guide, UI walkthrough, and QA environment documents"
---

# Generate Post-Implementation QA Documents

Create the mandatory manual QA guide, browser-first UI walkthrough, and
self-contained QA environment file for the active implemented spec.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding, but this command is
normally invoked as an `after_implement` hook and should use the active Spec Kit
feature directory.

## Required Outputs

Create all three files in the active spec directory:

- `qaNNN.md`
- `qaNNN_ui.md`
- `.env.qaNNN`

`NNN` is the three-digit spec number from the spec directory name. For example,
`specs/009-reliability-scale-hardening` must produce `qa009.md`,
`qa009_ui.md`, and `.env.qa009`.

## Reference Standard

Before writing any file, read these reference files and match their level of
specificity, reviewer tone, and copy/paste usability:

- `specs/008-production-audit-debugging/qa008.md`
- `specs/008-production-audit-debugging/.env.qa008`
- `specs/013-admin-workflow-builder/qa013_ui.md`

Do not copy QA008 or QA013 UI blindly. Use them as the detail bar, then tailor
every command, endpoint, browser URL, seed record, principal, expected response,
screen description, and known gap to the active spec. The UI document must be
accurate enough for a non-developer reviewer to understand what each screen is
for, what fields mean, what action to take, what should happen, and why the
check matters.

## Extension Configuration

Load configuration from `.specify/extensions/qa-docs/qa-docs-config.yml`.
Allow local machine overrides from
`.specify/extensions/qa-docs/qa-docs-config.local.yml` and environment
overrides named `SPECKIT_QA_DOCS_*`. If configuration is missing, use the
defaults in `.specify/extensions/qa-docs/extension.yml`.

Default values:

- `guide_prefix`: `qa`
- `reference_spec_dir`: `specs/008-production-audit-debugging`
- `ui_reference_file`: `specs/013-admin-workflow-builder/qa013_ui.md`
- `validation.min_guide_lines`: `180`
- `validation.min_env_lines`: `35`
- `validation.min_ui_lines`: `160`
- `validation.min_code_fences`: `10`
- `validation.min_expected_markers`: `12`
- `validation.min_ui_code_fences`: `6`
- `validation.min_ui_expected_markers`: `8`

## Execution

1. Resolve the active feature directory.

   From the repository root, run:

   ```bash
   .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
   ```

   Parse `FEATURE_DIR`. If that command cannot run, read
   `.specify/feature.json` and use its `feature_directory` value. Stop if the
   feature directory cannot be resolved or if `spec.md`, `plan.md`, or
   `tasks.md` are missing.

2. Derive the QA file names.

   Use the basename of `FEATURE_DIR`. It must start with a three-digit spec
   number:

   ```text
   specs/009-reliability-scale-hardening -> qa009.md and .env.qa009
   specs/009-reliability-scale-hardening -> qa009_ui.md
   ```

3. Load implementation context.

   Read these files when present:

   - `spec.md`
   - `plan.md`
   - `tasks.md`
   - `quickstart.md`
   - `research.md`
   - `data-model.md`
   - `contracts/`
   - relevant migrations, routers, services, workers, templates, static assets,
     tests, and docs touched by the implementation

   Extract the implemented user stories, API routes, web views, workers,
   database tables, environment variables, tenants, principals, seed data,
   object-storage paths, quality commands, and known implementation limits.

4. Generate `.env.qaNNN`.

   The environment file must be self-contained for a local manual QA pass. It
   must include, when applicable:

   - Application metadata, host, port, logging, build, metrics, and tracing.
   - `AUTH_MODE=local_principal` plus safe placeholder Auth0 values.
   - `LOCAL_PRINCIPAL_HEADER`, cookie name, and a
     `LOCAL_PRINCIPAL_CATALOG_JSON` with at least same-tenant admin, same-tenant
     non-admin or operator, same-tenant auditor when audit review matters, and
     cross-tenant admin principals.
   - A dedicated PostgreSQL database:
     `multi_agent_platform_qaNNN`.
   - SQLAlchemy and runtime checkpointer URLs pointing at that database.
   - Static secret provider values that are clearly fake placeholders and use
     `qaNNN` names.
   - Filesystem storage rooted at `.data/qaNNN-artifacts`.
   - Worker, channel, callback, SSE, rate-limit, and feature-specific settings
     needed to boot the app and exercise the implemented spec.

   Never include real API keys, real tokens, personal credentials, production
   hostnames, or raw secret values that look usable.

5. Generate `qaNNN.md`.

   Write the guide for a non-developer reviewer. It must be executable from a
   fresh checkout and include copy/paste commands with expected results. Use the
   QA008 guide as the detail model.

   Required sections:

   - `# QANNN: <Feature Name>`
   - `## Goal`
   - `## What This Guide Covers`
   - `## How To Use This Guide`
   - `## Environment`
   - `## Environment File Checklist`
   - `## Shared QA Variables`
   - One or more feature-specific manual verification sections
   - Authorization, tenant isolation, failure, or negative-path checks whenever
     the implementation has protected behavior
   - Security/redaction or data-safety checks whenever secrets, prompts,
     memory, artifacts, callbacks, audits, or model/tool routing are involved
   - `## Required Automated Evidence`
   - `## Acceptance Evidence Template`
   - `## Troubleshooting`
   - `## Related Files`

   The guide must include:

   - Exact setup commands: copy `.env.qaNNN` to `.env`, run `uv sync`, start
     PostgreSQL when needed, create the QA database, run migrations, and seed
     deterministic data.
   - Exact commands for starting the API and any worker processes needed by the
     spec.
   - Deterministic seed data or data-creation steps. Prefer SQL seed blocks for
     database-backed behavior when no public endpoint creates all evidence.
   - `curl`, `jq`, browser, worker, SQL, or CLI checks that map to each
     implemented user story.
   - Saved output files under `/tmp/qaNNN-*` so reviewers can preserve evidence.
   - Explicit `HTTP_STATUS` checks for API calls.
   - "Expected:" callouts after each command or command group.
   - "What this proves:" notes for important manual checks.
   - Current implementation notes and gaps, so reviewers can tell an expected
     limitation from a regression.
   - Redaction scans that fail if raw secrets, credential values, prompt bodies,
     memory payloads, or large external payloads leak.
   - The exact automated quality commands required for this project:

     ```bash
     uv run ruff check .
     uv run ruff format --check .
     uv run mypy src
     uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
     ```

   Add focused test commands for the implemented spec before the full coverage
   gate.

6. Generate `qaNNN_ui.md`.

   Write a browser-first guide for a non-developer reviewer. It must be
   executable from a fresh checkout, include the setup needed to boot the app,
   and walk the reviewer through the UI without requiring them to run `qaNNN.md`
   first. Use `specs/013-admin-workflow-builder/qa013_ui.md` as the detail
   model.

   Required sections:

   - `# QANNN UI: <Feature Name>`
   - `## Goal`
   - `## How To Use This Guide`
   - `## Environment Setup`
   - `## Browser Walkthrough`
   - `## Required Automated Evidence`
   - `## UI Evidence Checklist`
   - `## Acceptance Notes Template`
   - `## Troubleshooting`
   - `## Related Files`

   The guide must include:

   - Exact setup commands to copy `.env.qaNNN` to `.env`, run `uv sync`, start
     PostgreSQL when needed, create or reset the QA database, run migrations,
     seed deterministic data, and start the API or any worker process needed by
     the spec.
   - A local browser login flow using
     `http://127.0.0.1:8000/auth/local-login`, including which principal to
     pick first and how to switch principals.
   - Reviewer note or screenshot file names under `/tmp/qaNNN-*`.
   - A `Browser Walkthrough` with numbered screen-level steps. Each important
     step must include the page URL, navigation path, actions to complete,
     `Expected:` outcome, `What is happening:` explanation, and
     `Why this matters:` explanation.
   - Field-level explanations for forms, filters, selectors, tabs, toggles,
     tables, cards, publish/approval controls, and read-only inspectors that a
     non-developer reviewer must evaluate.
   - Authorization, tenant isolation, failure, stale-state, or negative-path UI
     checks whenever the implementation has protected behavior.
   - Security/redaction or data-safety UI checks whenever secrets, prompts,
     memory, artifacts, callbacks, audits, provider payloads, model/tool
     routing, or credentials are involved.
   - If the active spec has no browser UI, still create `qaNNN_ui.md`; under
     `Browser Walkthrough`, explain that no browser-admin surface changed,
     identify any existing UI that should remain unaffected, and provide a
     minimal login/navigation smoke test plus links back to `qaNNN.md`.
   - The exact automated quality commands required for this project:

     ```bash
     uv run ruff check .
     uv run ruff format --check .
     uv run mypy src
     uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
     ```

   Add focused test commands for the implemented spec before the full coverage
   gate.

7. Validate the files.

   After writing all three files, run:

   ```bash
   bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
   ```

   If validation fails, revise the QA guide, UI walkthrough, and environment
   file until it passes. Do not report implementation completion while this
   command is failing.

## Output

Report:

- The generated guide path.
- The generated UI walkthrough path.
- The generated environment path.
- The validator result.
- Any known implementation gap documented in the guide.
