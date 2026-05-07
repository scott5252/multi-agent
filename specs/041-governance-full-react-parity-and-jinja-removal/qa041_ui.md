# QA041 UI: Spec 041 - Governance Full React Parity And Jinja Removal

## Goal

This UI walkthrough verifies the browser experience for Spec 041.

The reviewer should confirm that governance work happens in the React admin workspace, that old governance links redirect there, and that deleted Jinja templates are not needed for daily provider, prompt, profile, routing, history, or provenance review.

Use this document even if you are not a developer.

Expected: by the end of the walkthrough, the reviewer has screenshots and notes proving React parity, redirect compatibility, role behavior, tenant isolation, and redaction.

## How To Use This Guide

Follow the sections in order.

Keep browser screenshots under `output/playwright/qa041_ui`.

Keep manual reviewer notes under `/tmp/qa041-ui-notes.md`.

Use local-principal login only.

Do not enter real provider credentials, real Telegram tokens, real Auth0 values, real connector credentials, or private prompt content.

Expected: all UI checks are deterministic and safe to share.

What is happening: the React UI reads backend-owned governance contracts and displays safe summaries.

Why this matters: the UI must prove parity without recreating sensitive logic in the browser.

## Environment Setup

Copy the QA environment.

```bash
cp specs/041-governance-full-react-parity-and-jinja-removal/.env.qa041 .env
```

Expected: `.env` points at `multi_agent_platform_qa041` and `.data/qa041-artifacts`.

Install dependencies and build React assets.

```bash
uv sync
cd frontend/admin && npm run build
cd ../..
```

Expected: dependencies are ready and the React manifest references the latest admin bundle.

Start PostgreSQL and reset the QA database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa041 && createdb -U postgres multi_agent_platform_qa041'
uv run alembic upgrade head
```

Expected: the database is reset and migrations complete.

Seed local tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa041 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex exist for role checks.

Start the API and worker.

```bash
mkdir -p output/playwright/qa041_ui /tmp/qa041-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa041-ui/api.log 2>&1
```

Expected: the API serves `http://127.0.0.1:8000/health/live`.

In another terminal, start the worker.

```bash
uv run python -m multi_agent_platform.workers.main > /tmp/qa041-ui/worker.log 2>&1
```

Expected: the worker runs without live provider, Telegram, credential, or connector calls.

Open the browser login page.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Expected: the local login page lists `platform-admin`, `tenant-admin-acme`, and other QA principals.

## Browser Walkthrough

1. Sign in as `platform-admin`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance`

Action: choose `platform-admin`.

Expected: the browser lands on `/admin/app/governance`.

What is happening: the local-principal login writes a safe local auth cookie for the platform admin.

Why this matters: provider mutation controls and platform-wide governance views require platform admin authority.

2. Review the governance landing page.

Page URL: `http://127.0.0.1:8000/admin/app/governance`

Action: capture `output/playwright/qa041_ui/manual-governance-home.png`.

Expected: the page heading is `Governance`, and setup, provider, prompt, profile, routing, history, provenance, and legacy redirect content are visible.

What is happening: the React page loads `bootstrap.json` and renders backend-owned summaries.

Why this matters: the first screen replaces multiple old Jinja governance pages.

3. Use the section navigation.

Page URL: `/admin/app/governance`

Action: click each governance section card or nav control.

Expected: active section styling changes without leaving the React workspace.

What is happening: React controls local navigation while backend data remains authoritative.

Why this matters: the browser experience must remain usable after template deletion.

4. Review provider governance.

Page URL: `/admin/app/governance/providers`

Action: inspect provider cards, credential reference text, health summary, local no-auth status, and direct-call guardrail.

Expected: provider details are summarized safely; no secret value, raw authorization header, or resolved credential appears.

What is happening: the UI renders `ProviderGovernanceSummary` records.

Why this matters: provider operators need readiness diagnostics without exposing credentials.

5. Run the deterministic provider probe action if the button is enabled.

Page URL: `/admin/app/governance/providers`

Action: click the probe action and capture the result panel.

Expected: the result shows an accepted or summarized mocked-safe diagnostic, not a live provider response.

What is happening: the action posts to a backend governance endpoint with provider policy checks.

Why this matters: React must not bypass the ModelGateway or direct-call guardrails.

6. Review prompt governance.

Page URL: `/admin/app/governance/prompts`

