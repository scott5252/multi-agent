# Quickstart: Prompt Profile Creation And Per-Agent Binding UI

## Prerequisites

1. Docker is running.
2. PostgreSQL is available through `docker compose up -d postgres`.
3. The Spec 071 QA environment file has been copied to `.env`.
4. Migrations are at head.
5. The QA seed script has created a workflow draft with at least three roles and deterministic prompt/profile seed records.

## Setup

```bash
cp specs/071-prompt-profile-creation-and-per-agent-binding-ui/.env.qa071 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa071 && createdb -U postgres multi_agent_platform_qa071'
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_prompt_profile_qa071.py
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Open `/auth/local-login?redirect_to=/admin/app/workflows`, choose the Acme tenant admin, and use visible navigation to open Workflow Registry.

## Browser Verification

1. Open the QA071 workflow draft.
2. Find the prompt/profile binding section.
3. For the first role, create or select a prompt.
4. Edit raw prompt content only in the prompt editor form.
5. Add variables and a deterministic fixture set.
6. Validate and publish the prompt.
7. Create or select a runtime profile for the same role.
8. Bind the published prompt version to the profile.
9. Validate and activate the profile.
10. Bind the profile reference to the workflow role.
11. Repeat or reuse safe catalog records for two more roles.
12. Save the workflow draft.
13. Reload the page and confirm all three role bindings return from durable state.
14. Confirm raw prompt content is absent from binding summaries, graph panels, JSON inspectors, screenshots, audit summaries, and docs.

## Automated Verification

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/071-prompt-profile-creation-and-per-agent-binding-ui
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa071-after-spec
```

## Expected Results

- Prompt and profile catalogs show only authorized live records.
- Clean tenant empty states are truthful and include creation actions.
- Prompt publish and profile activation produce immutable version references.
- Workflow role binding save persists only prompt/profile references and safe metadata.
- Validation findings map missing, stale, inactive, retired, unauthorized, and cross-tenant references back to role binding controls.
- No raw prompt, provider payload, credential value, raw completion, private tool payload, raw transcript, stack trace, local path, or unauthorized tenant label appears in safe UI or QA artifacts.
