# Tasks: Real Skill Tool Execution Connectors

**Input**: Design documents from `/specs/021-real-skill-tool-execution-connectors/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Required. Write failing tests before implementation for gateway policy, adapters, redaction, runtime integration, admin diagnostics, and docs.

## Phase 1: Setup

- [x] T001 Create `src/multi_agent_platform/skill_execution/` package with public exports in `src/multi_agent_platform/skill_execution/__init__.py`.
- [x] T002 Create `src/multi_agent_platform/runtime/skill_tools.py` bridge for graph role node tool calls.
- [x] T003 Create admin diagnostics router placeholder in `src/multi_agent_platform/api/routers/admin_skill_execution.py`.
- [x] T004 Create diagnostics template directory and placeholder in `src/multi_agent_platform/web_admin/templates/skill_execution/diagnostics.html`.

## Phase 2: Tests First - Contracts And Security

- [x] T005 [P] [US1] Add gateway success and contract-shape tests in `tests/unit/skill_execution/test_gateway.py`.
- [x] T006 [P] [US1] Add adapter fixture output tests for calendar, Gmail, news, weather, and commute in `tests/unit/skill_execution/test_adapters.py`.
- [x] T007 [P] [US2] Add policy denial tests for uninstalled tool, blocked outbound domain, side-effect request, missing credential, and tenant mismatch in `tests/unit/skill_execution/test_policies.py`.
- [x] T008 [P] [US2] Add redaction tests for token-like values, secret references, raw email bodies, and sensitive URL queries in `tests/unit/skill_execution/test_redaction.py`.
- [x] T009 [P] [US1] Add OpenAPI/contract tests in `tests/contract/test_skill_execution_gateway_contract.py`.
- [x] T010 [P] [US1] Add runtime bridge tests in `tests/unit/runtime/test_runtime_skill_tools.py`.
- [x] T011 [P] [US3] Add admin diagnostics UI tests in `tests/integration/api/test_admin_skill_execution_ui.py`.

## Phase 3: Gateway Foundation

- [x] T012 [US1] Implement Pydantic schemas in `src/multi_agent_platform/skill_execution/schemas.py`.
- [x] T013 [US2] Implement redaction helpers in `src/multi_agent_platform/skill_execution/redaction.py`.
- [x] T014 [US2] Implement policy evaluation primitives in `src/multi_agent_platform/skill_execution/policies.py`.
- [x] T015 [US1] Implement deterministic fixture payloads in `src/multi_agent_platform/skill_execution/fixtures.py`.
- [x] T016 [US1] Implement adapter registry and first-party read-only adapters in `src/multi_agent_platform/skill_execution/adapters.py`.
- [x] T017 [US1] Implement `SkillExecutionGateway` orchestration in `src/multi_agent_platform/skill_execution/gateway.py`.

## Phase 4: Runtime And Admin Integration

- [x] T018 [US1] Implement graph runtime bridge in `src/multi_agent_platform/runtime/skill_tools.py`.
- [x] T019 [US3] Implement admin diagnostics API and UI routes in `src/multi_agent_platform/api/routers/admin_skill_execution.py`.
- [x] T020 [US3] Register admin diagnostics router in `src/multi_agent_platform/api/main.py`.
- [x] T021 [US3] Implement diagnostics template in `src/multi_agent_platform/web_admin/templates/skill_execution/diagnostics.html`.
- [x] T022 [US3] Add admin navigation entry if supported by the existing shell in `src/multi_agent_platform/web_admin/templates/admin/base.html` or the local navigation provider.

## Phase 5: Documentation And QA Artifacts

- [x] T023 [P] Update `docs/skill-registry.md` with runtime tool execution, mock fixtures, live-probe guardrails, and diagnostics.
- [x] T024 [P] Update `docs/quickstart.md` with the diagnostics route and QA021 validation pointers.
- [x] T025 [P] Add QA environment file at `specs/021-real-skill-tool-execution-connectors/.env.qa021`.
- [x] T026 [P] Add generated QA validation guide at `specs/021-real-skill-tool-execution-connectors/qa021.md`.
- [x] T027 [P] Add generated Playwright QA guide at `specs/021-real-skill-tool-execution-connectors/qa021_ui.md`.
- [x] T028 [P] Add non-developer manual QA guide at `specs/021-real-skill-tool-execution-connectors/qa021_user_guide.md`.

## Phase 6: Validation

- [x] T029 Run targeted tests for skill execution and admin diagnostics.
- [x] T030 Run `uv run ruff check .`.
- [x] T031 Run `uv run ruff format --check .`.
- [x] T032 Run `uv run mypy src`.
- [x] T033 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.
- [x] T034 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/021-real-skill-tool-execution-connectors/validation.yml`.
- [x] T035 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/021-real-skill-tool-execution-connectors/validation.yml --start-processes`.

## Dependencies & Execution Order

- Phase 1 creates file anchors.
- Phase 2 tests should fail before Phases 3 and 4 implementation.
- Phase 3 blocks runtime and admin integration.
- Phase 4 blocks UI Playwright validation.
- Phase 5 can proceed after source paths and route names stabilize.
- Phase 6 validates the completed feature.

## Parallel Opportunities

- T005 through T011 can be authored in parallel because they target disjoint test files.
- T023 through T028 can be authored in parallel after route names stabilize.
- Adapter implementation inside T016 can split by tool family if future sub-agent execution is explicitly requested.
