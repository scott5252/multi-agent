# Testing Instructions: User And Tenant Membership Administration

## Focused Tests

Run the focused suite without coverage when iterating:

```bash
uv run pytest --no-cov \
  tests/unit/admin/memberships \
  tests/unit/api/test_membership_schemas.py \
  tests/unit/api/test_membership_ui_models.py \
  tests/unit/auth/test_membership_policy.py \
  tests/unit/db/test_membership_repository.py \
  tests/integration/api/test_admin_memberships_api.py \
  tests/integration/api/test_admin_memberships_ui.py \
  tests/contract/test_membership_administration_contract.py \
  tests/docs/test_membership_administration_docs.py \
  tests/integration/db/test_membership_administration_migration.py \
  tests/unit/auth/test_service.py
```

Expected: all focused membership, API, UI, auth, contract, docs, and migration
tests pass.

## Required Quality Gates

Run the repository gates before review:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: lint, formatting, static typing, and coverage pass at or above the
repository threshold.

## QA Document Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/018-user-tenant-membership-administration
```

Expected: the validator reports the QA guide, UI walkthrough, and environment
file paths.

## Spec Kit Validation

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml
```

Expected: setup, health checks, manual QA user guide validation, quality
commands, and coverage pass.

## Browser Validation

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml --start-processes
```

Expected: the flow signs in as `platform-admin`, reaches
`/admin/memberships`, and captures screenshots under
`output/playwright/qa018_ui`.

## Manual QA

Use:

- `specs/018-user-tenant-membership-administration/qa018.md`
- `specs/018-user-tenant-membership-administration/qa018_ui.md`
- `specs/018-user-tenant-membership-administration/qa018_user_guide.md`

Expected: reviewer evidence shows platform administration, tenant
self-service, tenant isolation, idempotent invitations, next-request role and
status behavior, and safe redaction.
