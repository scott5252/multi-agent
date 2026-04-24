# Feature Specification: User Interaction Channels

**Feature Branch**: `006-user-interaction-channels`  
**Created**: 2026-04-24  
**Status**: Draft  
**Input**: User description: "Add user interaction channels to the multi-agent platform: Web UI, Telegram, and Web APIs. All channels must route into the same workflow invocation model, share authentication and authorization policies where applicable, and support live progress, persisted status retrieval, terminal completion notifications, and final result retrieval by run identifier. Define a consistent run lifecycle across channels, including queued, running, waiting-for-input, completed, failed, and canceled states. Focus this spec on channel adapters and user interaction flows, not new workflow logic. Include approval and resume interactions, plus artifact download behavior. Require at least 90 percent unit-test coverage, PR review notes, testing instructions, and a README update."

## Clarifications

### Session 2026-04-24

- Q: How should channels prevent duplicate user requests or repeated channel deliveries from creating conflicting run effects? → A: Require client-supplied idempotency keys for duplicate-prone actions.
- Q: How should Telegram users establish the trusted association to a platform identity before protected actions are allowed? → A: Platform sign-in plus a short-lived one-time Telegram linking token.
- Q: How should artifact downloads be delivered across Web UI, Telegram, and Web API channels? → A: All channels provide short-lived platform-authenticated artifact download URLs.
- Q: Who should receive terminal-state notifications for a run? → A: The initiating user is automatically subscribed; additional authorized users may explicitly subscribe per run.
- Q: How should rate limiting and throttling apply across Web UI, Telegram, and Web API channels? → A: Shared platform limits apply by tenant, platform identity, and action type, with channel/provider throttles allowed to be stricter.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start Workflow Runs From Any Channel (Priority: P1)

As an authenticated user, I need to start an allowed workflow from the Web UI, Telegram, or a Web API and receive the same run identifier and lifecycle behavior so that I can choose the interaction channel that fits my work without changing what the platform does.

**Why this priority**: Unified invocation is the foundation for every other interaction flow; without it, channels would become separate products with inconsistent permissions and run behavior.

**Independent Test**: Can be fully tested by invoking the same eligible workflow from each channel, confirming that each invocation creates a run with equivalent request details, policy enforcement, initial lifecycle state, and returned run identifier.

**Acceptance Scenarios**:

1. **Given** a user is authorized to start a workflow, **When** the user submits the required inputs from the Web UI, Telegram, or a Web API, **Then** the platform creates one workflow run through the shared invocation model and returns the run identifier through that channel.
2. **Given** a user lacks permission to start a workflow, **When** the user attempts invocation from any channel, **Then** the platform rejects the request consistently and does not create a run.
3. **Given** a workflow requires input values, **When** the user omits required values from any channel, **Then** the channel explains the missing information and the platform does not start an incomplete run.

---

### User Story 2 - Track Run Progress and Status (Priority: P2)

As a user monitoring a workflow, I need live progress updates, durable status lookup, terminal-state notifications, and final result retrieval by run identifier so that I can safely leave and return to a run from the same or another channel.

**Why this priority**: Long-running workflows need reliable visibility and recovery; users should not depend on a single active session to know what happened.

**Independent Test**: Can be fully tested by starting a run, observing live progress in each supported channel, disconnecting, retrieving persisted status by run identifier, receiving completion notification when the run reaches a terminal state, and retrieving final results by run identifier.

**Acceptance Scenarios**:

1. **Given** a run is queued or running, **When** a user views it from any authorized channel, **Then** the user sees the current lifecycle state, latest progress summary, and run identifier.
2. **Given** a user disconnects or changes channel while a run continues, **When** the user later requests the run by identifier, **Then** the persisted status and latest available progress are shown.
3. **Given** a run reaches completed, failed, or canceled, **When** the terminal state is recorded, **Then** the initiating user and any additional authorized users who explicitly subscribed to the run receive a completion notification appropriate to their channel and permissions.
4. **Given** a run has final results, **When** an authorized user requests results by run identifier from any supported channel, **Then** the channel presents the final result or a clear explanation of why the result is unavailable.

---

### User Story 3 - Approve, Reject, and Resume Waiting Runs (Priority: P3)

