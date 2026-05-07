# User-Facing Run React UI Contract

## Browser Routes

- `GET /runs`: Authenticated legacy browser link. Redirects to `/admin/app/channels/runs` with allowlisted tenant context.
- `GET /runs/new`: Authenticated legacy browser link. Redirects to `/admin/app/channels/runs` with allowlisted tenant context.
- `GET /runs/{run_id}`: Authenticated legacy browser link. Validates safe access and redirects to `/admin/app/channels/runs/{run_id}` with allowlisted tenant context.
- `GET /admin/app/channels/runs`: React host route for the user-facing run start workspace.
- `GET /admin/app/channels/runs/{run_id}`: React host route for the user-facing run workspace.

## Retained JSON APIs

- `POST /runs`
- `GET /runs/{run_id}/status`
- `GET /runs/{run_id}/timeline`
- `GET /runs/{run_id}/events`
- `GET /runs/{run_id}/result`
- `POST /runs/{run_id}/approvals/{prompt_id}/decision`
- `POST /runs/{run_id}/cancel`
- `GET /runs/{run_id}/artifacts`
- `POST /runs/{run_id}/artifacts/{artifact_id}/download-url`
- `POST /runs/{run_id}/subscriptions`
- `POST /runs/{run_id}/callbacks`
- `POST /channels/telegram/link-token`

## React State Contract

The React page treats the retained JSON schemas as authoritative:

- `RunInvocationRequest` and `RunInvocationResponse` for start actions.
- `RunStatusResponse` and `WaitingPromptResponse` for state, progress, permitted actions, and approval prompts.
- `TimelineResponse` and `TimelineEventResponse` for bounded progress history.
- `RunResultResponse` for terminal safe summaries.
- `ArtifactListResponse` and `ArtifactDownloadUrlResponse` for artifact metadata and grants.
- `NotificationSubscriptionResponse`, `CallbackRegistrationResponse`, and `PromptDecisionResponse` for action results.

## Safe Rendering Rules

- Render status, timeline summaries, permitted actions, availability, audit/trace references, artifact names/types/statuses, and registration statuses.
- Do not render raw `inputs`, raw prompt context beyond safe summaries, raw completion/result bodies, callback secrets, private messages, full external identifiers, storage paths, stack traces, or unauthorized tenant labels.
