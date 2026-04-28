# Quickstart: Prompt Library And Agent Runtime Profiles

## Prerequisites

- PostgreSQL is running and configured for the project.
- Auth0 or deterministic local-principal mode is configured for admin access.
- Existing workflow registry, model-skill config, memory policy, audit, and
  redaction migrations are applied.

## Validate The Design Locally

```bash
uv sync
uv run alembic upgrade head
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Run The API And Admin UI

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open the shared admin shell:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts
http://127.0.0.1:8000/admin/prompt-runtime/profiles
```

## Reviewer Flow: Prompt Library

1. Sign in as a platform administrator or use deterministic local-principal
   mode.
2. Create a platform-scoped prompt lineage in the browser.
3. Add prompt content with `{{variable_name}}` placeholders only.
4. Declare each variable with purpose, required flag, allowed value category,
   and sample guidance.
5. Add a sanitized fixture value set and save the draft.
6. Run validation and confirm malformed, missing, unused, or duplicate
   variables produce blocking findings.
7. Preview with fixture values and confirm no raw secret, credential value, or
   unauthorized run content is rendered or audited.
8. Publish the prompt and confirm the published version is read-only.
9. Grant the specific published prompt version to a tenant.
10. Retire the prompt version and confirm it disappears from new-use selectors
    but remains visible for authorized historical review.

## Reviewer Flow: Agent Runtime Profiles

1. Open **Agent Profiles** in the shared admin shell.
2. Create a profile for an agent key or sub-agent key.
3. Select authorized active prompt versions for required profile purposes.
4. Add model routing hints, memory scope policy, skill requirements, tool
   policy expectations, output contract expectations, and test-suite
   requirements.
5. Run profile validation and confirm missing or incompatible sections show
   blocking findings with clear remediation.
6. Activate the profile and confirm an immutable profile version is created.
7. Grant a platform profile version to a tenant and preview resolution for that
   tenant.
8. Create a tenant profile for the same key and confirm tenant profile
   resolution wins over the platform fallback.
9. Retire the profile version and confirm it is unavailable for new workflow
   validation but remains visible in history and run provenance.

## Reviewer Flow: Workflow And Runtime Pinning

1. Create or open a workflow draft that references the agent and sub-agent keys.
2. Run workflow registry validation.
3. Confirm validation reports resolved profile version ids and Spec 007 prompt
   reference ids, plus underlying prompt library version ids when authorized.
4. Publish the workflow and inspect the immutable bundle summary for
   prompt/profile pins.
5. Start a run and confirm run acceptance stores the same prompt/profile
   versions in the pinned execution bundle.
6. Exercise a dynamically selected agent not declared in the workflow and
   confirm first-use pinning persists before any model, tool, or memory side
   effect.

## Safety Checks

- Search prompt/profile records, audit rows, logs, and rendered pages for raw
  API keys, credential values, provider tokens, unauthorized run content, and
  unsafe fixture values; none should be present.
- Attempt cross-tenant prompt/profile access and confirm safe not-found or
  safe forbidden behavior.
- Attempt to create a Spec 007 prompt reference to a retired or unauthorized
  prompt version and confirm validation blocks it.
- Attempt to activate a profile with a retired prompt version and confirm
  validation blocks it.
- Attempt concurrent draft saves with stale revision numbers and confirm the
  second save receives a conflict without overwriting the newer revision.

## Expected Evidence

- `docs/prompt-runtime-profiles.md` documents prompt lifecycle, variable
  validation, safe fixture previews, immutable versions, retirement semantics,
  runtime profile contracts, scope rules, workflow validation, Spec 007 prompt
  references, run pinning, audit behavior, and browser usage.
- `README.md` and `docs/quickstart.md` link to prompt library and runtime
  profile setup and reviewer flows.
- Feature PR notes describe immutable prompt/profile versions, tenant grants,
  preview safety, workflow validation, model-skill prompt references, run
  pinning, UI coverage, known risks, and rollback/retirement behavior.
- Testing instructions cover unit, integration, contract, migration, browser,
  authorization, audit/redaction, workflow validation, Spec 007 integration,
  runtime pinning, docs, and coverage evidence.
