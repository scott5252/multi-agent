# Daily Intelligence Briefing Test Example

Review date: 2026-05-03

This file documents how to set up the "Daily Intelligence Briefing" scenario
from `/Users/scottcornell/Downloads/multi-agent-testbed.md` against the current
`multi-agent-platform` codebase.

## Implementation Verdict

The current product can implement a governed, browser-administered and
mock-tested version of the scenario:

- tenant setup
- local-principal admin login
- model provider records
- prompt library records
- agent and sub-agent runtime profiles
- skill package and tenant installation metadata
- workflow draft authoring with parallel branch and join structure
- test-bench suites and mock-mode test runs
- Telegram link-token flow and `/run` command that creates a queued channel run
- audit, operations, usage, and test evidence views

The current product cannot fully implement the live scenario end to end yet.
Specifically, it cannot currently execute a published workflow graph into real
parallel sub-agent work, call real Google Calendar/Gmail/news/weather/commute
tools through the skill registry, synthesize the final briefing from live tool
results, or send an actual Telegram bot message back to the user from the
runtime command handler.

Use the setup below for a current-code demonstration and QA harness. Use the
missing-feature Spec Kit prompts at the end of this file to close the gaps.

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
- `src/multi_agent_platform/workers/orchestration.py`
- `src/multi_agent_platform/prompts/*`
- `src/multi_agent_platform/agents/*`
- `src/multi_agent_platform/model_providers/*`
- `src/multi_agent_platform/config/*`
- `src/multi_agent_platform/admin/skill_registry/*`
- `src/multi_agent_platform/testing/agent_bench/*`
- `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- `src/multi_agent_platform/db/models/agent_tests.py`
- `specs/015-agent-workflow-test-bench/plan.md`
- `specs/015-agent-workflow-test-bench/spec.md`
- `specs/015-agent-workflow-test-bench/quickstart.md`

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
Good Morning - Monday, May 3

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
| Telegram account linking | Link-token flow exists; token and identity state are in memory, with admin audit summaries persisted | `channels/service.py`, `channels/telegram.py`, `admin/telegram_config/service.py` | Yes for local/staging demos |
| Telegram trigger | Runtime command parser supports `/run <workflow_id> [text]`; it does not support plain `Morning briefing` | `channels/telegram.py` | Partially |
| Telegram bot reply | Webhook returns JSON test responses; it does not call Telegram `sendMessage` | `api/routers/telegram_webhook.py` | No |
| Workflow authoring | Browser/API workflow draft model supports roles, subagent roles, nodes, edges, joins, contracts, skills, test requirements | `api/schemas/workflow_registry.py` | Yes |
| Parallel sub-agent execution | Graph shape can be authored; current worker only claims runnable work and records a claim event | `workers/orchestration.py` | No |
| Runtime model calls | `ModelGateway` supports OpenAI and local OpenAI-compatible chat completions | `model_providers/gateway.py` | Partially |
| Prompt/profile setup | Prompt and agent runtime profile services exist | `prompts/`, `agents/` | Yes |
| Skill registry | Skill manifests, tenant grants, installs, credentials, smoke/readiness metadata exist; admin service is in-memory | `admin/skill_registry/` | Yes for metadata demos |
| Real Calendar/Gmail/news/weather/traffic tools | No concrete runtime adapters for these tools exist in the product code | no tool adapter package exists | No |
| Test bench | Durable suite/case/run tables and mock sandbox execution exist | `testing/agent_bench/`, `db/models/agent_tests.py` | Yes |
| Publish gate test evidence | Agent test API can evaluate DB evidence, but workflow publish validation reads `document.test_requirements.latest_result_status` rather than querying the test bench service | `admin/workflow_registry/reference_validation.py`, `api/routers/admin_agent_tests.py` | Partially |
| User preferences | Immutable memory exists, but there is no first-class briefing preference profile for location, topics, VIPs, commute mode, or calendar/email account choices | `memory/` | Partially |

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
LOCAL_PRINCIPAL_CATALOG_JSON={"platform-admin":{"catalog_key":"platform-admin","display_name":"Platform Admin","role_codes":["platform_admin"],"permission_codes":["tenant:admin","admin:role-grants:write","admin:support-overrides:write","admin:support-overrides:approve"]},"tenant-admin-acme":{"catalog_key":"tenant-admin-acme","display_name":"Acme Tenant Admin","tenant_id":"11111111-1111-1111-1111-111111111111","org_id":"org-acme","role_codes":["tenant_user","tenant_admin"],"permission_codes":["tenant:read","tenant:admin"]}}
```