As an authorized reviewer, I need to respond to workflow approval and resume prompts from supported channels so that runs waiting for human input can continue or stop without requiring a special operator-only path.

**Why this priority**: Human-in-the-loop workflows are already part of the platform direction; channel adapters must expose those interactions consistently without redefining workflow logic.

**Independent Test**: Can be fully tested by moving a run into `waiting-for-input`, presenting the pending decision in each channel, submitting an approved, rejected, or resumed response, and confirming that the run lifecycle changes consistently.

**Acceptance Scenarios**:

1. **Given** a run is waiting for approval, **When** an authorized reviewer opens the prompt from any supported channel, **Then** the reviewer sees the decision request, available actions, relevant context, and run identifier.
2. **Given** a reviewer approves or resumes a waiting run, **When** the response is accepted, **Then** the run leaves `waiting-for-input` and continues according to the existing workflow behavior.
3. **Given** a reviewer rejects or cancels a waiting run, **When** the response is accepted, **Then** the run moves to the appropriate terminal or stopped state and the decision is visible in subsequent status retrieval.
4. **Given** an unauthorized user attempts to answer a waiting prompt, **When** the response is submitted from any channel, **Then** the platform rejects the response and leaves the run unchanged.

---

### User Story 4 - Retrieve Artifacts and Delivery Evidence (Priority: P4)

As a workflow user or reviewer, I need to download run artifacts and verify delivery materials so that completed work can be inspected, shared, and reviewed with clear instructions.

**Why this priority**: Artifact access and release evidence make the feature usable beyond status tracking and help maintainers validate the delivered channel behavior.

**Independent Test**: Can be fully tested by completing a run that produces artifacts, retrieving artifact metadata and downloads from each authorized channel, and reviewing coverage evidence, PR review notes, testing instructions, and README updates.

**Acceptance Scenarios**:

1. **Given** a run produced downloadable artifacts, **When** an authorized user views the run by identifier, **Then** the channel lists available artifacts with names, types, sizes when known, and download actions.
2. **Given** an authorized user requests an artifact from any supported channel, **When** the artifact is available, **Then** the channel provides a short-lived platform-authenticated download URL rather than sending artifact bytes directly.
3. **Given** a short-lived artifact download URL expires, is reused outside its authorization context, or references unavailable content, **When** the user attempts retrieval, **Then** the platform denies retrieval safely and the channel can provide a fresh authorized retrieval action when allowed.
4. **Given** the feature is submitted for review, **When** a maintainer evaluates the delivery, **Then** unit-test coverage, PR review notes, testing instructions, and README guidance are present and cover all supported channels.

### Edge Cases

