# PR Notes: Spec 070

## Reviewer Focus

- Verify roles, contracts, topology, joins, approvals, and subworkflow controls
  persist through the Spec 069 full-document save contract.
- Confirm graph canvas state matches the keyboard-readable node, edge, and join
  lists.
- Confirm the browser never treats dependency warnings as publish readiness or
  authorization decisions.
- Review mobile layout for single-column controls, stable graph framing, and no
  text overlap.
- Review validation findings for safe section anchors and no raw payload leaks.

## Redaction And Security

- No raw prompts, completions, secrets, credentials, provider payloads, raw tool
  payloads, raw test transcripts, stack traces, local filesystem paths, or
  unauthorized tenant labels are intentionally rendered.
- Prompt/profile creation remains deferred to Spec 071; Spec 070 only preserves
  safe reference placeholders.
- Publish readiness remains backend-owned.

## Curl Coverage Decision

Spec 070 does not add a new route family and does not change the public React
workflow save route shape. The existing `curl_testing.md` coverage in section
`18.4a React workflow full document save scenarios` remains the authoritative
curl regression for create, save, replay, stale, invalid, and reload behavior.

## README And Quickstart Impact

No shared onboarding command changed. `README.md` and `docs/quickstart.md` do
not require additional command updates for Spec 070. The feature-specific
manual workflow is documented in `qa070.md`, `qa070_ui.md`, and
`qa070_user_guide.md`.

## Validation Evidence To Record

- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py -q --no-cov`
- `cd frontend/admin && npm test -- Workflow`
- `cd frontend/admin && npm run typecheck`
- `cd frontend/admin && npm run build`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/070-react-workflow-graph-and-agent-role-builder`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml --start-processes`
- `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa070-after-spec`
