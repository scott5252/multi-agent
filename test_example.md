# Daily Intelligence Briefing Test Example

Review date: 2026-05-04

This file documents how to set up the "Daily Intelligence Briefing" scenario
from `/Users/scottcornell/Downloads/multi-agent-testbed.md` against the current
`multi-agent-platform` codebase. It incorporates the feature specs created after
the original test example:

- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime`
- `specs/021-real-skill-tool-execution-connectors`
- `specs/022-telegram-natural-language-trigger-delivery-persistence`
- `specs/023-user-briefing-preferences-and-context`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates`
- `specs/025-live-model-credential-resolution-for-gateway-calls`

## Implementation Verdict

The current product can now implement a governed, browser-administered,
DB-backed, and deterministic QA version of the scenario:

- tenant setup
- local-principal admin login
- model provider records
- live model provider credential resolution through safe secret references
- prompt library records
- agent and sub-agent runtime profiles
- skill package and tenant installation metadata
- Daily Briefing skill execution diagnostics with mock Calendar, Gmail, news,
  weather, and commute tool outputs
- user briefing preference profiles and runtime preference resolution
- workflow draft authoring with parallel branch and join structure
- DB-backed workflow graph execution with deterministic role-node outputs,
  parallel waves, joins, checkpoints, handoffs, side-effect intent evidence,
  approval pauses, and safe final output references
- test-bench suites and mock-mode test runs
- workflow publish gates that query current authoritative test-bench evidence
- persistent Telegram link-token, identity-link, update-receipt, alias, and
  delivery-attempt records
- Telegram natural-language alias handling for `Morning briefing`, with
  deterministic result formatting and mockable or real Bot API delivery
- audit, operations, usage, and test evidence views

The current product cannot fully implement the live scenario end to end yet.
Specifically, the Daily Briefing connector adapters currently provide governed
mock fixtures and live-probe interfaces rather than real Google Calendar, Gmail,
news, weather, or traffic provider payloads. The graph executor uses a
deterministic role-node executor by default; it proves graph semantics and safe
runtime evidence, but it does not yet synthesize the sample briefing from live
external tool results through a fully wired prompt/model/tool agent loop.
Telegram alias delivery is implemented, but the deterministic local path
formats a safe completion summary instead of waiting for live external-agent
synthesis.

Use the setup below for a current-code demonstration and QA harness. Use the
spec-specific QA documents under `specs/020` through `specs/025` for deeper
feature validation.

## Current Code Structure Reviewed

The scenario setup below is grounded in these current code areas:

