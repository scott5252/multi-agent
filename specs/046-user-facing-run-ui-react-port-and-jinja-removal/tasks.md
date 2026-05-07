# Tasks: User-Facing Run UI React Port And Jinja Removal

**Input**: Design documents from `specs/046-user-facing-run-ui-react-port-and-jinja-removal/`

## Phase 1: Setup And Existing Surface Verification

- [x] T001 Confirm deleted `/runs` templates remain absent in quickstart.md
- [x] T002 [P] Confirm retained `/runs` lifecycle API coverage in tests/integration/api/test_channel_run_api.py
- [x] T003 [P] Confirm legacy browser redirect coverage in tests/integration/api/test_web_run_ui.py
- [x] T004 [P] Confirm cross-channel direct-link recovery coverage in tests/integration/channels/test_cross_channel_recovery.py
- [x] T005 [P] Confirm React channel run host coverage in tests/integration/test_admin_react_routes.py

## Phase 2: Tests First

- [x] T006 [P] Add user-facing run Jinja retirement scanner in tests/unit/admin/test_user_runs_jinja_retirement.py
- [x] T007 [P] Add generated channel run schema contract assertions in tests/contract/test_admin_react_contract.py
- [x] T008 [P] Extend legacy `/runs` browser redirect and safe query tests in tests/integration/api/test_web_run_ui.py
- [x] T009 [P] Extend retained lifecycle API tests for start/status/timeline/events/result/artifacts/approval/cancel/subscription/callback flows in tests/integration/api/test_channel_run_api.py
- [x] T010 [P] Extend cross-tenant direct-link tests in tests/integration/channels/test_cross_channel_recovery.py
- [x] T011 [P] Add React user run component tests in frontend/admin/src/components/userRuns/UserRunPage.test.tsx
- [x] T012 [P] Extend App route tests for `/admin/app/channels/runs/{run_id}` in frontend/admin/src/App.test.tsx

## Phase 3: Backend Contracts And Redirect Compatibility

- [x] T013 Import channel run Pydantic schemas in scripts/frontend/generate_admin_react_types.py
- [x] T014 Add RunInvocation, RunStatus, Timeline, Result, Artifact, Decision, Subscription, Callback, and ChannelError schemas to generated React contracts
- [x] T015 Regenerate frontend/admin/src/api/generated/reactAdminApi.ts
- [x] T016 Preserve only allowlisted query context in src/multi_agent_platform/api/routers/web_run_ui.py redirects
- [x] T017 Ensure `/runs/{run_id}` validates same-tenant access before redirect and returns safe problems on denial in src/multi_agent_platform/api/routers/web_run_ui.py
- [x] T018 Redirect `/runs` and `/runs/new` to `/admin/app/channels/runs` in src/multi_agent_platform/api/routers/web_run_ui.py
- [x] T019 Preserve retained JSON lifecycle routes in src/multi_agent_platform/api/routers/channel_runs.py without moving authorization into React

## Phase 4: React User Run Workspace

- [x] T020 [US1] Add channel run fetch/action helpers in frontend/admin/src/api/client.ts
- [x] T021 [US1] Create frontend/admin/src/components/userRuns/UserRunPage.tsx with bounded status/timeline/result/artifact loading
- [x] T022 [US1] Render safe status, progress, timeline, trace, result availability, artifact metadata, and unavailable states
- [x] T023 [US1] Wire `/admin/app/channels/runs` and `/admin/app/channels/runs/{run_id}` to UserRunPage in frontend/admin/src/App.tsx
- [x] T024 [US1] Ensure loading, denied, not-found, and dependency-unavailable states reuse safe React state patterns

## Phase 5: Start And Action Controls

- [x] T025 [US2] Add safe run start form controls to UserRunPage.tsx
- [x] T026 [US2] Add cancel action control using retained `/runs/{run_id}/cancel`
- [x] T027 [US2] Add waiting prompt approval/resume/reject/cancel controls using retained decision API
- [x] T028 [US2] Add terminal notification subscription action using retained subscription API
- [x] T029 [US2] Add callback registration action using retained callback API without echoing raw callback secrets
- [x] T030 [US2] Add artifact download grant action using retained artifact download API while avoiding storage paths
- [x] T031 [US2] Show action outcomes as safe status/audit/trace summaries only

## Phase 6: Jinja Retirement Evidence And Docs

- [x] T032 Delete or confirm deleted user-facing run templates and Jinja-only dependencies remain absent
- [x] T033 Remove or confirm absent TemplateResponse/Jinja imports from src/multi_agent_platform/api/routers/web_run_ui.py
- [x] T034 Update specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md with Spec 046 `/runs` retirement evidence
- [x] T035 Update docs/user-interaction-channels.md to prefer React browser destinations for user run links
- [x] T036 Update docs/quickstart.md with React-only `/runs` browser guidance
- [x] T037 Run scanner tests proving no user-facing run route references retired templates

## Phase 7: QA Docs And Validation

- [x] T038 [P] Create `.env.qa046`
- [x] T039 [P] Create `qa046.md`
- [x] T040 [P] Create `qa046_ui.md`
- [x] T041 [P] Create `qa046_user_guide.md`
- [x] T042 [P] Create `pr_notes.md`
- [x] T043 Patch validation.yml to use local-principal login and a React run status destination
- [x] T044 Run generated TypeScript contract check
- [x] T045 Run focused backend tests from quickstart
- [x] T046 Run frontend userRuns and App tests
- [x] T047 Run frontend build
- [x] T048 Run QA document validation
- [x] T049 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml`
- [x] T050 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/046-user-facing-run-ui-react-port-and-jinja-removal/validation.yml --start-processes`
- [x] T051 Inspect Playwright screenshot under output/playwright/qa046_ui

## Dependencies

- Tests T006-T012 before implementation changes.
- Contract generation T013-T015 before frontend client/component typing.
- Redirect compatibility T016-T019 before route deletion evidence T032-T037.
- User run status workspace T020-T024 before action controls T025-T031.
- QA document and validation tasks T038-T051 last.
