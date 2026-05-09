# PR Notes: Spec 071

## Reviewer Focus

- Verify the workflow builder uses safe selected-draft reference catalogs for prompt and runtime profile options.
- Verify per-agent binding rows show complete, incomplete, and blocked role states.
- Verify generated prompt/profile references persist through the existing workflow save route.
- Verify graph and role summaries show readiness metadata without raw prompt template content.
- Verify mobile layout keeps the binding matrix and controls readable without overlap.

## Redaction And Security

- No raw prompts, completions, secrets, credentials, provider payloads, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, or unauthorized tenant labels are intentionally rendered by workflow setup surfaces.
- The QA seed creates prompt/profile records for deterministic API checks, but browser screenshots stay on workflow setup surfaces and do not capture prompt template editor content.
- Profile routing and credential expectations are represented as safe summaries and static reference labels only.
- Publish readiness and validation remain backend-owned.

## Curl Coverage Decision

Spec 071 uses existing route families:

- `7.1 Prompt runtime profile API smoke`
- `18.4a React workflow full document save scenarios`
- `18.4b React workflow graph and setup routes`

No new public route family was added. `curl_testing.md` does not require new commands for this spec. The new QA071 guide documents focused prompt/profile API checks and workflow save checks for reviewer evidence.

## README And Quickstart Impact

No shared onboarding command changed. `README.md` and `docs/quickstart.md` do not require command updates for Spec 071. The feature-specific manual workflow is documented in `qa071.md`, `qa071_ui.md`, and `qa071_user_guide.md`.

## Validation Evidence To Record

- `uv run python scripts/frontend/generate_admin_react_types.py --check`
- `uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py -q --no-cov`
- `cd frontend/admin && npm test -- workflowPromptProfileBinding WorkflowBuilderPage`
- `cd frontend/admin && npm run typecheck`
- `cd frontend/admin && npm run build`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/071-prompt-profile-creation-and-per-agent-binding-ui`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml --start-processes`
- `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa071-after-spec`
