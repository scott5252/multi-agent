# Feature Specification: User-Facing Run UI React Port And Jinja Removal

**Feature Branch**: `codex/046-user-facing-run-ui-react-port-and-jinja-removal`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Implement the user-facing run UI React port and Jinja removal for `/runs`, preserving start/status/timeline/progress/approval/result/artifact/subscription/callback flows, safe direct links, tenant/principal scope, idempotency, and redaction."

## Clarifications

### Session 2026-05-07

- Q: Which user-facing run surface is canonical after Jinja removal? -> A: (autopilot) Authenticated legacy `/runs` and `/runs/new` browser links redirect to `/admin/app/channels/runs`, legacy `/runs/{run_id}` links redirect to `/admin/app/channels/runs/{run_id}`, and `/runs` JSON APIs remain the source of truth for mutations and status data.
- Q: Should Spec 046 remove admin run inspection assets already retired by Spec 044? -> A: (autopilot) No. Spec 046 owns user-facing `/runs` compatibility and React parity evidence only; admin run inspection remains complete under Spec 044.
- Q: How should real-time progress be represented in the React browser flow? -> A: (autopilot) Use bounded polling against retained JSON endpoints and keep SSE as a retained API capability with backend tests.
- Q: How should unavailable, unauthorized, or cross-tenant run links behave? -> A: (autopilot) Return safe JSON problems from APIs and authenticated React redirects for browser routes without exposing whether unauthorized data exists.
- Q: How are raw run payloads, prompts, artifacts, callbacks, and identifiers shown? -> A: (autopilot) Show safe summaries, state, audit references, and artifact metadata only; never render raw payloads, raw prompts, private messages, full callback payloads, or unauthorized tenant labels.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open And Track A Run In React (Priority: P1)

A signed-in tenant user opens an existing `/runs/{run_id}` browser link from a web session, Telegram notification, or callback email and lands in a React experience that shows safe status, progress, timeline, result availability, artifact metadata, subscription/callback state, and next action without any Jinja rendering.

**Why this priority**: Existing safe run links must remain usable before the `/runs` templates can stay removed.

**Independent Test**: Start a run through the retained `/runs` API, open `/runs/{run_id}` with a local-principal browser session, confirm the browser redirects to React, and verify status/progress/timeline/result/artifact summary content is loaded from backend-owned JSON endpoints.

**Acceptance Scenarios**:

1. **Given** a tenant user has a queued or running workflow run, **When** they open `/runs/{run_id}`, **Then** the response redirects to a React run workspace for the same run and preserves tenant query context.
2. **Given** a user opens a run from another tenant, **When** React requests the safe run data, **Then** the UI shows a non-revealing unavailable state and backend tests prove the API does not disclose cross-tenant existence.
3. **Given** timeline updates exist for a run, **When** the React page polls or refreshes, **Then** the page shows bounded progress and safe timeline summaries without raw prompts or payloads.

---

### User Story 2 - Start And Manage A Run Without Jinja Forms (Priority: P2)

A signed-in tenant user opens the React run workspace from `/runs` or `/runs/new`, starts a workflow from the browser, supplies a safe text input, receives the created run link, and can cancel, subscribe, register callback metadata, and decide waiting prompts through React-backed controls that call retained JSON APIs with idempotency keys.

**Why this priority**: The old Jinja start form and detail page covered more than display; parity must include safe actions.

**Independent Test**: Use React unit tests and backend integration tests to start a run, perform cancel/subscription/callback actions, and approve/reject/resume/cancel a waiting prompt while checking idempotency and stale-decision behavior.

**Acceptance Scenarios**:

1. **Given** a tenant user opens `/runs` or `/runs/new`, **When** the browser redirects to React, **Then** the user can start a run from `/admin/app/channels/runs` and the backend records a deterministic idempotency key.
2. **Given** a run is waiting for approval, **When** the user selects an allowed prompt action, **Then** the backend returns the updated safe status and stale decisions return a safe conflict.
3. **Given** a run supports terminal notifications and callbacks, **When** the user registers those actions, **Then** React shows only subscription/callback status and safe trace/audit references.

---

### User Story 3 - Preserve Safe Compatibility And Deletion Evidence (Priority: P3)

An operator or reviewer verifies that no `/runs` Jinja templates or browser-rendering handlers remain and that every legacy direct link has a documented React redirect or non-Jinja safe response.

**Why this priority**: Complete Jinja removal needs deletion-grade evidence before Spec 047 removes global infrastructure.

**Independent Test**: Run scanner tests, route tests, QA docs validation, redaction sweeps, full Spec QA, and Playwright against the React run workspace.

**Acceptance Scenarios**:

1. **Given** the repository after implementation, **When** scanner tests inspect user-facing run files, **Then** no retired `/runs` template path, `TemplateResponse`, or Jinja template provider is referenced by `web_run_ui.py`.
2. **Given** old browser routes `/runs`, `/runs/new`, and `/runs/{run_id}`, **When** authenticated users open them, **Then** they redirect to React destinations or safe detail routes while API endpoints remain JSON.
3. **Given** QA artifacts are reviewed, **When** the redaction sweep runs, **Then** no raw prompt, raw run payload, private channel message, callback secret, full Telegram identifier, local filesystem path, or stack trace is present.