- A user starts a run in one channel and later monitors, approves, cancels, resumes, or retrieves results from another channel.
- A run is created successfully but stays in `queued` longer than expected; channels continue to show persisted state rather than implying failure.
- A live progress connection drops while the run continues; the user can recover by retrieving the run by identifier.
- A terminal completion notification cannot be delivered because a subscribed user blocked the channel, revoked access, lost authorization, or the channel is temporarily unavailable.
- A Telegram identity is not linked to a platform identity, the linking token is expired or already used, or the platform session cannot be verified; channel access is limited until the user completes a valid platform sign-in and one-time Telegram linking flow.
- A Web API caller uses credentials that are valid for status retrieval but not for approvals or artifact download.
- A run enters `waiting-for-input` with multiple eligible reviewers; only one accepted decision should affect the run, and later responses must see the updated status.
- A run is canceled while a progress viewer or approval prompt is open; the next action must show the canceled state and prevent stale decisions.
- A final result or artifact is unavailable because the run failed, was canceled, expired, was removed by retention policy, or is outside the user's authorization scope.
- A channel sends duplicate invocation, approval, resume, cancel, notification acknowledgement, or artifact download requests; the user sees a consistent outcome without duplicate run effects.
- A user or integration exceeds a platform rate limit across one or more channels; equivalent actions are throttled by tenant, platform identity, and action type, while provider-specific channel throttles may impose stricter delivery limits.
- Artifact names, result summaries, and progress messages may contain sensitive content; channels must display only what the requesting user is authorized to see.
- A user requests an unknown, malformed, or cross-tenant run identifier; the platform returns a safe not-found or unauthorized response without disclosing protected run details.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST support user interaction through Web UI, Telegram, and Web API channels for workflow invocation, progress viewing, status retrieval, approval and resume responses, cancellation, final result retrieval, and artifact download.
- **FR-002**: Every channel MUST route workflow starts into the same workflow invocation model so that the resulting run has one canonical run identifier, requester identity, input record, authorization decision, and lifecycle history.
- **FR-003**: Channel adapters MUST NOT introduce new workflow decision logic; they may collect user input, present workflow state, enforce channel-specific interaction constraints, and forward accepted user actions to existing workflow behavior.
- **FR-004**: The platform MUST apply shared authentication and authorization policies across channels wherever the channel can establish a platform identity.
- **FR-005**: Telegram interactions MUST require the user to sign in through the platform and confirm a short-lived one-time Telegram linking token that expires within 10 minutes before allowing protected workflow starts, approvals, resumes, status retrieval, result retrieval, cancellation, or artifact downloads.
- **FR-006**: Web UI and Web API interactions MUST enforce the same tenant, role, and workflow permissions for equivalent user actions.
- **FR-007**: The platform MUST return a stable run identifier for every accepted workflow invocation and require that identifier for persisted status retrieval, final result retrieval, and artifact lookup.
- **FR-008**: The platform MUST expose a consistent run lifecycle with exactly these user-visible states: `queued`, `running`, `waiting-for-input`, `completed`, `failed`, and `canceled`.
- **FR-009**: Every channel MUST display or return the current run lifecycle state using the shared state names and consistent meanings.
- **FR-010**: The platform MUST preserve enough status history for users to retrieve the latest known state, progress summary, waiting prompt when applicable, terminal outcome, and final result availability by run identifier.
- **FR-011**: Channels MUST support live progress updates for active runs when the channel has an active user session or conversation capable of receiving updates.
- **FR-012**: Channels MUST support persisted status retrieval by run identifier even when live progress was missed or unavailable.
- **FR-013**: The platform MUST automatically subscribe the initiating user to terminal-state notifications and MUST allow additional authorized users to explicitly subscribe per run; subscribed users MUST be notified when the run reaches `completed`, `failed`, or `canceled`, subject to current authorization, channel availability, and user notification preferences.
- **FR-014**: Terminal-state notifications MUST include the run identifier, terminal state, and next available action, without exposing unauthorized result or artifact content.
- **FR-015**: Authorized users MUST be able to retrieve final run results by run identifier after completion.
- **FR-016**: Final result retrieval MUST clearly distinguish completed results, failed-run summaries, canceled-run summaries, unavailable results, expired results, and unauthorized access.
- **FR-017**: The platform MUST present `waiting-for-input` runs with the pending prompt, eligible actions, deadline when available, requester or reviewer context when authorized, and run identifier.
- **FR-018**: Authorized reviewers MUST be able to approve, reject, resume, or cancel a waiting run from any supported channel when those actions are valid for the prompt.
- **FR-019**: Approval, rejection, resume, and cancellation responses MUST be validated against the user's current authorization, the run's current lifecycle state, and the prompt's allowed actions before changing run state.
- **FR-020**: Stale responses to prompts that have already been answered, canceled, completed, failed, or superseded MUST be rejected with the latest retrievable run status.
- **FR-021**: Authorized users MUST be able to list downloadable artifacts for a run by run identifier when artifacts exist.
- **FR-022**: Artifact listings MUST include artifact name, user-facing type, size when known, creation or availability status, and a short-lived platform-authenticated download URL action with a default TTL of 15 minutes and a configurable maximum of 60 minutes when retrieval is allowed.
- **FR-023**: Artifact download behavior MUST enforce the same authorization policy as run result retrieval and MUST use short-lived platform-authenticated URLs rather than direct channel file delivery.
- **FR-024**: The platform MUST record channel source, authenticated actor, requested action, run identifier when known, authorization outcome, and user-visible result for invocation, status, approval, resume, cancellation, result retrieval, notification, and artifact actions.
- **FR-025**: Channel-specific errors MUST be presented in user-friendly language while preserving a consistent error category for unauthorized access, missing input, invalid run identifier, unavailable channel delivery, invalid lifecycle action, and platform failure.
- **FR-026**: Channel adapters MUST require client-supplied idempotency keys for duplicate-prone invocation, approval, rejection, resume, cancellation, notification acknowledgement, and artifact download requests, and repeated requests with the same key MUST return the existing accepted outcome without creating conflicting user-visible effects.
- **FR-027**: Channel adapters MUST enforce shared platform rate limits across Web UI, Telegram, and Web API channels by tenant, platform identity, and action type, while allowing channel/provider throttles to impose stricter delivery limits.
- **FR-028**: The delivered feature MUST include unit-test evidence showing at least 90 percent coverage for the submitted channel-adapter and user-interaction behavior.
- **FR-029**: The delivered feature MUST include PR review notes covering shared invocation, lifecycle consistency, authorization behavior, approval and resume flows, notifications, artifact access, cross-channel recovery, and known risks.
- **FR-030**: The delivered feature MUST include testing instructions that allow reviewers to verify Web UI, Telegram, and Web API invocation, live progress, persisted status retrieval, terminal notifications, final result retrieval, approvals, resumes, cancellation, and artifact downloads.
- **FR-031**: The delivered feature MUST update the README with user-facing guidance for available channels, run lifecycle states, run identifier usage, approval and resume behavior, notifications, artifact downloads, and review verification steps.