- `system_architecture.md` and `user_guide.md`
- `src/multi_agent_platform/api/main.py`
- `src/multi_agent_platform/api/routers/channel_runs.py`
- `src/multi_agent_platform/api/routers/telegram_webhook.py`
- `src/multi_agent_platform/channels/service.py`
- `src/multi_agent_platform/channels/telegram.py`
- `src/multi_agent_platform/admin/telegram_config/service.py`
- `src/multi_agent_platform/api/routers/admin_telegram.py`
- `src/multi_agent_platform/admin/workflow_registry/*`
- `src/multi_agent_platform/api/schemas/workflow_registry.py`
- `src/multi_agent_platform/runtime/orchestration/service.py`
- `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- `src/multi_agent_platform/workers/orchestration.py`
- `src/multi_agent_platform/prompts/*`
- `src/multi_agent_platform/agents/*`
- `src/multi_agent_platform/model_providers/*`
- `src/multi_agent_platform/config/*`
- `src/multi_agent_platform/admin/skill_registry/*`
- `src/multi_agent_platform/skill_execution/*`
- `src/multi_agent_platform/runtime/skill_tools.py`
- `src/multi_agent_platform/admin/briefing_preferences/*`
- `src/multi_agent_platform/runtime/briefing_preferences.py`
- `src/multi_agent_platform/channels/telegram_delivery.py`
- `src/multi_agent_platform/testing/agent_bench/*`
- `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- `src/multi_agent_platform/api/routers/admin_briefing_preferences.py`
- `src/multi_agent_platform/api/routers/admin_skill_execution.py`
- `src/multi_agent_platform/db/models/agent_tests.py`
- `src/multi_agent_platform/db/models/briefing_preferences.py`
- `src/multi_agent_platform/db/models/telegram_config.py`
- `src/multi_agent_platform/db/repositories/agent_tests.py`
- `src/multi_agent_platform/db/repositories/briefing_preferences.py`
- `src/multi_agent_platform/db/repositories/telegram_config.py`
- `specs/015-agent-workflow-test-bench/plan.md`
- `specs/015-agent-workflow-test-bench/spec.md`
- `specs/015-agent-workflow-test-bench/quickstart.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/*`
- `specs/021-real-skill-tool-execution-connectors/*`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/*`
- `specs/023-user-briefing-preferences-and-context/*`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/*`
- `specs/025-live-model-credential-resolution-for-gateway-calls/*`

## Scenario To Build

A user sends a morning Telegram request:

```text
Morning briefing
```

The intended Orchestrator Agent receives the request, determines the current
date and user context, and fans out to four independent sub-agents:

1. Calendar Scout: reads today's calendar events, classifies priority, and
   detects conflicts.
2. Email Triage Agent: reads unread or recent Gmail messages, summarizes
   threads, extracts actions, and elevates VIP senders.
3. News And Context Agent: searches news based on user interests, ranks
   relevance, and summarizes headlines.
4. Logistics Agent: fetches weather, checks commute or transit conditions, and
   cross-references calendar locations.

After those four finish, an optional Focus Recommender uses the aggregated
results to propose one to three focus items. The Orchestrator synthesizes a
single clean briefing and returns it to the user through Telegram.

The target output resembles:

```text
Good Morning - Monday, May 4

TODAY'S SCHEDULE
- 9:00 AM - Standup (30 min)
- 11:00 AM - Product Review (back-to-back with your 12pm)
- 2:00 PM - Investor Call - HIGH PRIORITY

EMAIL
- Sarah K. - "Launch date moved up" -> Decision needed
- Legal - "Contract redline ready" -> Review and sign
- Jake - Quick question on budget -> Low urgency

IN THE NEWS
- OpenAI releases a new reasoning model
- Fed signals rate hold through Q3
- Industry update: new EU data rules take effect next month

LOGISTICS
- Providence: 58 F, partly cloudy, light rain by 3pm
- Investor Call is remote - Zoom link is in calendar

SUGGESTED FOCUS
1. Prep for Investor Call
2. Respond to Sarah about launch date
3. Block time to review the contract before EOD
```

## Current Capability Map

| Scenario requirement | Current support | Codebase used | Implementable now |
| --- | --- | --- | --- |
| Telegram account linking | Admin-issued link tokens and consumed identity links persist in PostgreSQL; the legacy channel link-token endpoint remains in-memory | `channels/telegram.py`, `admin/telegram_config/service.py`, `db/repositories/telegram_config.py`, `db/repositories/channels.py` | Yes |
| Telegram trigger | Exact-match tenant aliases such as `Morning briefing` route to a published workflow version; slash commands such as `/run` still work | `channels/telegram.py`, `admin/telegram_config/service.py`, `api/routers/admin_telegram.py` | Yes |
| Telegram bot reply | Alias-triggered results are formatted and sent through a mockable or real `sendMessage` client; delivery attempts persist with safe fingerprints | `channels/telegram_delivery.py`, `channels/telegram.py`, `api/routers/telegram_webhook.py` | Yes with configured Bot API secret or test-injected mock client |
| Workflow authoring | Browser/API workflow draft model supports roles, subagent roles, nodes, edges, joins, contracts, skills, test requirements | `api/schemas/workflow_registry.py` | Yes |
| Parallel sub-agent execution | DB-backed graph executor loads published bundle documents, schedules ready nodes in waves, runs independent scout branches concurrently, evaluates joins, and records timeline/checkpoint/handoff evidence | `runtime/orchestration/graph_execution.py`, `workers/orchestration.py` | Yes for deterministic role-node QA |
| Runtime model calls | `ModelGateway` supports OpenAI and local OpenAI-compatible chat completions with per-call secret resolution through configured secret providers | `model_providers/gateway.py`, `model_providers/probes.py`, `model_providers/secrets.py` | Yes for gateway/probe paths; graph role nodes still use deterministic execution by default |
| Prompt/profile setup | Prompt and agent runtime profile services exist | `prompts/`, `agents/` | Yes |
| Skill registry | Skill manifests, tenant grants, installs, credentials, smoke/readiness metadata exist; admin service is in-memory | `admin/skill_registry/` | Yes for metadata demos |
| Daily Briefing tool connectors | `SkillExecutionGateway` exposes read-only Calendar, Gmail, news, weather, and commute adapter contracts, mock fixtures, policy checks, credential summaries, redaction, and diagnostics | `skill_execution/*`, `runtime/skill_tools.py`, `api/routers/admin_skill_execution.py` | Yes for mock/local diagnostics; not yet real external provider reads |
| Test bench | Durable suite/case/run tables and mock sandbox execution exist | `testing/agent_bench/`, `db/models/agent_tests.py` | Yes |
| Publish gate test evidence | Workflow publish gate evaluation queries current same-tenant test-bench evidence for the active draft revision; legacy `latest_result_status` remains compatibility metadata | `admin/workflow_registry/service.py`, `admin/workflow_registry/publish_gate.py`, `testing/agent_bench/service.py` | Yes |
| User preferences | Tenant users can save, export, import, summarize, and resolve Daily Briefing preference profiles with immutable revisions and safe summaries | `admin/briefing_preferences/*`, `runtime/briefing_preferences.py`, `api/routers/admin_briefing_preferences.py` | Yes |

## Spec 020-025 Updates Incorporated

| Spec | Change to this test example | Detail to verify |
| --- | --- | --- |
| 020 | The workflow graph is no longer authoring-only. A DB-backed graph executor can run published bundle documents with deterministic role-node outputs. | Verify graph waves, four parallel scout nodes, join policy decisions, checkpoints, handoff envelopes, side-effect intent evidence, manual-resolution pauses, resume idempotency, tenant mismatch denial, and redaction. |
| 021 | Daily Briefing tools now have a governed `SkillExecutionGateway` and mock fixture adapters. | Verify all five tool families succeed in mock diagnostics, policy denials block adapter invocation, credentials are represented as safe metadata, and raw email bodies/secrets/URL query strings are redacted. |
| 022 | Telegram now supports tenant-scoped exact aliases such as `Morning briefing`, persistent identity links, update receipts, and Bot API delivery attempts. | Verify alias creation, normalized matching, linked-identity enforcement, duplicate update replay, disabled-config denial, mocked or real `sendMessage` delivery, and safe fingerprints. |
| 023 | Daily Briefing preferences are first-class user context. | Verify profile save/reload, immutable revisions, safe admin summaries, JSON export/import ownership checks, runtime resolution, and tenant/principal isolation. |
| 024 | Required workflow test evidence is authoritative test-bench data rather than a manually copied status field. | Verify required suite evidence is bound to the current `workflow_draft_id` and current revision id, stale or cross-tenant evidence blocks publish, and UI summaries show required/passing/missing/failing/stale counts. |
| 025 | Provider probes and gateway calls resolve credentials live from secret references. | Verify OpenAI fails closed without a resolvable reference, local OpenAI-compatible no-auth is allowed only for allowlisted local endpoints, configured references are passed to adapters, and raw secret values never render. |

## Step-By-Step Setup With Current Code

### Step 1 - Prepare The Local Environment

From the repository root:

```bash
uv sync
cp .env.example .env
```

Edit `.env` for a local demo:

```bash
APP_ENV=local
AUTH_MODE=local_principal
DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5432/multi_agent_platform
TELEGRAM_WEBHOOK_SECRET=local-dev-secret
TELEGRAM_PROVIDER_TOKEN_REF=env:TELEGRAM_BOT_TOKEN
# Use the current .env.example LOCAL_PRINCIPAL_CATALOG_JSON. It must include
# platform-admin and tenant-admin-acme permissions for telegram-config,
# agent-tests, briefing-preferences, skill-execution, usage, operations, and
# tenant admin work.
LOCAL_PRINCIPAL_CATALOG_JSON=<copy-current-.env.example-value>
```

If you are using a real Telegram bot for webhook testing, also provide the
environment secret used by your deployment convention:

```bash
SECRET_PROVIDER=env
ENV_SECRET_PREFIX=MAP_SECRET_
MAP_SECRET_TELEGRAM_BOT_TOKEN=<telegram-bot-token-from-botfather>
```

If you are testing a live OpenAI provider connection instead of the local
OpenAI-compatible path, store only a secret reference on the provider record and
provide the referenced value through the configured secret provider:

```bash
SECRET_PROVIDER=env
ENV_SECRET_PREFIX=MAP_SECRET_
MAP_SECRET_OPENAI_API_KEY=<openai-api-key>
```

Use `OPENAI_API_KEY` as the provider credential secret reference id in the
admin model-provider form. The resolver reads `MAP_SECRET_OPENAI_API_KEY` at
probe/runtime call time and never stores the raw value on the provider record.

Codebase used by this step:

- `config/settings.py`
- `.env.example`
- `compose.yaml`
- `auth/local_principals.py`

Current-code review: this step is fully supported.

### Step 2 - Start PostgreSQL And Apply Migrations

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

Create the Acme tenant used by this scenario:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform <<'SQL'
INSERT INTO tenants (
  tenant_id,
  slug,
  display_name,
  status,
  created_at,
  updated_at
)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  'acme',
  'Acme',
  'active',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING;
SQL
```

Codebase used by this step:

- `alembic/versions/*.py`
- `db/models/*`
- `db/session.py`

Current-code review: this step is fully supported.

### Step 3 - Start The API And Optional Worker

Terminal 1:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2, optional:

```bash
uv run python -m multi_agent_platform.workers.main
```

Open the admin console:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin
```

Choose `platform-admin` for platform-wide setup and `tenant-admin-acme` for
tenant-scoped setup.

Codebase used by this step:

- `api/main.py`
- `workers/main.py`
- `workers/loops.py`
- `workers/orchestration.py`
- `runtime/orchestration/graph_execution.py`

Current-code review: API startup is fully supported. The worker now claims
DB-backed orchestration work and runs published workflow bundle documents
through `GraphExecutionService`. This proves deterministic graph execution,
parallel wave scheduling, joins, checkpoints, handoffs, and safe output
evidence for DB-backed runs. The public channel facade still keeps its user
visible channel run state in process memory, so the Telegram alias demo below
uses deterministic channel completion/delivery rather than waiting on a worker
graph result.

### Step 4 - Configure Telegram For The Acme Tenant

Open:

```text
http://127.0.0.1:8000/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111
```

In the browser:

1. Review provider readiness.
2. Enable Telegram for Acme.
3. Keep protected commands enabled for `/run`, `/status`, `/result`,
   `/approve`, `/reject`, `/resume`, `/cancel`, and `/artifacts`.
4. Confirm the `Telegram Command Aliases` section is visible. Create the
   `Morning briefing` alias after the workflow has been published in Step 11,
   because the alias must reference an immutable published workflow version id.
5. Issue the link token after alias setup in Step 12 so the token and identity
   link are persisted through the admin Telegram repository path.

Codebase used by this step:

- `api/routers/admin_telegram.py`
- `admin/telegram_config/service.py`
- `db/models/telegram_config.py`
- `channels/service.py`

Current-code review: Telegram configuration, command aliases, link-token audit,
identity summaries, persistent runtime identity links, update receipts, local
webhook command parsing, and mockable or real Bot API delivery are supported.
Alias routing enforces tenant Telegram readiness before starting the run.

### Step 5 - Configure A Model Provider

Open:

```text
http://127.0.0.1:8000/admin/model-providers
```

For a current-code local demo, prefer a local OpenAI-compatible endpoint:

1. Create a provider connection.
2. Set provider type to `local_openai_compatible`.
3. Set base URL to an allowlisted endpoint, for example
   `http://127.0.0.1:11434`.
4. Add one model id exposed by that endpoint.
5. Set visibility for the Acme tenant.
6. Activate the connection after review.

For a live OpenAI connection, create an `openai` provider record and store only
credential references, not raw keys. Use a reference such as `OPENAI_API_KEY`
when `SECRET_PROVIDER=env` and `MAP_SECRET_OPENAI_API_KEY` are configured.
OpenAI probes fail closed with `secret_reference_invalid` when a reference is
missing or cannot be resolved. Local OpenAI-compatible providers may run
without credentials only when the base URL is on the configured local endpoint
allowlist.

Codebase used by this step:

- `model_providers/service.py`
- `model_providers/gateway.py`
- `model_providers/openai_adapter.py`
- `model_providers/local_adapter.py`
- `model_providers/secrets.py`
- `model_providers/probes.py`
- `api/routers/admin_model_providers.py`

Current-code review: provider records, probes, gateway calls, live credential
resolution, local no-auth allowlist behavior, safe failure summaries, usage
capture, and gateway attempt evidence are supported. The graph role-node
executor does not automatically call model providers in this daily briefing
demo unless a role executor is explicitly wired to do so.

### Step 6 - Create Prompt Library Entries

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts
```

Create and publish prompt versions for:

1. `daily-briefing-orchestrator`
2. `calendar-scout`
3. `email-triage`
4. `news-context`
5. `logistics-agent`
6. `focus-recommender`
7. `briefing-synthesizer`

Recommended prompt purposes:

- Orchestrator: parse the briefing request, select today's date and user
  context, delegate to scouts, tolerate partial failures, and prepare final
  synthesis inputs.
- Calendar Scout: summarize today's events, priority, conflicts, and travel
  requirements.
- Email Triage: identify recent unread or important email that requires action.
- News Context: summarize user-topic news with relevance rationale.
- Logistics Agent: summarize weather, commute, and location constraints.
- Focus Recommender: rank focus items from the aggregated scout outputs.
- Briefing Synthesizer: turn structured scout outputs into the final concise
  Telegram-ready briefing.

Codebase used by this step:

- `prompts/service.py`
- `prompts/validation.py`
- `prompts/preview.py`
- `api/routers/admin_prompts.py`

Current-code review: prompt creation, validation, publication, grants, preview,
and history are supported. Current runtime graph execution does not yet load
these prompt versions to perform the final daily briefing.

### Step 7 - Create Agent And Sub-Agent Runtime Profiles

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles
```

Create and activate these profiles:

| Profile | Agent key | Agent kind in profile UI | Purpose |
| --- | --- | --- | --- |
| Orchestrator Agent | `daily_briefing_orchestrator` | `agent` | coordinates request, fan-out, failure handling, and synthesis |
| Calendar Scout | `calendar_scout` | `sub_agent` | returns today's calendar summary |
| Email Triage Agent | `email_triage` | `sub_agent` | returns recent email actions |
| News And Context Agent | `news_context` | `sub_agent` | returns relevant news |
| Logistics Agent | `logistics_agent` | `sub_agent` | returns weather and commute flags |
| Focus Recommender | `focus_recommender` | `sub_agent` | returns one to three focus recommendations |
| Briefing Synthesizer | `briefing_synthesizer` | `agent` | formats final Telegram briefing |

For each profile:

1. Attach the matching prompt version from Step 6.
2. Add model routing hints for the provider from Step 5.
3. Add skill requirements for the external skills in Step 8 where applicable.
4. Add output contract expectations matching the workflow contracts in Step 9.
5. Validate the profile.
6. Activate the profile version.
7. Grant the version to Acme if the profile is platform-scoped.

Codebase used by this step:

- `agents/service.py`
- `agents/validation.py`
- `agents/resolution.py`
- `api/routers/admin_agent_profiles.py`

Current-code review: profile lifecycle and resolution are supported. The live
runtime does not yet execute a workflow node by resolving the profile and
invoking its prompt/model/tool stack.

### Step 8 - Register Skill Packages And Tenant Installations

Open:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages
```

Create platform skill packages and publish immutable versions for:

| Skill package slug | Tool id | Approved integration ref | Action category | Credential style |
| --- | --- | --- | --- | --- |
| `daily-briefing-calendar` | `google_calendar.events.read` | `tool:google-calendar:v1` | `read` | delegated credential |
| `daily-briefing-gmail` | `gmail.messages.read` | `tool:gmail:v1` | `read` | delegated credential |
| `daily-briefing-news` | `news.search` | `tool:web-search:v1` | `search` | secret reference |
| `daily-briefing-weather` | `weather.forecast.read` | `tool:weather:v1` | `read` | secret reference |
| `daily-briefing-commute` | `commute.lookup` | `tool:maps-traffic:v1` | `read` | secret reference |

Use this manifest pattern for each package, replacing the bracketed values:

```json
{
  "schema_version": "1.0",
  "slug": "daily-briefing-calendar",
  "semantic_version": "1.0.0",
  "description": "Read-only calendar event lookup for daily briefing workflows.",
  "entrypoint": {
    "type": "approved_tool_ref",
    "approved_integration_ref": "tool:google-calendar:v1"
  },
  "tools": [
    {
      "tool_id": "google_calendar.events.read",
      "approved_integration_ref": "tool:google-calendar:v1",
      "display_name": "Read calendar events",
      "description": "Reads tenant-approved user calendar events for the requested day.",
      "action_categories": ["read"],
      "side_effect_profile": "read_only",
      "safe_usage": "Use only for tenant-authorized calendar reads."
    }
  ],
  "action_categories": ["read"],
  "network_requirements": [
    {
      "tool_id": "google_calendar.events.read",
      "action_category": "read",
      "allowed_schemes": ["https"],
      "allowed_domain_patterns": ["googleapis.com"],
      "allowed_ports": [443],
      "required": true,
      "safe_description": "Google Calendar API endpoint."
    }
  ],
  "credential_requirements": [
    {
      "requirement_key": "calendar-read-delegated",
      "credential_kind": "google_calendar_oauth",
      "tool_id": "google_calendar.events.read",
      "action_category": "read",
      "required": true,
      "delegated_credential_scopes": ["calendar.readonly"],
      "safe_description": "Delegated read-only calendar access."
    }
  ],
  "runtime_permissions": [
    {
      "permission_key": "calendar-read",
      "permission_type": "tool_access",
      "tool_id": "google_calendar.events.read",
      "action_category": "read",
      "side_effect_level": "read_only",
      "required": true,
      "safe_description": "Read calendar events."
    }
  ],
  "test_fixtures": [
    {
      "fixture_key": "calendar-read-policy-preview",
      "tool_id": "google_calendar.events.read",
      "action_category": "read",
      "fixture_kind": "policy_preview",
      "safe_input_summary": "Policy-only calendar read probe.",
      "fixture_digest": "sha256:calendar-fixture",
      "requires_credentials": true,
      "expected_outcome": "passed",
      "timeout_seconds": 10
    }
  ],
  "compatibility": {"platform_min_version": "0.1.0"},
  "safe_documentation": {
    "summary": "Read-only daily briefing calendar skill.",
    "documentation_digest": "sha256:calendar-docs",
    "redaction_classification": "safe",
    "support_contacts": ["ops@example.com"]
  },
  "artifact_digests": {
    "package": "sha256:calendar-package",
    "documentation": "sha256:calendar-docs"
  }
}
```

For each package:

1. Create the package.
2. Paste the manifest candidate.
3. Validate the manifest.
4. Publish version `1.0.0`.
5. Grant the version to Acme.
6. Switch to Acme tenant scope.
7. Install the version.
8. Configure credential references only, never raw credentials.
9. Run smoke/readiness checks.
10. Preview binding eligibility.

Codebase used by this step:

- `admin/skill_registry/manifest.py`
- `admin/skill_registry/validation.py`
- `admin/skill_registry/service.py`
- `admin/skill_registry/readiness.py`
- `admin/skill_registry/smoke_runner.py`
- `api/routers/admin_skill_registry.py`
- `skill_execution/gateway.py`
- `skill_execution/adapters.py`
- `skill_execution/policies.py`
- `runtime/skill_tools.py`
- `api/routers/admin_skill_execution.py`

Current-code review: package, validation, publication, grant, installation,
credential readiness, smoke readiness, and binding eligibility metadata are
supported. The admin skill registry service is process-local in memory, so the
state is lost when the API process restarts unless the service is replaced with
a persistent implementation. Spec 021 adds a separate runtime
`SkillExecutionGateway` with concrete mock adapters for the five Daily Briefing
tool families, safe policy checks, credential summaries, fixture outputs,
redaction, and admin diagnostics. These adapters are suitable for local QA and
staging interface validation; they are not live Google/Gmail/news/weather/maps
provider clients.

After registering metadata, open:

```text
http://127.0.0.1:8000/admin/skill-execution/ui/diagnostics?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected current-code result:

- all five tool families are listed
- mock diagnostic runs return `succeeded`
- request and response summaries are redacted
- credential readiness is represented by safe labels and references
- no raw email body, access token, secret value, or sensitive URL query string
  appears in the page or API payloads

### Step 8A - Create User Briefing Preferences

Open:

```text
http://127.0.0.1:8000/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111
```

Sign in as `tenant-admin-acme` and save the Acme user's Daily Briefing context:

- Location label: `Providence, RI`
- Timezone: `America/New_York`
- News topics: `AI, fintech, climate`
- VIP senders: `Sarah K., Legal`
- Workday: `09:00` to `17:00`
- Commute mode: `driving`
- Calendar account reference: `delegated:calendar:acme-user`
- Email account reference: `delegated:gmail:acme-user`
- Output style: `standard`
- Scheduled delivery: disabled for this on-demand test, or enabled with
  `08:00` for scheduled-flow QA

API equivalent:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/admin/briefing-preferences/api/profile \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "location_label": "Providence, RI",
    "timezone": "America/New_York",
    "news_topics": ["AI", "fintech", "climate"],
    "vip_senders": ["Sarah K.", "Legal"],
    "workday_start": "09:00",
    "workday_end": "17:00",
    "commute_mode": "driving",
    "calendar_account_ref": "delegated:calendar:acme-user",
    "email_account_ref": "delegated:gmail:acme-user",
    "output_style": "standard",
    "scheduled_enabled": false
  }'
```

Resolve the runtime context that the Telegram alias path will attach to
`Morning briefing` inputs:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/admin/briefing-preferences/api/resolve \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "principal_id": "tenant-admin-acme",
    "source_channel": "telegram",
    "trace_id": "daily-briefing-preferences-check"
  }'
```

Codebase used by this step:

- `admin/briefing_preferences/service.py`
- `admin/briefing_preferences/models.py`
- `admin/briefing_preferences/redaction.py`
- `runtime/briefing_preferences.py`
- `api/routers/admin_briefing_preferences.py`
- `db/models/briefing_preferences.py`
- `db/repositories/briefing_preferences.py`

Current-code review: preference save/read/update, immutable revisions, safe
admin summaries, export/import, runtime resolution, audit events, validation,
and tenant/principal isolation are supported. Account fields must be safe
references such as `delegated:...`, `secret-ref:...`, `account:...`, `local:...`,
or `none`; raw OAuth tokens, passwords, and API keys are rejected.

### Step 9 - Create The Workflow Draft

Open:

```text
http://127.0.0.1:8000/admin/workflows/ui
```

Create a tenant-scoped main workflow:

- Slug: `daily-intelligence-briefing`
- Display name: `Daily Intelligence Briefing`
- Scope: Acme tenant
- Workflow kind: `main_workflow`
- Entry node: `orchestrator-intake`

Model this graph:

```text
orchestrator-intake
  -> calendar-scout
  -> email-triage
  -> news-context
  -> logistics-agent
calendar-scout, email-triage, news-context, logistics-agent
  -> scout-join
scout-join
  -> focus-recommender
focus-recommender
  -> briefing-synthesizer
briefing-synthesizer
  -> terminal
```

Use an `all_success` join policy for the four scout branches. This models the
intended parallel fan-out in the current workflow authoring schema.

Minimum authoring document shape:

```json
{
  "workflow_key": "daily-intelligence-briefing",
  "display_name": "Daily Intelligence Briefing",
  "description": "Telegram-triggered daily briefing workflow with calendar, email, news, logistics, focus, and synthesis roles.",
  "workflow_kind": "main_workflow",
  "entry_node_key": "orchestrator-intake",
  "roles": [
    {
      "role_key": "orchestrator",
      "display_name": "Orchestrator Agent",
      "role_kind": "agent",
      "purpose": "Parse the request, fan out to scouts, tolerate partial failures, and prepare synthesis inputs.",
      "responsibilities": ["parse request", "delegate scouts", "handle partial failures"],
      "profile_reference_key": "profile-orchestrator",
      "input_contract_key": "briefing-request",
      "output_contract_key": "orchestration-plan",
      "graph_node_keys": ["orchestrator-intake"]
    },
    {
      "role_key": "calendar-scout",
      "display_name": "Calendar Scout",
      "role_kind": "subagent",
      "purpose": "Summarize today's calendar and conflicts.",
      "profile_reference_key": "profile-calendar-scout",
      "input_contract_key": "briefing-request",
      "output_contract_key": "calendar-result",
      "skill_installation_keys": ["daily-briefing-calendar-install"],
      "graph_node_keys": ["calendar-scout-node"]
    },
    {
      "role_key": "email-triage",
      "display_name": "Email Triage Agent",
      "role_kind": "subagent",
      "purpose": "Summarize recent email actions.",
      "profile_reference_key": "profile-email-triage",
      "input_contract_key": "briefing-request",
      "output_contract_key": "email-result",
      "skill_installation_keys": ["daily-briefing-gmail-install"],
      "graph_node_keys": ["email-triage-node"]
    },
    {
      "role_key": "news-context",
      "display_name": "News And Context Agent",
      "role_kind": "subagent",
      "purpose": "Return relevant headlines and context.",
      "profile_reference_key": "profile-news-context",
      "input_contract_key": "briefing-request",
      "output_contract_key": "news-result",
      "skill_installation_keys": ["daily-briefing-news-install"],
      "graph_node_keys": ["news-context-node"]
    },
    {
      "role_key": "logistics-agent",
      "display_name": "Logistics Agent",
      "role_kind": "subagent",
      "purpose": "Return weather, commute, and event-location flags.",
      "profile_reference_key": "profile-logistics-agent",
      "input_contract_key": "briefing-request",
      "output_contract_key": "logistics-result",
      "skill_installation_keys": ["daily-briefing-weather-install", "daily-briefing-commute-install"],
      "graph_node_keys": ["logistics-node"]
    },
    {
      "role_key": "focus-recommender",
      "display_name": "Focus Recommender",
      "role_kind": "subagent",
      "purpose": "Recommend one to three focus items from aggregated scout outputs.",
      "profile_reference_key": "profile-focus-recommender",
      "input_contract_key": "scout-results",
      "output_contract_key": "focus-result",
      "graph_node_keys": ["focus-node"]
    },
    {
      "role_key": "briefing-synthesizer",
      "display_name": "Briefing Synthesizer",
      "role_kind": "agent",
      "purpose": "Render the final Telegram-ready briefing.",
      "profile_reference_key": "profile-briefing-synthesizer",
      "input_contract_key": "focus-result",
      "output_contract_key": "briefing-output",
      "graph_node_keys": ["synthesis-node"]
    }
  ],
  "prompt_profile_references": [
    {"reference_key": "profile-orchestrator", "role_key": "orchestrator", "agent_key": "daily_briefing_orchestrator", "agent_kind": "agent", "readiness_status": "ready"},
    {"reference_key": "profile-calendar-scout", "role_key": "calendar-scout", "agent_key": "calendar_scout", "agent_kind": "sub_agent", "readiness_status": "ready"},
    {"reference_key": "profile-email-triage", "role_key": "email-triage", "agent_key": "email_triage", "agent_kind": "sub_agent", "readiness_status": "ready"},
    {"reference_key": "profile-news-context", "role_key": "news-context", "agent_key": "news_context", "agent_kind": "sub_agent", "readiness_status": "ready"},
    {"reference_key": "profile-logistics-agent", "role_key": "logistics-agent", "agent_key": "logistics_agent", "agent_kind": "sub_agent", "readiness_status": "ready"},
    {"reference_key": "profile-focus-recommender", "role_key": "focus-recommender", "agent_key": "focus_recommender", "agent_kind": "sub_agent", "readiness_status": "ready"},
    {"reference_key": "profile-briefing-synthesizer", "role_key": "briefing-synthesizer", "agent_key": "briefing_synthesizer", "agent_kind": "agent", "readiness_status": "ready"}
  ],
  "skill_installations": [
    {"skill_installation_key": "daily-briefing-calendar-install", "skill_slug": "daily-briefing-calendar", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "daily-briefing-gmail-install", "skill_slug": "daily-briefing-gmail", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "daily-briefing-news-install", "skill_slug": "daily-briefing-news", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "daily-briefing-weather-install", "skill_slug": "daily-briefing-weather", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "daily-briefing-commute-install", "skill_slug": "daily-briefing-commute", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"}
  ],
  "contracts": [
    {"contract_key": "briefing-request", "display_name": "Briefing Request", "contract_kind": "workflow_input", "json_schema": {"type": "object", "required": ["text"], "properties": {"text": {"type": "string"}}}, "example_payload": {"text": "Morning briefing"}},
    {"contract_key": "orchestration-plan", "display_name": "Orchestration Plan", "json_schema": {"type": "object"}},
    {"contract_key": "calendar-result", "display_name": "Calendar Result", "json_schema": {"type": "object"}},
    {"contract_key": "email-result", "display_name": "Email Result", "json_schema": {"type": "object"}},
    {"contract_key": "news-result", "display_name": "News Result", "json_schema": {"type": "object"}},
    {"contract_key": "logistics-result", "display_name": "Logistics Result", "json_schema": {"type": "object"}},
    {"contract_key": "scout-results", "display_name": "Scout Results", "json_schema": {"type": "object"}},
    {"contract_key": "focus-result", "display_name": "Focus Result", "json_schema": {"type": "object"}},
    {"contract_key": "briefing-output", "display_name": "Briefing Output", "contract_kind": "workflow_output", "json_schema": {"type": "object", "required": ["briefing_text"], "properties": {"briefing_text": {"type": "string"}}}}
  ],
  "nodes": [
    {"node_key": "orchestrator-intake", "node_type": "role", "display_name": "Orchestrator Intake", "role_key": "orchestrator"},
    {"node_key": "calendar-scout-node", "node_type": "role", "display_name": "Calendar Scout", "role_key": "calendar-scout"},
    {"node_key": "email-triage-node", "node_type": "role", "display_name": "Email Triage", "role_key": "email-triage"},
    {"node_key": "news-context-node", "node_type": "role", "display_name": "News Context", "role_key": "news-context"},
    {"node_key": "logistics-node", "node_type": "role", "display_name": "Logistics", "role_key": "logistics-agent"},
    {"node_key": "scout-join", "node_type": "join", "display_name": "Join Scout Results", "join_policy_key": "all-scouts-return"},
    {"node_key": "focus-node", "node_type": "role", "display_name": "Focus Recommender", "role_key": "focus-recommender"},
    {"node_key": "synthesis-node", "node_type": "role", "display_name": "Briefing Synthesizer", "role_key": "briefing-synthesizer"},
    {"node_key": "terminal", "node_type": "terminal", "display_name": "Briefing Complete"}
  ],
  "edges": [
    {"edge_key": "orchestrator-to-calendar", "source_node_key": "orchestrator-intake", "target_node_key": "calendar-scout-node", "contract_key": "briefing-request"},
    {"edge_key": "orchestrator-to-email", "source_node_key": "orchestrator-intake", "target_node_key": "email-triage-node", "contract_key": "briefing-request"},
    {"edge_key": "orchestrator-to-news", "source_node_key": "orchestrator-intake", "target_node_key": "news-context-node", "contract_key": "briefing-request"},
    {"edge_key": "orchestrator-to-logistics", "source_node_key": "orchestrator-intake", "target_node_key": "logistics-node", "contract_key": "briefing-request"},
    {"edge_key": "calendar-to-join", "source_node_key": "calendar-scout-node", "target_node_key": "scout-join", "contract_key": "calendar-result"},
    {"edge_key": "email-to-join", "source_node_key": "email-triage-node", "target_node_key": "scout-join", "contract_key": "email-result"},
    {"edge_key": "news-to-join", "source_node_key": "news-context-node", "target_node_key": "scout-join", "contract_key": "news-result"},
    {"edge_key": "logistics-to-join", "source_node_key": "logistics-node", "target_node_key": "scout-join", "contract_key": "logistics-result"},
    {"edge_key": "join-to-focus", "source_node_key": "scout-join", "target_node_key": "focus-node", "contract_key": "scout-results"},
    {"edge_key": "focus-to-synthesis", "source_node_key": "focus-node", "target_node_key": "synthesis-node", "contract_key": "focus-result"},
    {"edge_key": "synthesis-to-terminal", "source_node_key": "synthesis-node", "target_node_key": "terminal", "contract_key": "briefing-output"}
  ],
  "join_policies": [
    {
      "join_policy_key": "all-scouts-return",
      "strategy": "all_success",
      "inbound_edge_keys": ["calendar-to-join", "email-to-join", "news-to-join", "logistics-to-join"],
      "required_branches": ["calendar", "email", "news", "logistics"],
      "failure_behavior": "manual_resolution",
      "output_merge_contract_key": "scout-results"
    }
  ],
  "approval_gates": [],
  "subworkflow_refs": [],
  "test_requirements": []
}
```

After creating the draft:

1. Save it.
2. Validate it.
3. Review graph preview.
4. Resolve blocking findings.
5. Do not publish until Step 10 test evidence has been produced.

Codebase used by this step:

- `api/schemas/workflow_registry.py`
- `admin/workflow_registry/validation.py`
- `admin/workflow_registry/reference_validation.py`
- `admin/workflow_registry/graph_preview.py`
- `admin/workflow_registry/service.py`
- `runtime/orchestration/graph_execution.py`
- `runtime/orchestration/graph_roles.py`

Current-code review: authoring and validation of this graph structure are
supported. DB-backed execution of this graph as deterministic parallel
role-node work is implemented by Spec 020. The current executor schedules the
four scout role nodes in one wave, evaluates the join, runs focus and synthesis
nodes after the join, persists checkpoints and handoffs, and emits safe
timeline events. It does not yet turn the prompt/profile/tool stack into live
external-agent synthesis by default.

Focused automated graph proof:

```bash
uv run pytest --no-cov -vv \
  tests/integration/runtime/test_workflow_graph_execution.py::test_daily_briefing_graph_schedules_four_scouts_in_one_wave \
  tests/integration/runtime/test_workflow_graph_execution.py::test_manual_resolution_join_pauses_and_persists_approval \
  tests/integration/workers/test_orchestration_worker.py::test_orchestration_worker_executes_claimed_graph_run
```

Expected: the Daily Briefing graph schedules the four scout nodes in one wave,
manual-resolution join behavior persists an approval pause when a branch fails,
and the worker executes a claimed graph run.

### Step 10 - Create Test Bench Evidence

Open:

```text
http://127.0.0.1:8000/admin/agent-tests/ui
```

Create a suite:

- Name: `Daily Briefing Mock Smoke`
- Tenant: Acme
- Target type: `workflow_draft`
- Target id: use the actual `workflow_draft_id` for
  `daily-intelligence-briefing`
- Target version: use the current `workflow_draft_revision_id`
- Default safe mode: `mock_model`
- Model mode: `mock`
- Tool mode: `mock`
- Pass threshold: `1.0`
- Required for publish: enabled

Add at least one case:

```json
{
  "request": "Morning briefing",
  "date": "2026-05-04",
  "location": "Providence, RI",
  "topics": ["AI", "fintech", "climate"],
  "vip_senders": ["Sarah K.", "Legal"]
}
```

Expected contract shape:

```json
{
  "status": "string",
  "contract": "object"
}
```

Assertions:

```json
[
  {
    "kind": "deterministic",
    "path": "status",
    "comparator": "equals",
    "expected_value": "passed",
    "severity": "blocking"
  },
  {
    "kind": "deterministic",
    "path": "contract.summary",
    "comparator": "contains",
    "expected_value": "Morning briefing",
    "severity": "blocking"
  }
]
```

Run the suite in `mock_model` mode and capture the run id. After the mock run
passes, add a required test declaration to the workflow draft:

```json
{
  "requirement_key": "daily-briefing-smoke",
  "suite_id": "<agent_test_suite_id>",
  "target_type": "workflow_draft",
  "freshness_policy": "latest_revision",
  "safe_summary": "Daily Briefing Mock Smoke must pass for the current draft revision."
}
```

Then validate the workflow draft again. Spec 024 changed this flow: the
workflow publish gate now queries authoritative test-bench evidence for the
current `workflow_draft_id` and `workflow_draft_revision_id`. Do not manually
copy `latest_result_status` or a run id into the workflow document to force
readiness; stale, missing, failing, malformed, wrong-target, or cross-tenant
evidence must block publication.

Codebase used by this step:

- `testing/agent_bench/service.py`
- `testing/agent_bench/sandbox.py`
- `testing/agent_bench/assertions.py`
- `api/routers/admin_agent_tests.py`
- `db/models/agent_tests.py`
- `db/repositories/agent_tests.py`
- `admin/workflow_registry/service.py`
- `admin/workflow_registry/publish_gate.py`
- `admin/workflow_registry/reference_validation.py`

Current-code review: test suites, cases, mock runs, assertion results, redacted
transcripts, token summaries, and DB-backed publish requirement records are
supported. Workflow publish gate evaluation now re-queries DB-backed test-bench
evidence for the current draft revision and summarizes required, passing,
failing, missing, and stale evidence counts.

### Step 11 - Publish The Workflow

In `/admin/workflows/ui`:

1. Open the `daily-intelligence-briefing` draft.
2. Validate the draft after adding the Step 10 test requirement.
3. Open the publish gate.
4. Confirm validation status is passed.
5. Confirm prompt/profile references are ready.
6. Confirm skill references use exact versions and are marked ready.
7. Confirm required test summary is passing.
8. Publish the workflow.
9. Record the published workflow version id.

Codebase used by this step:

- `admin/workflow_registry/service.py`
- `admin/workflow_registry/publish_gate.py`
- `admin/workflow_registry/compiler.py`
- `runtime/workflow_bundle.py`

Current-code review: publication of a validated bundle is supported. The
published bundle is executable by the DB-backed graph worker when a DB runtime
run references it. In this Telegram demo, the channel facade still returns a
deterministic channel result immediately for alias delivery; use the Spec 020
QA tests for direct worker graph-execution evidence.

### Step 12 - Create The Telegram Alias And Link Identity

Create the `Morning briefing` alias for the published workflow version from
Step 11:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/admin/telegram/api/aliases \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "alias_text": "Morning briefing",
    "published_workflow_version_id": "PUBLISHED_WORKFLOW_VERSION_ID",
    "description": "Daily Intelligence Briefing",
    "protected": true,
    "enabled": true
  }'
```

Expected response: `alias_normalized` is `morning briefing`, the alias is
enabled, and no bot token, webhook secret, raw link token, full Telegram user
id, or full chat id appears.

Create a persisted link token through the admin Telegram API:

```bash
curl --fail --silent \
  -X POST "http://127.0.0.1:8000/admin/telegram/api/link-tokens?tenant_id=11111111-1111-1111-1111-111111111111" \
  -H "X-Local-Principal: tenant-admin-acme"
```

Link that token through the local Telegram webhook endpoint:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1001,
    "message": {
      "chat": {"id": 12345},
      "from": {"id": 67890},
      "text": "/link TOKEN_FROM_PREVIOUS_RESPONSE"
    }
  }'
```

Codebase used by this step:

- `api/routers/admin_telegram.py`
- `api/routers/telegram_webhook.py`
- `channels/telegram.py`
- `admin/telegram_config/service.py`
- `db/repositories/telegram_config.py`
- `db/repositories/channels.py`

Current-code review: alias records, link-token audits, identity links, identity
summaries, and update receipts are persisted. The older
`/channels/telegram/link-token` endpoint still exists for legacy local channel
tests, but this scenario should use the admin Telegram endpoint so restart-safe
linking is exercised.

### Step 13 - Start The Scenario Through Telegram

Send the natural-language alias as the linked Telegram identity:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1002,
    "message": {
      "chat": {"id": 12345},
      "from": {"id": 67890},
      "text": "Morning briefing"
    }
  }'
```

Expected response:

```json
{
  "ok": true,
  "messages": ["Daily Intelligence Briefing delivered."],
  "run_id": "<run-id>",
  "alias": "Morning briefing",
  "delivered": true
}
```

Repeat the exact same webhook request with the same `update_id`.

Expected duplicate result: the stored response is replayed, no second run is
created, and no second delivery attempt is recorded.

If you have not injected `MockTelegramBotApiClient` through a test harness, the
running API uses `HttpTelegramBotApiClient`. For a plain `uvicorn` manual run,
provide a real `TELEGRAM_PROVIDER_TOKEN_REF` secret if you expect actual
`sendMessage` delivery. For deterministic local QA without external Telegram
calls, run the QA022 integration test or use a TestClient harness that stores a
`MockTelegramBotApiClient` in `app.state.container.state["telegram_bot_client"]`.

The slash command path remains available:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1003,
    "message": {
      "chat": {"id": 12345},
      "from": {"id": 67890},
      "text": "/run PUBLISHED_WORKFLOW_VERSION_ID Morning briefing"
    }
  }'
```

The `/run` command creates a queued channel run. The natural-language alias path
is the one that formats the deterministic Daily Briefing completion summary and
attempts Telegram delivery in current code.

Codebase used by this step:

- `channels/telegram.py`
- `channels/telegram_delivery.py`
- `channels/service.py`
- `runtime/orchestration/service.py`
- `runtime/briefing_preferences.py`
- `db/repositories/telegram_config.py`
- `db/repositories/channels.py`

Current-code review: plain text `Morning briefing` is supported through the
tenant alias path. Linked identity enforcement, runtime Telegram readiness,
preference resolution, idempotent duplicate update replay, safe result
formatting, and delivery-attempt persistence are implemented. The delivered
message is deterministic local QA output, not a live synthesis from external
Calendar/Gmail/news/weather/commute providers.

### Step 14 - Optional Generic Web API Completion Simulation

The Telegram alias path in Step 13 already completes and delivers deterministic
Daily Briefing output. The Web API channel also has a generic simulation hook
for local QA. It can force a channel run into `completed` state by passing
`_channel_state` in the input payload:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/runs \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "X-Idempotency-Key: daily-briefing-demo-001" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "PUBLISHED_WORKFLOW_VERSION_ID",
    "channel": "web_api",
    "inputs": {
      "text": "Morning briefing",
      "_channel_state": "completed"
    }
  }'
```

Fetch result:

```bash
curl --fail --silent \
  -H "X-Local-Principal: tenant-admin-acme" \
  http://127.0.0.1:8000/runs/RUN_ID/result
```

Codebase used by this step:

- `channels/service.py`
- `api/routers/channel_runs.py`

Current-code review: this proves the generic channel lifecycle, result endpoint,
and artifact metadata path. It does not execute the Daily Briefing workflow
graph or produce live scenario content.

### Step 15 - Inspect Operations, Usage, And Audit Surfaces

After setup and mock runs, inspect:

- `/admin/operations`
- `/admin/usage`
- `/admin/runs`
- `/admin/agent-tests/ui`
- `/admin/telegram`
- `/admin/briefing-preferences`
- `/admin/skill-execution/ui/diagnostics`
- `/admin/workflows/ui`

Codebase used by this step:

- `operations/`
- `usage/`
- `audit/`
- `api/routers/admin_operations.py`
- `api/routers/admin_usage.py`
- `api/routers/admin_run_inspection.py`

Current-code review: these surfaces are implemented for safe operational
visibility. They will show the evidence produced by current deterministic graph
execution tests, mock connector diagnostics, preference resolution, test-bench
runs, Telegram alias delivery, provider probes, and queued or simulated channel
flows.

## Step Review And Implementability Audit

| Step | Can current code implement it | Notes |
| --- | --- | --- |
| 1. Prepare env | Yes | Uses current settings and local-principal mode |
| 2. DB and tenant | Yes | Uses current Compose and Alembic migrations |
| 3. API and worker | Yes for DB graph QA | API runs; worker executes DB-backed graph runs, while channel facade state remains in-memory |
| 4. Telegram config | Yes | Admin config, aliases, persistent link state, runtime readiness checks, update receipts, and delivery attempts exist |
| 5. Model provider | Yes for gateway/probe paths | Credential references resolve live through configured secret providers; graph role nodes do not call providers by default |
| 6. Prompts | Yes | Prompt lifecycle exists |
| 7. Profiles | Yes | Profile lifecycle exists |
| 8. Skills | Yes for mock/local connectors | Registry metadata exists; `SkillExecutionGateway` has mock Daily Briefing adapters and diagnostics, but not live external provider clients |
| 8A. Preferences | Yes | Preference profiles, revisions, safe summaries, export/import, and runtime resolver exist |
| 9. Workflow draft | Yes | Parallel graph can be represented and executed through deterministic DB graph QA |
| 10. Test bench | Yes | Mock test runs work; publish gates query authoritative current evidence |
| 11. Publish | Yes | Published bundle can be executed by DB graph worker; Telegram alias delivery still uses deterministic channel completion |
| 12. Telegram alias/link | Yes | Alias records, link tokens, identity links, and update receipts persist |
| 13. Telegram run | Yes for deterministic alias path | Plain `Morning briefing` triggers and delivers deterministic output; `/run` still creates a queued channel run |
| 14. Completed channel demo | Yes as optional simulation | Uses `_channel_state=completed` for generic channel result QA |
| 15. Operations/audit | Yes | Evidence reflects deterministic graph, connector, preference, test-bench, provider, Telegram, and channel flows |

## Spec 020-025 Status And Remaining Limits

### Spec 020 - Workflow Graph Execution And Parallel Sub-Agent Runtime

Current status:

- `GraphExecutionService` loads published workflow bundle documents from the
  DB runtime repository.
- `OrchestrationWorker.poll_once` now calls the graph executor after claiming a
  run.
- Role and sub-agent nodes execute through the deterministic
  `RoleNodeExecutor` boundary.
- Independent ready role nodes are scheduled together with
  `asyncio.gather`, so the four Daily Briefing scout nodes run in one wave in
  focused QA.
- Join policies cover `all_success`, `quorum`, `first_success`, and
  `manual_resolution`.
- Successful nodes create run steps, checkpoint refs, handoff envelopes,
  side-effect intent evidence for skill boundaries, and safe timeline events.
- Failed joins can pause the run and create durable approval-gate evidence for
  manual resolution.
- Resume tests prove already succeeded steps are not re-executed.
- Cross-tenant bundle execution fails closed.

Remaining limit: this proves graph semantics and deterministic role execution.
It does not yet make each role node resolve an agent profile, execute live
tools, call a model, and synthesize the final sample briefing from live
provider data by default.

Primary QA references:

- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_ui.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/testing-instructions.md`

### Spec 021 - Real Skill Tool Execution Connectors

Current status:

- `SkillExecutionGateway` is implemented as the runtime boundary.
- The Daily Briefing tool set is:
  `google_calendar.events.read`, `gmail.messages.read`, `news.search`,
  `weather.forecast.read`, and `commute.lookup`.
- Mock fixtures return contract-shaped calendar, Gmail, news, weather, and
  commute outputs for local QA.
- Policy checks evaluate installed skill version, allowed tool, outbound
  domains, read-only side-effect behavior, execution mode, credential
  availability, and credential tenant.
- Admin diagnostics are available at
  `/admin/skill-execution/ui/diagnostics`.
- Redaction removes raw email body fields, token-like strings, credential
  values, and sensitive URL query strings from summaries.
- `runtime/skill_tools.py` provides a role-node helper that executes approved
  tool requests through the gateway.

Remaining limit: the adapters are fixture-backed and live-probe shaped. They do
not perform real Google Calendar, Gmail, news, weather, or maps/traffic network
reads in this repository.

Primary QA references:

- `specs/021-real-skill-tool-execution-connectors/qa021.md`
- `specs/021-real-skill-tool-execution-connectors/qa021_ui.md`
- `specs/021-real-skill-tool-execution-connectors/qa021_user_guide.md`

### Spec 022 - Telegram Natural-Language Trigger, Delivery, And Persistence

Current status:

- Tenant admins can create exact normalized aliases such as `Morning briefing`
  on `/admin/telegram`.
- Alias records include published workflow version id, protected/enabled flags,
  revision tokens, and safe metadata.
- Admin-issued link tokens, consumed identity links, identity summaries, and
  update receipts persist in PostgreSQL.
- Protected aliases require a linked active Telegram identity.
- Runtime alias routing enforces tenant Telegram enablement and provider
  readiness before starting a run.
- Duplicate webhook update ids replay the stored safe response without creating
  duplicate runs or delivery attempts.
- Results are formatted through `format_telegram_result` and sent through a
  mockable `TelegramBotApiClient`; real `HttpTelegramBotApiClient` resolves the
  bot token secret at send time.
- Delivery attempts persist destination fingerprint, payload fingerprint,
  status, provider message id, failure category, retry timestamp, and trace id.
- The `Morning briefing` alias resolves briefing preferences and attaches safe
  context to run inputs when a profile exists.

Remaining limit: current alias completion is deterministic and immediate for
local QA. It does not wait on a live external-agent graph result before
formatting the Telegram message.

Primary QA references:

- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022_ui.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/testing-instructions.md`

### Spec 023 - User Briefing Preferences And Context

Current status:

- `/admin/briefing-preferences` supports tenant-scoped Daily Briefing profile
  save/read/update.
- Profiles have immutable revision rows and a current head projection.
- Validated fields include location label, IANA timezone, news topics, VIP
  senders, workday hours, commute mode, calendar/email account references,
  output style, scheduled toggle, and scheduled time.
- Account references reject raw credential-looking values and accept safe
  references such as `delegated:...`, `secret-ref:...`, `account:...`,
  `local:...`, or `none`.
- Admin summaries show safe counts, masked/fingerprinted values, broad location
  labels, schedule status, revision, and digest metadata.
- Users can export/import their own profile JSON; mismatched tenant/principal
  imports fail closed.
- Runtime resolution returns preferences plus safe summary metadata and records
  audit events for resolved, missing, denied, and validation paths.

Remaining limit: scheduled delivery preferences are captured as configuration,
but this test example exercises on-demand Telegram alias triggering rather than
a scheduler that wakes the workflow at the saved time.

Primary QA references:

- `specs/023-user-briefing-preferences-and-context/qa023.md`
- `specs/023-user-briefing-preferences-and-context/qa023_ui.md`
- `specs/023-user-briefing-preferences-and-context/qa023_user_guide.md`

### Spec 024 - Automatic Test Bench Evidence Integration In Workflow Publish Gates

Current status:

- Workflow service publish-gate evaluation builds required test evidence
  requests from the workflow draft's `test_requirements`.
- `AgentTestBenchService.evidence_summary_for_required_suites` queries
  same-tenant test-bench records for the current `workflow_draft_id` and
  current `workflow_draft_revision_id`.
- Passing evidence for older revisions, wrong target ids, wrong target types,
  failing runs, missing suites, malformed suite ids, archived suites, and
  cross-tenant suites blocks publish.
- Publish-gate responses include safe required-test snapshots and required,
  passing, failing, missing, and stale counts.
- Legacy `latest_result_status` fields remain parseable compatibility metadata,
  but they do not make the workflow ready when the workflow service provides
  authoritative evidence snapshots.

Remaining limit: low-level `validate_reference_readiness` still has a
compatibility fallback when it is called without required-test snapshots. The
workflow registry service path used by publish gates passes snapshots and
should be the path used for reviewer validation.

Primary QA references:

- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024.md`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024_ui.md`
- `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/testing-instructions.md`

### Spec 025 - Live Model Credential Resolution For Gateway Calls

Current status:

- Provider connections persist credential secret reference ids only.
- Validation rejects blank references, duplicates, and raw-secret-looking
  values such as `sk-`, bearer tokens, passwords, direct secret assignments, or
  API-key strings.
- `ProviderProbeRunner` resolves the selected reference immediately before
  adapter invocation when a `ProviderSecretResolver` is configured.
- `ModelGateway.invoke` resolves the selected reference immediately before
  runtime adapter invocation when a `ProviderSecretResolver` is configured.
- OpenAI probes and runtime calls fail closed with `secret_reference_invalid`
  when no reference is configured or the reference cannot be resolved.
- Local OpenAI-compatible providers may run without credentials only for
  allowlisted local endpoints; when a reference is configured, the resolved
  credential is passed to the adapter.
- Credential failures record safe provider type, connection id, model id,
  reference id, normalized category, retry/breaker summaries, gateway attempt
  evidence, and usage-safe metadata without raw secret values.
- The application and worker container factories provide secret resolver
  dependencies for probes and gateway calls.

Remaining limit: direct test-only construction of `ModelGateway` or
`ProviderProbeRunner` without a `ProviderSecretResolver` can still use the
legacy explicit `credential` argument. The normal app/container path uses live
secret resolution.

Primary QA references:

- `specs/025-live-model-credential-resolution-for-gateway-calls/qa025.md`
- `specs/025-live-model-credential-resolution-for-gateway-calls/qa025_ui.md`
- `specs/025-live-model-credential-resolution-for-gateway-calls/testing-instructions.md`

## Final Accuracy Review

The current repository can be used to create a detailed administrative showcase
and deterministic QA harness for the Daily Intelligence Briefing. It can
demonstrate tenants, local-principal access, provider records with safe
credential references, prompts, profiles, skill package metadata, mock
connector diagnostics, user briefing preferences, workflow drafts, current
test-bench publish evidence, published bundles, DB graph execution evidence,
Telegram aliases, persistent link state, update receipts, delivery attempts,
and channel results.

The current repository still cannot produce the real sample Telegram briefing
from live Google Calendar, Gmail, news, weather, and commute data. The remaining
gap is now narrower and more precise: the platform has the graph executor,
gateway boundaries, safe credential resolution, preference context, alias
delivery, and mock connector contracts, but the Daily Briefing path does not
yet wire live external tool payloads through agent prompts/models into a final
real-world synthesis. For reviewer QA, treat the sample briefing as the target
product behavior and the current output as deterministic evidence that the
governance, routing, safety, and orchestration scaffolding is in place.
