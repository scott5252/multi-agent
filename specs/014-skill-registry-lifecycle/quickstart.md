# Quickstart: Skill Registry And Installation Lifecycle

## Prerequisites

```bash
uv sync
uv run alembic upgrade head
```

Use local-principal admin test mode for reviewer flows unless Auth0 test
credentials are available.

## Start The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

When smoke-test workers are implemented, run the worker process in a second
terminal:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Platform Admin Flow

1. Open `/admin/skill-registry/ui/packages`.
2. Create a package with a stable slug, description, owner, and safe docs
   summary.
3. Open the candidate form and submit a declarative manifest that references
   only existing approved tool/MCP integrations.
4. Run validation and confirm findings cover manifest fields, documentation,
   fixtures, tool declarations, network requirements, credential requirements,
   runtime permissions, compatibility metadata, and artifact digests.
5. Publish semantic version `X.Y.Z`.
6. Grant availability to one selected tenant.
7. Confirm another tenant cannot discover or install the version.

## Tenant Admin Flow

1. Open `/admin/skill-registry/ui/installations?tenant_id=<tenant>`.
2. Install the authorized package version.
3. Configure each required credential using an existing secret reference or
   delegated credential link. Do not enter raw credential values.
4. Run declared smoke tests.
5. Confirm readiness remains blocked until required credentials,
   compatibility, permissions, and smoke tests pass.
6. Promote readiness and confirm binding eligibility shows matched Spec 007
   policy versions or actionable denial reasons.

## Binding And Workflow Publish Flow

1. Open the existing model/skill configuration admin page.
2. Attempt to bind a non-ready or quarantined installation and confirm it is
   denied with a safe reason.
3. Bind a ready installation to an eligible agent profile or workflow role.
4. Publish a workflow that references the installation.
5. Confirm the published workflow pins installation id, installation version,
   package slug/version, manifest digest, artifact digest, and matched policy
   evidence.

## Upgrade And Rollback Flow

1. Publish a newer package version.
2. Install it as a new tenant installation version.
3. Confirm existing bindings still point to the old installation.
4. Explicitly create a new binding or publish a workflow referencing the new
   installation.
5. Roll back by explicitly binding or publishing to the prior installation
   version.
6. Confirm rollback is blocked if the prior installation is quarantined or no
   longer eligible.

## Quarantine Flow

1. Quarantine a package version as platform admin.
2. Confirm new installs are blocked.
3. Confirm readiness promotion, new bindings, workflow publish validation, and
   runtime eligibility are blocked for affected installations.
4. Confirm existing immutable package and installation history remains
   visible as safe summaries.
5. Resolve quarantine and rerun readiness/policy checks before allowing use.

## Optimistic Concurrency Check

1. Open the same installation configuration page in two sessions.
2. Configure credentials in the first session.
3. Submit smoke-test or readiness changes from the second stale session.
4. Confirm the request returns 409, makes no state change, and writes a safe
   stale-token audit record.

## Automated Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Targeted suites to add during implementation:

```bash
uv run pytest tests/unit/admin/test_skill_manifest.py
uv run pytest tests/integration/skill_registry/test_skill_installation_lifecycle.py
uv run pytest tests/integration/skill_registry/test_skill_policy_integration.py
uv run pytest tests/integration/skill_registry/test_skill_workflow_publish_validation.py
uv run pytest tests/contract/test_skill_registry_contract.py
```

## Required Reviewer Evidence

- Validation blocks missing manifest fields, duplicate semantic versions,
  unsafe docs, disallowed permissions, and rejected entrypoint types.
- Tenant isolation blocks unauthorized discovery, installation, smoke-test
  evidence, binding, audit, and exports.
- Raw package secrets and credential values are absent from database rows,
  audit records, logs, rendered views, and exports.
- Quarantine blocks new installs, readiness promotion, new bindings, workflow
  publish, and runtime use while preserving immutable history.
- Upgrade keeps existing bindings pinned until explicit rebinding or workflow
  publication.
- README, user-facing docs, PR notes, and testing instructions are updated.
