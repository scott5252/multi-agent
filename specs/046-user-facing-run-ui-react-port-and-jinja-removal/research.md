# Research: User-Facing Run UI React Port And Jinja Removal

## Decision: Use retained `/runs` JSON APIs as the run lifecycle source of truth

**Rationale**: `channel_runs.py` already owns start, status, timeline, events, result, artifact, approval, cancel, subscription, callback, and Telegram link-token behavior with tenant actor mapping and idempotency checks. React should call those APIs instead of duplicating lifecycle rules.

**Alternatives considered**: A new React-only aggregate endpoint was rejected because it would duplicate channel run authorization and increase drift risk before Spec 047.

## Decision: Serve legacy `/runs` browser links through authenticated redirects to React

**Rationale**: `web_run_ui.py` already no longer renders templates and can validate run access before redirecting detail routes. Redirects preserve bookmarked links, Telegram-safe run links, browser navigation, and start-form compatibility without keeping Jinja. `/runs` and `/runs/new` should land on `/admin/app/channels/runs`; `/runs/{run_id}` should land on `/admin/app/channels/runs/{run_id}`.

**Alternatives considered**: Returning a standalone HTML response at `/runs/{run_id}` was rejected because it would create another host surface to decommission. Returning `410 Gone` was rejected because safe direct links must keep working.

## Decision: Add a focused React user run workspace under the existing app host

**Rationale**: The current channel React app already handles local-principal shell/bootstrap, safe navigation, and static asset serving. A `userRuns` component can expose run-specific start/status/actions without another bundle or auth model.

**Alternatives considered**: Extending the broad channel dashboard with all run lifecycle controls was rejected because it would make operational Telegram/briefing panels carry user workflow state.

## Decision: Use bounded polling in React validation while retaining SSE API tests

**Rationale**: SSE is already exposed by the retained `/runs/{run_id}/events` endpoint and should remain covered by backend tests. Playwright validation is more stable when the browser uses bounded fetches for status/timeline/result/artifact state.

**Alternatives considered**: Browser SSE-only validation was rejected as unnecessarily flaky for QA evidence.

## Decision: Treat Spec 044 admin run inspection work as complete and out of scope

**Rationale**: Spec 044 already converted and deleted admin run inspection templates. Spec 046 focuses only on user-facing `/runs` direct links and retained channel APIs.

**Alternatives considered**: Reopening admin run inspection pages was rejected as duplicate scope and higher regression risk.
