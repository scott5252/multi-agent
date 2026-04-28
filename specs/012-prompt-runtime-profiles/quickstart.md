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

## Version 2 Reviewer Flow: Gateway-Governed Runtime Execution

1. Apply migrations and seed one healthy provider connection, model definition,
   active prompt version, active runtime profile version, and valid
   model_skill_config route.
2. Start the API and worker with container-built dependencies:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   uv run python -m multi_agent_platform.workers.main
   ```

3. Start a workflow run that uses a declared agent key.
4. Confirm run acceptance already pinned prompt/profile versions before the
   worker performs model-backed work.
5. Confirm the worker invokes `ModelGateway` and records tenant id, workflow
   run id, step id when available, trace id, idempotency identity, selected
   profile version id, prompt version ids, model routing provenance, provider
   connection id, model id, latency, usage availability, retry/breaker
   summaries, normalized outcome, and safe summary.
6. Confirm no tool, memory, handoff, artifact, approval, or other
   side-effectful runtime action occurs before the gateway operation identity
   and prompt/profile provenance are persisted.

## Version 2 Reviewer Flow: Test Bench And Validation Parity

1. Run a profile test bench execution that intentionally calls a model
   provider.
2. Run a workflow validation path that performs model-backed validation.
3. Confirm both paths use `ModelGateway` and produce comparable safe attempt
   metadata.
4. Confirm non-model-backed validation does not create gateway operation rows.
5. Confirm runtime profile model routing hints are present as context but do
   not bypass model_skill_config authorization or tenant-over-platform profile
   precedence.

## Version 2 Reviewer Flow: Idempotency And Recovery

1. Trigger a gateway invocation with a stable logical operation identity.
2. Retry or restart the worker with the same identity.
3. Confirm the platform reuses or recovers the prior authoritative result and
   records each physical attempt under the same logical operation.
4. Repeat the pattern for an admin provider test probe and a provider catalog
   sync action.
5. Confirm duplicate completed operations return the previous safe result
   without launching unnecessary provider work.
6. Confirm ambiguous outcomes either recover from persisted safe state or fail
   closed according to retry/breaker policy.

## Version 2 Reviewer Flow: Admin Probe Controls

1. Launch a provider test probe as an authorized admin.
2. Exceed the actor/provider-connection rate limit or bounded-operation limit.
3. Confirm the denied or throttled attempt persists safe audit evidence with
   actor, scope, provider identity, recovery identity, decision category, and
   safe summary.
4. Confirm denied and throttled attempts do not call the provider.
5. Confirm tenant-level and global backstop limits apply for shared provider
   capacity.

## Version 2 Reviewer Flow: Reliability And Observability

1. Simulate timeout, rate limit, provider unavailable, malformed response,
   authorization failure, invalid model, inactive catalog, and unknown provider
   failure outcomes.
2. Confirm normalized provider categories map into existing retry categories,
   retry budgets, breaker scopes, breaker decisions, and persisted gateway
   attempt summaries.
3. Confirm breaker scope is provider connection plus model/catalog identity,
   with tenant/run/step context recorded as evidence.
4. Confirm successful attempts record latency and usage availability even when
   usage token counts are unavailable.
5. Confirm run provenance shows prompt/profile pins and gateway metadata
   together for newly accepted runs and dynamic first-use selections.

## Version 2 Guardrail Checks

Run the full static, contract, integration, docs, and coverage suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/model_providers tests/unit/bootstrap tests/unit/runtime tests/unit/reliability
uv run pytest tests/contract
uv run pytest tests/integration/workers tests/integration/runtime tests/integration/api
uv run pytest tests/docs
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Additional V2 guardrails:

- Static tests must fail if runtime, worker, test bench, workflow validation,
  prompt/profile, or agent code imports provider SDKs or performs direct
  provider HTTP calls outside allowed `ModelGateway` adapter modules.
- Behavioral tests must fail if representative model-backed runtime, test
  bench, or workflow validation paths do not create gateway operation metadata.
- Regression tests must prove completed Spec 012 prompt authoring, safe
  preview, publication, retirement, tenant grants, runtime profile activation,
  browser UI, workflow validation, model-skill prompt reference integration,
  docs, migrations, and coverage still pass.

## Version 2 Safety Checks

- Search gateway attempts, probe results, catalog sync records, audit rows,
  logs, traces, browser pages, and run provenance for raw prompts,
  completions, credentials, provider tokens, API keys, local endpoint secrets,
  unsafe preview content, and unauthorized run content; none should be present.
- Break provider catalog visibility, connection health, credential references,
  retry/breaker state, tenant authorization, and prompt/profile pins
  independently; each failure must fail closed with safe audit evidence.
- Review historical runs and pre-V2 gateway rows; they must remain unchanged
  and display missing V2 metadata as unavailable rather than being rewritten.