Action: inspect prompt status, safe change summary, render test status, and history labels.

Expected: prompt cards show summarized content only and never display raw prompt bodies.

What is happening: the UI renders `PromptLibrarySummary` and safe preview contracts.

Why this matters: prompt governance is sensitive because raw prompt text can contain protected business context.

7. Run safe prompt preview.

Page URL: `/admin/app/governance/prompts`

Action: click the preview action.

Expected: the preview panel shows safe fixture output, redaction findings, variable summary, and audit reference.

What is happening: the backend returns a summarized preview for deterministic fixture data.

Why this matters: reviewers can verify preview behavior without exposing private prompts or completions.

8. Review runtime profile governance.

Page URL: `/admin/app/governance/profiles`

Action: inspect model binding, provider binding, prompt binding, skill requirements, resolver status, and tenant grants.

Expected: profile summaries are readable and safe; no raw runtime payload or memory content appears.

What is happening: the UI renders runtime profile governance contracts.

Why this matters: profile choices affect runtime model, prompt, and tool behavior.

9. Resolve the runtime profile.

Page URL: `/admin/app/governance/profiles/resolve`

Action: click the resolve action.

Expected: the resolution panel shows selected profile version, model route, provider route, prompt route, skill route, policy reasons, and audit reference.

What is happening: backend profile resolution evidence is displayed in React.

Why this matters: profile resolution must remain deterministic and tenant-aware.

10. Review routing preview.

Page URL: `/admin/app/governance/routing`

Action: click the routing preview action.

Expected: the routing panel displays model, provider, skill, credential reference, direct-call guardrail, remediation, and policy reasons.

What is happening: the backend computes a read-only policy preview.

Why this matters: route previews must not trigger side effects or live external calls.

11. Review policy history.

Page URL: `/admin/app/governance/history`

Action: inspect history rows and links.

Expected: rows show actor label, tenant scope label, timestamp, outcome, safe diff summary, and audit reference.

What is happening: the UI renders redacted history records.

Why this matters: policy changes need review evidence without raw payloads.

12. Review run provenance.

Page URL: `/admin/app/governance/provenance/run-qa031-briefing`

Action: inspect provider, model, prompt, profile, routing, credential reference, usage, and audit evidence.

Expected: all provenance fields are summaries and no unauthorized run payload is visible.

What is happening: the UI displays run provenance from backend-owned evidence.

Why this matters: run debugging must remain safe after the Jinja pages are removed.

13. Review legacy route redirects.

Page URL: `/admin/app/governance`

Action: find the Legacy route redirects section and capture `output/playwright/qa041_ui/manual-legacy-routes.png`.

Expected: route cards list old path, React path, compatibility status, authorization behavior, and evidence summary.

What is happening: React displays the backend-owned migration ledger.

Why this matters: reviewers can verify route retirement without reading source code.

14. Test old provider URL.

Page URL: `http://127.0.0.1:8000/admin/model-providers`

Action: open the URL directly.

Expected: the browser redirects to `/admin/app/governance/providers`.

What is happening: the old route returns a redirect instead of rendering `model_providers/index.html`.

Why this matters: bookmarks remain useful after template deletion.

15. Test old prompt preview URL.

Page URL: `http://127.0.0.1:8000/admin/prompt-runtime/prompts/11111111-1111-1111-1111-111111111041/preview?fixture_set_id=default`

Action: open the URL directly.

Expected: the browser redirects to a React prompt preview path and preserves safe fixture intent.

What is happening: the old route maps the prompt id into a React destination.

Why this matters: direct links should not leak whether unauthorized prompt data exists.

16. Test old profile resolution URL.

Page URL: `http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve?tenant_id=11111111-1111-1111-1111-111111111111&agent_key=planner&agent_kind=agent`

Action: open the URL directly.

Expected: the browser redirects to `/admin/app/governance/profiles/resolve` and keeps `agent_key=planner`.

What is happening: safe query values are preserved.

Why this matters: reviewers can follow old profile resolution links without retyping context.

17. Test old model-skill history URL.

Page URL: `http://127.0.0.1:8000/admin/config/ui/history?tenant_id=11111111-1111-1111-1111-111111111111`

Action: open the URL directly.

Expected: the browser redirects to `/admin/app/governance/history`.

What is happening: the old model-skill history page is retired.

Why this matters: model-skill governance moved into the shared React workspace.