If you are using a real Telegram bot for webhook testing, also provide the
environment secret used by your deployment convention:

```bash
SECRET_PROVIDER=env
ENV_SECRET_PREFIX=MAP_SECRET_
MAP_SECRET_TELEGRAM_BOT_TOKEN=<telegram-bot-token-from-botfather>
```

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

Current-code review: API startup is fully supported. The worker currently
claims DB-backed orchestration work but does not interpret and execute a
workflow graph into agent/sub-agent steps.

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
4. Issue a link token for the Acme user.
5. Send `/link TOKEN_FROM_PLATFORM` through Telegram or through the local
   webhook API shown in Step 12.

Codebase used by this step:

- `api/routers/admin_telegram.py`
- `admin/telegram_config/service.py`
- `db/models/telegram_config.py`
- `channels/service.py`

Current-code review: Telegram configuration, link token audit, identity summary,
and local webhook command parsing are supported. The runtime Telegram command
handler does not currently enforce the persisted tenant Telegram config before
handling commands, and it does not send real Telegram Bot API messages.

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
credential references, not raw keys.

Codebase used by this step:

- `model_providers/service.py`
- `model_providers/gateway.py`
- `model_providers/openai_adapter.py`
- `model_providers/local_adapter.py`
- `api/routers/admin_model_providers.py`

Current-code review: provider records and gateway calls are supported.
Provider tests currently pass `credential=None`, so live OpenAI probes require
additional credential-resolution wiring before relying on them for production.

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
| `calendar-reader` | `calendar.events.read` | `tool:google-calendar:v1` | `read` | delegated credential |
| `gmail-reader` | `gmail.messages.read` | `tool:gmail:v1` | `read` | delegated credential |
| `web-news-search` | `web.news.search` | `tool:web-search:v1` | `search` | secret reference or none |
| `weather-fetcher` | `weather.forecast.read` | `tool:weather:v1` | `read` | secret reference or none |
| `commute-checker` | `maps.commute.read` | `tool:maps-traffic:v1` | `read` | secret reference |

Use this manifest pattern for each package, replacing the bracketed values:

