# Quickstart: React Workflow Graph And Agent Role Builder

## Preconditions

- PostgreSQL is running through Docker Compose.
- The React Admin frontend has generated API contracts.
- Local QA uses `AUTH_MODE=local_principal`.
- Spec 069 full-document save behavior is present.

## Local Validation Setup

```bash
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/frontend/generate_admin_react_types.py
```

## Manual Browser Journey

1. Start the FastAPI app and React Admin assets using the validation runner or
   local dev commands.
2. Sign in as the local principal.
3. Open Admin, then Workflow Registry.
4. Create a workflow draft.
5. Add three roles:
   - Coordinator
   - Research Agent
   - Review Agent
6. Add input and output contracts.
7. Add role nodes for the three roles.
8. Add a join node and terminal node.
9. Add edges from the entry role to the agent roles, from agent roles to the
   join node, and from the join node to the terminal node.
10. Add a join policy with inbound edges and quorum behavior.
11. Add an approval gate or subworkflow reference if the route supports it in
   the current draft.
12. Save the draft.
13. Reload the page and confirm roles, contracts, nodes, edges, join settings,
   approval/subworkflow summaries, canvas preview, and keyboard-readable lists
   match the saved state.
14. Trigger validation and confirm backend-owned findings point to the edited
   sections.

## Focused Commands

```bash
uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py -q --no-cov
cd frontend/admin && npm test -- Workflow
cd frontend/admin && npm run typecheck
cd frontend/admin && npm run build
```

## Spec Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/070-react-workflow-graph-and-agent-role-builder
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa070-after-spec
```

## Expected Evidence

- Frontend tests prove role, contract, node, edge, join, and dirty-save controls.
- Backend smoke tests prove full graph document changes persist and reload.
- Playwright desktop and mobile screenshots prove nonblank graph rendering,
  stable framing, keyboard-readable lists, and no obvious text overlap.
- Curl regression either remains unchanged because no route family changed, or
  includes updated workflow save coverage if the public contract changes.