### Key Entities

- **Channel Adapter**: A user interaction surface for Web UI, Telegram, or Web API that collects user actions, presents run information, and forwards accepted actions to the shared workflow invocation and run interaction model.
- **Platform Identity**: The authenticated user, service, or linked channel account used to evaluate permissions and personalize channel interactions.
- **Channel Session**: A web session, Telegram conversation, or Web API caller context through which a user starts, monitors, or acts on workflow runs.
- **Workflow Invocation Request**: A user-submitted request to start a workflow, including selected workflow, provided inputs, channel source, requester identity, and authorization outcome.
- **Run Identifier**: The stable identifier returned for an accepted workflow run and used across channels for status, progress, approval, resume, cancellation, result, and artifact interactions.
- **Run Lifecycle State**: The user-visible state of a run: `queued`, `running`, `waiting-for-input`, `completed`, `failed`, or `canceled`.
- **Progress Update**: A user-facing summary of current run activity, latest milestone, timestamp, and lifecycle state.
- **Waiting Prompt**: A durable human-interaction request for approval, rejection, resume input, or cancellation decision while a run is in `waiting-for-input`.
- **Terminal Notification**: A channel-delivered message that tells an authorized user a run has reached `completed`, `failed`, or `canceled`.
- **Run Notification Subscription**: A per-run notification preference automatically created for the initiating user and explicitly created by any additional authorized user who wants terminal-state notifications.
- **Final Result**: The final user-facing outcome, summary, or structured response available for a run after completion or a terminal failure or cancellation summary.
- **Run Artifact**: A downloadable output associated with a run, with metadata, authorization requirements, and a short-lived platform-authenticated download URL retrieval action.
- **Interaction Audit Record**: A durable record of user and channel actions related to invocation, status viewing, approvals, resumes, cancellations, notifications, final results, and artifact retrieval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 percent of accepted workflow invocations from Web UI, Telegram, and Web API channels return a stable run identifier and create runs through the shared invocation model.
- **SC-002**: 100 percent of equivalent protected actions enforce the same authorization outcome across channels when the same platform identity and permissions are used.
- **SC-003**: Users can retrieve the latest persisted status for any authorized run by run identifier in under 2 seconds during normal operating conditions.
- **SC-004**: Active users receive live progress updates for at least 95 percent of observable lifecycle changes while their channel session or conversation remains reachable.
- **SC-005**: 100 percent of runs that reach `completed`, `failed`, or `canceled` produce a terminal-state notification attempt for the initiating user and each explicitly subscribed user who remains authorized.
- **SC-006**: Users can retrieve final results by run identifier for 100 percent of completed runs that have available results and for which the user remains authorized.
- **SC-007**: 100 percent of waiting-run approval, rejection, resume, and cancellation attempts are accepted only when the user is authorized, the prompt is current, and the action is valid.
- **SC-008**: 100 percent of stale prompt responses return the latest run status without changing the run.
- **SC-009**: Authorized users can access downloadable artifact metadata and a valid retrieval action for 100 percent of completed runs with available artifacts.
- **SC-010**: At least 90 percent of users in acceptance testing can start a run, locate it by identifier, monitor status, and retrieve the final result without assistance.
- **SC-011**: Submitted channel-adapter and user-interaction behavior demonstrates at least 90 percent unit-test coverage.
- **SC-012**: PR review notes, testing instructions, and README guidance are present and sufficient for a maintainer to verify all supported channel flows without additional verbal explanation.
- **SC-013**: 100 percent of rate-limited channel actions return a consistent throttling category and do not bypass shared tenant, platform identity, and action-type limits by switching channels.