```json
{
  "schema_version": "1.0",
  "slug": "calendar-reader",
  "semantic_version": "1.0.0",
  "description": "Read-only calendar event lookup for daily briefing workflows.",
  "entrypoint": {
    "type": "approved_tool_ref",
    "approved_integration_ref": "tool:google-calendar:v1"
  },
  "tools": [
    {
      "tool_id": "calendar.events.read",
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
      "tool_id": "calendar.events.read",
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
      "credential_kind": "delegated_credential",
      "tool_id": "calendar.events.read",
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
      "tool_id": "calendar.events.read",
      "action_category": "read",
      "side_effect_level": "read_only",
      "required": true,
      "safe_description": "Read calendar events."
    }
  ],
  "test_fixtures": [
    {
      "fixture_key": "calendar-read-policy-preview",
      "tool_id": "calendar.events.read",
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

Current-code review: package, validation, publication, grant, installation,
credential readiness, smoke readiness, and binding eligibility metadata are
supported. The admin skill registry service is process-local in memory, so the
state is lost when the API process restarts unless the service is replaced with
a persistent implementation. The product also does not currently include real
runtime adapters for Google Calendar, Gmail, web search, weather, or commute
tools.

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
      "skill_installation_keys": ["calendar-reader-install"],
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
      "skill_installation_keys": ["gmail-reader-install"],
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
      "skill_installation_keys": ["web-news-search-install"],
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
      "skill_installation_keys": ["weather-fetcher-install", "commute-checker-install"],
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
    {"skill_installation_key": "calendar-reader-install", "skill_slug": "calendar-reader", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "gmail-reader-install", "skill_slug": "gmail-reader", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "web-news-search-install", "skill_slug": "web-news-search", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "weather-fetcher-install", "skill_slug": "weather-fetcher", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"},
    {"skill_installation_key": "commute-checker-install", "skill_slug": "commute-checker", "skill_version": "1.0.0", "tenant_id": "11111111-1111-1111-1111-111111111111", "credential_requirement_status": "ready"}
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

Current-code review: authoring and validation of this graph structure are
supported. Execution of this graph as real parallel sub-agent work is not yet
implemented.

### Step 10 - Create Test Bench Evidence

Open:

```text
http://127.0.0.1:8000/admin/agent-tests/ui
```

Create a suite:

- Name: `Daily Briefing Mock Smoke`
- Tenant: Acme
- Target type: `workflow_draft`
- Target id: `daily-intelligence-briefing`
- Target version: use the current draft revision id or a stable label such as
  `draft-rev-1`
- Default safe mode: `mock_model`
- Model mode: `mock`
- Tool mode: `mock`
- Pass threshold: `1.0`
- Required for publish: enabled

Add at least one case:

```json
{
  "request": "Morning briefing",
  "date": "2026-05-03",
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

Run the suite in `mock_model` mode and capture the run id.

Important: the current workflow publish gate reads required test status from
the workflow draft document's `test_requirements` list. The separate test-bench
API can evaluate DB evidence, but workflow publication does not automatically
query it. After the mock run passes, update the workflow draft's
`test_requirements` to include the passing suite/run:

```json
{
  "requirement_key": "daily-briefing-smoke",
  "suite_id": "<agent_test_suite_id>",
  "target_type": "workflow_draft",
  "freshness_policy": "latest_revision",
  "latest_result_id": "<agent_test_run_id>",
  "latest_result_status": "passed",
  "safe_summary": "Daily Briefing Mock Smoke passed in mock_model mode."
}
```

Then validate the workflow draft again.

Codebase used by this step:

- `testing/agent_bench/service.py`
- `testing/agent_bench/sandbox.py`
- `testing/agent_bench/assertions.py`
- `api/routers/admin_agent_tests.py`
- `db/models/agent_tests.py`
- `admin/workflow_registry/reference_validation.py`

Current-code review: test suites, cases, mock runs, assertion results, redacted
transcripts, token summaries, and DB-backed publish requirement records are
supported. Automatic synchronization between test-bench evidence and workflow
publish-gate evidence is missing.

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
published bundle is metadata and a run blueprint; current workers do not yet
execute the graph nodes.

### Step 12 - Link Telegram Identity Through Current Webhook Handler

Create a link token through the channel API:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/link-token \
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

- `api/routers/channel_runs.py`
- `api/routers/telegram_webhook.py`
- `channels/service.py`
- `channels/telegram.py`

Current-code review: this step is supported while the API process remains
running. Link tokens and runtime Telegram identity links are in-memory in the
channel service and are lost on API restart.

### Step 13 - Start The Scenario Through Telegram

Current Telegram command syntax requires `/run`, not the plain text
`Morning briefing`. Use the published workflow version id from Step 11:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1002,
    "message": {
      "chat": {"id": 12345},
      "from": {"id": 67890},
      "text": "/run PUBLISHED_WORKFLOW_VERSION_ID Morning briefing"
    }
  }'
