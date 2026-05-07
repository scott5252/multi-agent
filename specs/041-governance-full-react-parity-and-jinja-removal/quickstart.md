# Quickstart: Governance React Parity And Jinja Removal

## Prerequisites

- `uv sync`
- PostgreSQL/Docker available for QA validation
- Node.js version compatible with `frontend/admin`
- Local QA uses `AUTH_MODE=local_principal`

## Focused Local Checks

```bash
uv run pytest --no-cov tests/integration/api/test_admin_governance_legacy_redirects.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py -q
cd frontend/admin && npm test -- --run src/components/governance
cd frontend/admin && npm run build
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python scripts/frontend/generate_admin_react_types.py --check
```

## Spec QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/041-governance-full-react-parity-and-jinja-removal
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/041-governance-full-react-parity-and-jinja-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/041-governance-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

## Manual Smoke

1. Start the app in local-principal mode.
2. Log in as the platform-admin principal.
3. Open `/admin/app/governance`.
4. Confirm provider, prompt, profile, routing, history, and provenance sections are reachable without Jinja.
5. Exercise deterministic mocked-safe provider probe, credential diagnostics, prompt preview, profile resolution, and routing preview actions.
6. Open old URLs such as `/admin/model-providers`, `/admin/model-providers/new`, `/admin/model-providers/{id}`, `/admin/prompt-runtime/prompts`, `/admin/prompt-runtime/prompts/{id}/preview`, `/admin/prompt-runtime/profiles`, `/admin/prompt-runtime/profiles/resolve`, `/admin/config/ui/history`, and `/admin/config/ui/runs/{run_id}/provenance`.
7. Confirm old URLs redirect to React or return non-Jinja safe problem responses.
8. Sign in as `tenant-admin-acme`.
9. Confirm provider mutation controls are unavailable and tenant read-only governance views remain authorized.
10. Confirm QA screenshots, route responses, and reviewer notes do not expose raw secrets, raw prompts, raw completions, raw provider payloads, raw tool payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

## Rollback Notes

If governance React parity fails after governance templates are deleted, restore only the affected governance templates/static assets and corresponding browser route handlers from git, keep React JSON APIs intact, and mark the affected governance inventory items retained with blockers in reviewer notes. Do not restore shared shell, non-governance templates, or global Jinja infrastructure as part of the Spec 041 rollback.
