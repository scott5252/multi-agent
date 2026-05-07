# Quickstart: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## Setup

1. Install dependencies:

   ```bash
   uv sync
   cd frontend/admin && npm install
   ```

2. Apply database migrations:

   ```bash
   uv run alembic upgrade head
   ```

3. Use the generated QA environment for deterministic local-principal validation:

   ```bash
   cp specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/.env.qa042 .env
   ```

## Local Development

1. Build React assets:

   ```bash
   cd frontend/admin && npm run build
   ```

2. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

3. Sign in locally and open the skill workspace:

   ```text
   http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/skills
   ```

## Validation

Run the mandatory Spec 042 validation sequence:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml --start-processes
```

Expected Playwright evidence:

```text
output/playwright/qa042_ui/qa042-react-ui2-smoke.png
```

## Reviewer Checks

- Open `/admin/app/skills` and verify package, installation, readiness, binding, diagnostics, audit, and legacy redirect evidence are visible.
- Open old `/admin/skill-registry/ui/*` and `/admin/skill-execution/ui/diagnostics` URLs and verify they redirect to React or return a safe non-Jinja problem.
- Confirm manifest candidate output contains only summaries, findings, fingerprints, revision tokens, and audit or artifact references.
- Confirm credential and diagnostics output contains no raw secret values, resolved credentials, connector payloads, smoke-test transcripts, local paths, stack traces, or unauthorized tenant labels.