```

The response includes a `run_id`. Check status:

```bash
curl --fail --silent \
  -X POST http://127.0.0.1:8000/channels/telegram/webhook/local-dev-secret \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 1003,
    "message": {
      "chat": {"id": 12345},
      "from": {"id": 67890},
      "text": "/status RUN_ID"
    }
  }'
```

Expected current-code result: the run is accepted and remains `queued` unless
the channel run is manually simulated or a future graph execution worker is
implemented.

Codebase used by this step:

- `channels/telegram.py`
- `channels/service.py`
- `runtime/orchestration/service.py`

Current-code review: accepting a Telegram `/run` command is supported. Plain
text `Morning briefing` and end-to-end completion are not supported.

### Step 14 - Demonstrate A Completed Channel Result With Current Code

The Web API channel has a current-code simulation hook for local QA. It can
force a channel run into `completed` state by passing `_channel_state` in the
input payload:

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

Current-code review: this proves the channel lifecycle, result endpoint, and
artifact metadata path. It does not execute the daily briefing workflow graph
or produce the scenario's real briefing content.

### Step 15 - Inspect Operations, Usage, And Audit Surfaces

After setup and mock runs, inspect:

- `/admin/operations`
- `/admin/usage`
- `/admin/runs`
- `/admin/agent-tests/ui`
- `/admin/telegram`
- `/admin/workflows/ui`

Codebase used by this step:

- `operations/`
- `usage/`
- `audit/`
- `api/routers/admin_operations.py`
- `api/routers/admin_usage.py`
- `api/routers/admin_run_inspection.py`

Current-code review: these surfaces are implemented for safe operational
visibility. They will show only the evidence produced by the current mocked and
queued flows.

## Step Review And Implementability Audit

| Step | Can current code implement it | Notes |
| --- | --- | --- |
| 1. Prepare env | Yes | Uses current settings and local-principal mode |
| 2. DB and tenant | Yes | Uses current Compose and Alembic migrations |
| 3. API and worker | Partially | API runs; worker does not execute workflow graph nodes |
| 4. Telegram config | Partially | Admin config exists; command handler does not enforce config or send Telegram API messages |
| 5. Model provider | Partially | Gateway exists; live credential resolution must be verified for real OpenAI calls |
| 6. Prompts | Yes | Prompt lifecycle exists |
| 7. Profiles | Yes | Profile lifecycle exists |
| 8. Skills | Partially | Registry metadata exists; real tool adapters and persistent admin service are missing |
| 9. Workflow draft | Yes for authoring | Parallel graph can be represented but not executed |
| 10. Test bench | Partially | Mock test runs work; publish gate sync is manual |
| 11. Publish | Yes for metadata bundle | Published bundle will not execute live graph |
| 12. Telegram link | Partially | Works in memory for the current API process |
| 13. Telegram run | Partially | `/run` creates queued run; plain text trigger and completion missing |
| 14. Completed channel demo | Yes as simulation | Uses `_channel_state=completed`, not real scenario logic |
| 15. Operations/audit | Yes | Evidence reflects current flows only |

## Missing Features Blocking Full Scenario

### Missing Feature 1 - Workflow Graph Execution And Parallel Sub-Agent Runtime

Why it blocks the scenario:

The workflow builder can represent parallel branches and joins, but the current
runtime worker only claims a runnable workflow run and records a claim event. It
does not interpret published workflow nodes, invoke agent profiles, fan out
sub-agent work, wait on joins, handle partial branch failure, or synthesize the
final output.

Current code evidence:

- `WorkflowDraftDocument` supports roles, subagent roles, nodes, edges, and
  joins.
- `compile_workflow_blueprint` stores graph metadata and dependencies.
- `RuntimeOrchestrationService.start_run` creates a runnable run from a cloned
  execution bundle.
- `OrchestrationWorker.poll_once` claims a run and records a timeline event,
  but no graph executor follows.

Spec Kit prompt breakdown:

```text
/speckit.specify Add workflow graph execution for published workflow bundles. The runtime worker must load the published bundle document, execute role nodes in dependency order, fan out independent branches in parallel, apply join policies such as all_success, quorum, first_success, and manual_resolution, invoke agent and sub-agent runtime profiles through the existing ModelGateway and policy services, persist per-node run steps, checkpoints, handoffs, side-effect intents, approvals, timeline events, partial failure summaries, and final structured outputs. The first flagship scenario is the Daily Intelligence Briefing workflow: Telegram starts one orchestrator run, four scout sub-agents run in parallel, their outputs join, a focus recommender runs after the join, and a synthesis node produces a final briefing. Cross-tenant access must fail closed, execution must be idempotent on resume, and no raw secrets or raw tool payloads may be rendered.

