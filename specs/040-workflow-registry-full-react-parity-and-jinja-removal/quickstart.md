# Quickstart: Workflow Registry React Parity And Jinja Removal

## Prerequisites

- `uv sync`
- PostgreSQL/Docker available for QA validation
- Node.js version compatible with `frontend/admin`
- Local QA uses `AUTH_MODE=local_principal`

## Focused Local Checks

```bash
uv run pytest --no-cov tests/integration/api/test_admin_workflow_react_parity_routes.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py -q
cd frontend/admin && npm test -- --run src/components/workflows
cd frontend/admin && npm run build
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Spec QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/040-workflow-registry-full-react-parity-and-jinja-removal
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/040-workflow-registry-full-react-parity-and-jinja-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/040-workflow-registry-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

## Manual Smoke

1. Start the app in local-principal mode.
2. Log in as the platform-admin principal.
3. Open `/admin/app/workflows`.
4. Confirm the workflow registry, create action, draft editor, graph preview/list alternative, validation panel, publish gate, revision history, and published version detail are reachable without Jinja.
5. Open old URLs such as `/admin/workflows/ui`, `/admin/workflows/new`, `/admin/workflows/drafts/{id}/editor`, `/admin/workflows/drafts/{id}/publish-gate/ui`, `/admin/workflows/drafts/{id}/revisions/ui`, and `/admin/workflows/versions/{id}/detail`.
6. Confirm each old URL redirects to the React workflow route or returns a non-Jinja safe problem response.
7. Confirm QA screenshots, route responses, and reviewer notes do not expose raw secrets, raw prompts, raw completions, raw tool payloads, local filesystem paths, stack traces, or unauthorized tenant labels.

## Rollback Notes

If workflow React parity fails after workflow templates are deleted, restore only the workflow templates/static assets and corresponding browser routes from git, keep the React JSON APIs intact, and mark the workflow inventory items retained with blockers in reviewer notes. Do not restore shared shell or global Jinja behavior beyond the workflow-owned rollback.
