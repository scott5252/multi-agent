# Quickstart: React User And Tenant Membership Administration

## Goal

Validate the additive React membership administration workspace at
`/admin/app/memberships` while preserving the existing fallback page at
`/admin/memberships`.

## Local Setup

```bash
cp specs/034-react-user-and-tenant-membership-administration/.env.qa034 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

## Browser Flow

Open local login:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/memberships
```

Validate as `platform-admin`:

- Directory loads with platform scope.
- Invite dialog shows tenant picker and masked email result.
- Principal link/provision dialog shows safe subject suffix.
- Role grant wizard offers platform and tenant role scopes.
- Revoke, suspend, reactivate, and membership status actions require
  confirmation.
- Access history and audit timeline show safe summaries.

Validate as `tenant-admin-acme`:

- Directory is Acme-scoped.
- Invite dialog allows only permitted tenant roles.
- Platform role assignment is denied.
- Globex details and mutations fail closed.
- Screenshots show no unsafe identifiers.

## Required Checks

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run pytest --no-cov tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Full validation after implementation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/034-react-user-and-tenant-membership-administration
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml --start-processes
```

## Redaction Scan

```bash
rg -n "qa034-secret-value|raw email|full subject|authorization header|provider token|credential value|private message|/Users/|unauthorized tenant label|full external subject" /tmp/qa034-* output/playwright/qa034_ui || true
```