/speckit.plan Plan this using the existing FastAPI app, SQLAlchemy async repositories, runtime orchestration models, workflow registry compiled bundles, ModelGateway, model-skill config resolver, immutable memory service, side-effect intent model, audit/debugging capture, reliability leases, and worker loop. Add a graph execution service under runtime/orchestration, extend workers/orchestration.py to execute claimed runs, define node state transitions, parallel branch scheduling, join evaluation, retry/resume semantics, safe output storage, and timeline/audit evidence. Reuse existing runtime_run_steps, checkpoints, handoff envelopes, side-effect intents, approval gates, and usage capture. Include unit, integration, crash-resume, tenant isolation, and performance tests.

/speckit.tasks Break implementation into TDD tasks for graph executor contracts, bundle loading, node scheduling, role-node execution, sub-agent invocation, parallel branch fan-out, join policy evaluation, failure handling, final output persistence, checkpoint/resume behavior, audit/timeline evidence, worker integration, channel result propagation, and QA docs. Include tests for the Daily Intelligence Briefing graph with four parallel scout nodes and one downstream focus/synthesis path.
```

### Missing Feature 2 - Real Skill Tool Execution Connectors

Why it blocks the scenario:

The skill registry stores manifests, readiness, credentials, and eligibility
metadata, but the product does not contain runtime tool adapters for Google
Calendar, Gmail, web/news search, weather, maps/traffic, summarization tools,
or connector execution behind skill bindings.

Current code evidence:

- `admin/skill_registry/*` validates manifests and readiness.
- `runtime/skill_registry.py` evaluates installed skill evidence.
- `config/model_skill.py` and `config/policy.py` evaluate skill/tool policy.
- No product module executes `calendar.events.read`, `gmail.messages.read`,
  `web.news.search`, `weather.forecast.read`, or `maps.commute.read`.

Spec Kit prompt breakdown:

```text
/speckit.specify Add a governed runtime tool execution layer and first-party read-only skill adapters for the Daily Intelligence Briefing scenario. The platform must execute approved skill tools for Google Calendar event reads, Gmail message reads, web/news search, weather forecast lookup, and commute or traffic lookup through installed skill versions. Tool calls must resolve only delegated credential or secret-reference metadata, enforce model-skill tool policy and outbound policy, block unsafe side effects by default, store redacted request/response summaries, and return structured outputs matching workflow contracts. The feature must support mock fixtures for local QA and approved live probes for staging.

/speckit.plan Plan adapters using existing skill registry manifests, model-skill config policies, delegated credential metadata, secret providers, outbound policy models, side-effect intents, audit/redaction helpers, reliability retry/breaker controls, and artifact storage. Define a ToolGateway or SkillExecutionGateway boundary, typed tool request/response contracts, credential resolution interfaces, mock/live execution modes, fixture support, timeout/retry behavior, and safe observability. Include specific adapter contracts for calendar, gmail, news search, weather, and commute tools without storing raw external payloads inline.

/speckit.tasks Create TDD tasks for tool execution contracts, policy enforcement, credential resolution, outbound allowlist checks, mock adapter fixtures, live adapter interfaces, redaction, artifact references, runtime integration from graph role nodes, skill smoke-test integration, admin diagnostics, and docs. Add tests for each Daily Briefing skill, denied credential cases, blocked outbound domains, tenant isolation, and no raw secret leakage.
```

### Missing Feature 3 - Telegram Natural-Language Trigger, Delivery, And Persistence

Why it blocks the scenario:

The attached scenario starts from the plain message `Morning briefing` and ends
with a Telegram reply. The current handler requires slash commands such as
`/run <workflow_id> [text]`, stores link/runtime state in memory, and returns
test JSON rather than sending a Telegram Bot API message.

Current code evidence:

- `TelegramCommandHandler._dispatch` supports `/start`, `/link`, `/run`,
  `/status`, `/approve`, `/reject`, `/resume`, `/cancel`, `/result`,
  `/artifacts`, `/subscribe`, `/watch`, and `/unwatch`.
- Unknown plain text raises a missing-input channel error.
- `ChannelService` stores runs, link tokens, Telegram links, updates, and rate
  windows in in-memory dictionaries.
- `TelegramConfigurationService` persists safe admin config and audits, but the
  runtime command handler does not enforce tenant Telegram enablement or command
  policy before handling commands.

Spec Kit prompt breakdown:

```text
/speckit.specify Add production Telegram command delivery for tenant workflows. Tenants must be able to configure aliases such as "Morning briefing" or "/briefing" that map to a published workflow version, require linked identities for protected aliases, enforce tenant Telegram configuration at runtime, persist Telegram link tokens and identity links in PostgreSQL, and send final run results back through the Telegram Bot API using safe secret references. The Daily Intelligence Briefing alias must start the published workflow when a linked user sends "Morning briefing" and must deliver the final briefing or partial-failure note to the same chat.

/speckit.plan Plan this using existing Telegram admin config tables, channel models, ChannelService contracts, FastAPI webhook route, secret provider abstractions, notification subscriptions, audit/redaction helpers, idempotency records, and operations diagnostics. Add persistent repositories for channel runtime link tokens and Telegram identity links, alias configuration models, Bot API client boundary, delivery attempts, retry/backoff, command policy enforcement, and safe diagnostics. Keep local QA fully deterministic with a mocked Bot API client.

/speckit.tasks Break into tasks for persistent link tokens, persistent identity links, command alias CRUD, runtime config enforcement, natural-language command routing, Bot API sendMessage client, delivery attempt records, notification integration, result formatting, idempotent Telegram update handling, revocation, rate limits, tenant isolation, tests, browser QA, and docs.
```

### Missing Feature 4 - User Briefing Preferences And Context

Why it blocks the scenario:

The scenario depends on user-specific topics, location, VIP contacts, commute
mode, calendar account, email account, and preferred briefing time. The current
platform has immutable memory primitives, tenant/auth context, and prompt/profile
configuration, but no first-class daily briefing preference UI/API or runtime
resolver.

Current code evidence:

- `memory/` supports immutable memory scopes and runtime-safe reads/writes.
- Channel actors carry tenant and platform identity.
- No dedicated user preference service exists for briefing topics, VIP senders,
  location, commute profile, or connected account selection.

Spec Kit prompt breakdown:

```text
/speckit.specify Add tenant-scoped user briefing preferences for recurring and on-demand Daily Intelligence Briefing workflows. Linked users must be able to define location, timezone, news topics, VIP senders, workday hours, commute mode, default calendar/email account references, output style, and optional scheduled briefing time. Admins must inspect safe summaries only. Runtime workflows must resolve preferences by tenant and principal id and pass them to the orchestrator without exposing raw credentials or private data in logs.

/speckit.plan Plan this using existing auth principal context, tenancy guards, immutable memory policy, PostgreSQL repositories, admin shell, audit/redaction helpers, and channel runtime inputs. Define preference models, APIs, server-rendered UI, validation rules, memory or table ownership decision, safe summaries, import/export behavior, and runtime resolver hooks. Include migration and tenant isolation tests.

/speckit.tasks Create tasks for preference data model, migration, repository, service, API schemas, admin/user UI forms, validation, runtime resolution dependency, audit events, redaction tests, tenant isolation tests, docs, and Daily Briefing QA fixtures.
```

### Missing Feature 5 - Automatic Test Bench Evidence Integration In Workflow Publish Gates

Why it blocks the scenario:

The test bench can persist passing suite runs, and the workflow document can
list required tests, but publish validation currently trusts the
`latest_result_status` embedded in the workflow draft document. It does not
automatically query `AgentTestBenchService.evidence_summary`.

Current code evidence:

- `AgentTestBenchService.evidence_summary` evaluates DB-backed publication
  requirements and latest passing runs.
- `evaluate_agent_test_publish_gate` exposes that through
  `/admin/agent-tests/publish-gates/evaluate`.
- `validate_reference_readiness` summarizes required tests from
  `document.test_requirements.latest_result_status`.

Spec Kit prompt breakdown:

```text
/speckit.specify Wire agent workflow test-bench evidence directly into workflow publish gates. When a workflow draft declares required test suites, validation and publication must query the test-bench repository for current passing evidence tied to the candidate draft revision or published target version. Admins must no longer manually copy latest_result_status into the workflow document. Stale, missing, failing, or cross-tenant test evidence must block publication with safe diagnostics.

/speckit.plan Plan this using AgentTestBenchService, AgentTestRepository, workflow registry validation, workflow publish gate evaluation, existing required test document fields, audit/debugging capture, and admin workflow UI. Define target-version matching, freshness policies, current revision binding, stale evidence detection, safe summary projection, and migration behavior for existing documents.

/speckit.tasks Create tasks for repository query integration, workflow validation service changes, publish gate response changes, UI required-test selectors, stale evidence tests, cross-tenant denial tests, migration/backfill docs, and browser QA.
```

### Missing Feature 6 - Live Model Credential Resolution For Gateway Calls

Why it may block production:

The gateway can call OpenAI and local OpenAI-compatible providers, but current
provider probes pass `credential=None`, and the user guide already warns that
deployments must verify credential resolution before live OpenAI runtime calls.

Current code evidence:

- `ProviderSecretResolver` exists.
- `ModelGateway.invoke` accepts a `credential` argument.
- `ModelProviderService.test_connection` calls `run_probe(... credential=None)`.

Spec Kit prompt breakdown:

```text
/speckit.specify Complete live model provider credential resolution for provider probes and runtime gateway calls. Provider connections must store safe secret reference ids, resolve them through the configured secret provider only at call time, never expose raw values, and pass resolved credentials into OpenAI or local OpenAI-compatible adapters. Failed or missing credentials must produce safe diagnostics and audit evidence.

/speckit.plan Plan this using ProviderSecretResolver, secret provider abstractions, ModelProviderService, ModelGateway, provider probes, bootstrap container factories, audit/redaction helpers, and operations diagnostics. Define credential selection when multiple references exist, production guardrails, probe behavior, runtime behavior, and test-mode mocks.

/speckit.tasks Add tests and implementation for resolving provider credentials in probe and gateway paths, secret-resolution failures, audit-safe summaries, no raw secret rendering, local/no-auth provider behavior, operations diagnostics, and docs.
```

## Final Accuracy Review

The current repository can be used to create an administrative showcase and a
mock QA harness for the Daily Intelligence Briefing. It can demonstrate how the
scenario would be represented in tenants, prompts, profiles, skill packages,
workflow drafts, test suites, Telegram link tokens, and channel runs.

The current repository cannot yet produce the real sample Telegram briefing from
live calendar, email, news, weather, and commute data. The blocking gaps are not
configuration mistakes; they are missing product features documented above.