18. Switch to `tenant-admin-acme`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance`

Action: select `tenant-admin-acme`.

Expected: the governance page loads for Acme tenant context.

What is happening: local login swaps the principal and tenant scope.

Why this matters: tenant reviewers must still see authorized governance data.

19. Review tenant-admin provider controls.

Page URL: `/admin/app/governance/providers`

Action: inspect provider actions.

Expected: platform-only mutation controls are absent or disabled for tenant admin.

What is happening: backend authorization shapes the action list.

Why this matters: React cannot expose platform-only provider mutation to tenant users.

20. Switch to `tenant-admin-globex`.

Page URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance?tenant_id=11111111-1111-1111-1111-111111111111`

Action: select `tenant-admin-globex`.

Expected: Acme-specific views are denied or scoped safely.

What is happening: the backend rejects forged tenant scope.

Why this matters: cross-tenant isolation is a release blocker.

21. Capture final evidence.

Page URL: `/admin/app/governance`

Action: write final reviewer notes in `/tmp/qa041-ui-notes.md`.

Expected: notes include screenshots, principals tested, old URLs tested, and any unexpected behavior.

What is happening: manual evidence is gathered for review.

Why this matters: Spec 041 cannot advance without auditable QA notes.

## Required Automated Evidence

Run focused backend tests.

```bash
uv run pytest --no-cov tests/unit/api/test_admin_governance_schema.py tests/unit/admin/test_governance_jinja_retirement.py tests/integration/api/test_admin_governance_legacy_redirects.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py -q
```

Expected: backend governance, redirect, scanner, and contract tests pass.

Run focused frontend tests.

```bash
cd frontend/admin && npm test -- --run src/App.test.tsx src/components/governance
```

Expected: all governance UI tests pass.

Run React build.

```bash
cd frontend/admin && npm run build
```

Expected: TypeScript and Vite build complete.

Run full quality gates.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: every command exits successfully.

Run Spec 041 browser validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/041-governance-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected: Playwright writes `output/playwright/qa041_ui/qa041-react-ui2-smoke.png`.

## UI Evidence Checklist

- `manual-governance-home.png` captures the React governance landing page.
- `manual-legacy-routes.png` captures the redirect ledger.
- Provider screenshot shows credential reference summaries without secret values.
- Prompt screenshot shows safe preview without raw prompt text.
- Profile screenshot shows resolution evidence without raw runtime payloads.
- Routing screenshot shows read-only model, provider, skill, policy, and credential summaries.
- History screenshot shows redacted audit-safe summaries.
- Provenance screenshot shows evidence summaries only.
- Old provider URL redirect is recorded.
- Old prompt preview URL redirect is recorded.
- Old profile resolve URL redirect is recorded.
- Old model-skill history URL redirect is recorded.
- Tenant-admin controls are captured.
- Cross-tenant denial is captured or noted.

## Acceptance Notes Template

- Reviewer:
- Date:
- Principal checks completed:
- Screenshots captured:
- Old URLs tested:
- Tenant isolation result:
- Redaction result:
- Backend tests:
- Frontend tests:
- React build:
- Playwright:
- Release concerns:

## Troubleshooting

If local login does not show expected principals, confirm `.env.qa041` is copied to `.env`.

If `/admin/app/governance` shows a loading state forever, check `/tmp/qa041-ui/api.log`.

If old URLs do not redirect, confirm the app was restarted after the route changes.

If screenshots show a missing bundle, rerun the React build.

If tenant switching appears stale, clear the `map_local_principal` cookie and sign in again.

If a response shows a stack trace, stop QA and file it as a blocker.

If evidence contains raw secrets, prompt bodies, completions, memory content, provider payloads, or local filesystem paths, stop QA and treat it as a redaction blocker.

## Related Files

- `specs/041-governance-full-react-parity-and-jinja-removal/qa041.md`
- `specs/041-governance-full-react-parity-and-jinja-removal/.env.qa041`
- `specs/041-governance-full-react-parity-and-jinja-removal/qa041_user_guide.md`
- `specs/041-governance-full-react-parity-and-jinja-removal/pr_notes.md`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/admin/governance.py`
- `frontend/admin/src/components/governance/GovernancePage.tsx`
- `tests/integration/api/test_admin_governance_legacy_redirects.py`
- `tests/unit/admin/test_governance_jinja_retirement.py`