### Edge Cases

- Missing authentication returns the existing safe auth-required behavior before React data is loaded.
- Cross-tenant or unknown run identifiers produce safe unavailable states and do not reveal whether a run exists.
- Waiting prompt decisions with stale prompt versions return safe conflicts without changing run state.
- Replayed start, cancel, subscription, callback, artifact grant, or prompt decisions use idempotency keys and return deterministic evidence.
- Artifact downloads expose only short-lived download grants from retained APIs, not raw storage paths.
- SSE remains available as a retained API capability, while React browser validation may use bounded polling to avoid flaky browser evidence.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST serve every authenticated browser request for `/runs`, `/runs/new`, and `/runs/{run_id}` without rendering Jinja templates.
- **FR-002**: The system MUST preserve retained JSON APIs for run start, status, timeline, events, result, artifacts, artifact download grants, approvals, cancel, subscriptions, callbacks, and Telegram link-token creation.
- **FR-003**: The React run workspace MUST provide a canonical start route at `/admin/app/channels/runs` and detail routes at `/admin/app/channels/runs/{run_id}`.
- **FR-004**: The React run workspace MUST load safe run status, progress, timeline, result availability, artifact metadata, permitted actions, subscription state, and callback/subscription outcomes from backend-owned contracts.
- **FR-005**: The React run workspace MUST allow start, cancel, approval/resume/reject/cancel decisions, subscription registration, callback registration, and artifact grant requests when the backend marks those actions permitted.
- **FR-006**: Legacy browser redirects MUST preserve safe route parameters and tenant query context and MUST avoid reflecting arbitrary query values.
- **FR-007**: Backend tests MUST prove Auth0-shaped and local-principal authorization behavior, including same-tenant success, cross-tenant denial, unauthenticated denial, and role-bound behavior.
- **FR-008**: UI tests and Playwright validation MUST prove local-principal users can open React run pages from legacy links and complete the safe browser journey without Jinja.
- **FR-009**: Retired `/runs` templates and Jinja-only static assets MUST remain deleted, and scanners MUST fail if user-facing run routes reintroduce `TemplateResponse`, `Jinja2Templates`, or retired template names.
- **FR-010**: QA artifacts, screenshots, exports, logs, and UI text MUST not expose raw run payloads, raw prompts, raw completions, private messages, raw artifact bodies, callback secrets, full external identifiers, local filesystem paths, stack traces, or unauthorized tenant labels.
- **FR-011**: Admin run inspection routes and operations workbench behavior completed in Spec 044 MUST remain out of scope except for ensuring links from user-facing run evidence remain safe.

### Key Entities *(include if feature involves data)*

- **Run Invocation**: A tenant-scoped request to start a workflow run, including workflow identifier, safe user input summary, channel, and idempotency evidence.
- **Run Status**: A safe user-visible state projection containing progress, latest cursor, permitted actions, waiting prompt summary, terminal outcome, result availability, artifact availability, and trace/audit references.
- **Timeline Event**: A safe event summary with order, state, severity, occurrence time, and trace reference.
- **Waiting Prompt**: A user decision request with prompt identifier, prompt version, allowed actions, deadline, and safe context summary.
- **Run Result**: A safe terminal result projection with availability, summary, and redacted structured result metadata.
- **Artifact Metadata**: A safe artifact listing with identifier, name, user-facing type, status, download availability, and bounded size metadata.
- **Subscription And Callback Registration**: Status records proving notification or callback registration without exposing callback secrets or private payloads.
- **Compatibility Redirect**: A legacy browser route response that maps old `/runs` links to React destinations while preserving only safe context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of old `/runs` browser routes covered by tests return React redirects or safe non-Jinja responses.
- **SC-002**: 100 percent of retained `/runs` JSON lifecycle endpoints used by the React flow are covered by backend tests for same-tenant success and cross-tenant denial where applicable.
- **SC-003**: Playwright evidence captures a local-principal user opening a legacy run link and viewing the React run workspace with status, timeline, action, and artifact/result sections visible.
- **SC-004**: Scanner tests find zero user-facing run references to deleted templates, `TemplateResponse`, `Jinja2Templates`, or `workflow_ui_templates`.
- **SC-005**: Redaction checks over QA docs and Playwright screenshots find zero raw prompts, raw payloads, callback secrets, full external identifiers, local filesystem paths, stack traces, or unauthorized tenant labels.
- **SC-006**: Focused backend and frontend tests, generated contracts, QA document validation, full Spec QA, and Playwright validation pass for `qa046`.

## Assumptions

- The retained channel run JSON APIs remain the source of truth for run lifecycle behavior.
- React can use bounded polling for browser progress validation while SSE remains covered by backend API tests.
- Existing local-principal test catalogs provide deterministic tenant users and tenant admins for QA.
- Admin-only run inspection and operations workbench Jinja removal was completed by Spec 044 and is not duplicated here.
- Spec 047 will remove global Jinja infrastructure after all domain surfaces, including this one, are proven React-only or non-Jinja.