## Testing, Review, And Documentation Impact

- **Testing Instructions**: Reviewer instructions must cover Web UI, Telegram,
  and Web API invocation, live progress, persisted status retrieval, terminal
  notifications, final result retrieval, approvals, resumes, cancellation,
  artifact downloads, auth denials, rate limits, and cross-channel recovery.
- **PR Review Guidance**: PR notes must call out shared invocation behavior,
  lifecycle consistency, authorization behavior, Telegram identity linking,
  approval/resume flows, notification delivery, artifact access, idempotency,
  rate limiting, cross-channel recovery, observability, and known risks.
- **Documentation Impact**: The feature requires updates to `README.md`,
  `docs/quickstart.md`, and a new `docs/user-interaction-channels.md` guide
  covering available channels, run lifecycle states, run identifier usage,
  Telegram linking, approval/resume behavior, notifications, artifact downloads,
  callback behavior, rate limits, and review verification steps.

## Constitution Impact

- **Durability**: Run identifiers, lifecycle state, progress summaries, waiting prompts, terminal outcomes, notification attempts, final result availability, artifact metadata, and interaction audit records must be durable enough for cross-channel recovery.
- **Tenant Isolation And Fairness**: Every channel action must include tenant-aware identity context and enforce tenant boundaries and shared rate limits for invocation, status, approvals, resumes, notifications, results, and artifacts.
- **Versioning**: User-visible lifecycle states, channel interaction contracts, notification payloads, and artifact metadata expectations must be compatibility-managed so existing clients and in-flight runs remain understandable.
- **Secrets And Tool Access**: Channel messages, notifications, logs, audit records, and artifact metadata must avoid exposing secrets or unauthorized result content.
- **Artifact Storage**: Artifacts remain governed by the platform artifact model; this feature defines how channels list and retrieve them, not a new artifact storage system.
- **Approval And Resume**: Human approval and resume prompts must remain durable, authorized, and recoverable across channels while preserving the existing workflow's decision semantics.
- **Observability**: Channel adapters must provide traceable user and channel actions for debugging invocation, progress, approval, resume, notification, result, and artifact flows.
- **Security**: Existing platform authentication and authorization are reused wherever applicable, with Telegram access limited to securely linked identities before protected actions are allowed.

## Assumptions

- Existing workflow definitions, workflow execution behavior, approval semantics, and resume semantics already exist or will be supplied by related runtime features; this feature only exposes them through user interaction channels.
- Web UI, Telegram, and Web APIs are the required channels for this feature; additional channels are out of scope for this specification.
- Web API refers to user-facing programmatic access for external clients and integrations, not a separate workflow execution engine.
- Telegram users must complete an identity-linking or authentication process before accessing protected tenant or workflow data.
- Live progress delivery is best effort while the user session or channel conversation is reachable; persisted status retrieval by run identifier is the source of truth after interruptions.
- Terminal-state notifications are attempted for the initiating user and explicitly subscribed authorized users, but failed delivery does not change the run lifecycle state or final result availability.
- Artifact download permissions are at least as restrictive as final result retrieval permissions, and artifact bytes are retrieved through short-lived platform-authenticated URLs rather than direct channel file delivery.
- This feature may add presentation and adapter behavior but does not introduce new workflow logic, new workflow states beyond the specified lifecycle, or new artifact storage rules.
