# Quickstart: Model Routing And Skill Configuration

This quickstart shows how an administrator or reviewer safely changes model
assignments and tool access, previews the result, and verifies runtime
provenance without exposing secrets.

## 1. Start The Local Stack

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Use the existing local-principal development mode for deterministic admin and
tenant identities. Production mode must use Auth0 and role-based
authorization.

## 2. Set A Tenant Global Default Model

Create and activate one tenant-scoped global default LLM:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/model-routing \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {"tenant_id": "TENANT_UUID"},
    "provider_key": "openai",
    "model_id": "gpt-5.4",
    "routing_parameters": {"temperature": 0.2},
    "activate": true,
    "reason": "Set safe tenant default for workflow execution"
  }'
```

Expected result: a new immutable `model_routing` version is created, activated,
and visible in `/admin/config/model-routing`.

## 3. Add Workflow, Agent, Or Step Overrides

Create narrower overrides only where needed:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/model-routing \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "tenant_id": "TENANT_UUID",
      "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
      "agent_key": "researcher",
      "step_key": "summarize_sources"
    },
    "provider_key": "openai",
    "model_id": "gpt-5.4-mini",
    "activate": true,
    "expected_active_version_id": "CURRENT_ACTIVE_VERSION_UUID",
    "reason": "Use lower latency model for summarization step"
  }'
```

Precedence is deterministic:

1. Step override
2. Agent override
3. Workflow override
4. Tenant global default

Prompt references are resolved separately:

1. Step prompt reference
2. Agent prompt reference
3. Workflow prompt reference

There is no tenant-global prompt fallback. A missing prompt blocks
model-backed execution.

## 4. Preview Model Resolution Before Starting A Run

```bash
curl -X POST http://127.0.0.1:8000/admin/config/preview/model \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "TENANT_UUID",
    "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
    "agent_key": "researcher",
    "step_key": "summarize_sources"
  }'
```

Verify the response identifies the resolved model source as `step`, `agent`,
`workflow`, or `tenant_default`, and includes the prompt source as `step`,
`agent`, or `workflow`.

## 5. Bind A Skill And Allow A Tool

Create an exact skill binding:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/skill-bindings \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "tenant_id": "TENANT_UUID",
      "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
      "agent_key": "researcher"
    },
    "skill_slug": "web-research",
    "skill_version": "1.0.0",
    "allowed_contexts": ["runtime_step"],
    "activate": true,
    "reason": "Permit researcher agent to use approved web research skill"
  }'
```

Create a tool allow policy:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/tool-policies \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "tenant_id": "TENANT_UUID",
      "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
      "agent_key": "researcher"
    },
    "skill_slug": "web-research",
    "tool_id": "http.fetch",
    "allowed_action_categories": ["read"],
    "activate": true,
    "reason": "Allow read-only fetches through approved research skill"
  }'
```

Tool access is deny-by-default. Every applicable active policy must allow the
requested tool and action category.

## 6. Add Outbound Domain And Credential Controls

Allow a specific outbound domain pattern:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/outbound-domain-policies \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "tenant_id": "TENANT_UUID",
      "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
      "agent_key": "researcher"
    },
    "tool_id": "http.fetch",
    "action_category": "read",
    "allowed_domain_patterns": ["docs.example.com"],
    "allowed_schemes": ["https"],
    "allowed_ports": [443],
    "activate": true,
    "reason": "Limit research fetches to approved documentation host"
  }'
```

Create credential requirements only with secret references or delegated
credential metadata:

```bash
curl -X POST http://127.0.0.1:8000/admin/config/credential-requirements \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "tenant_id": "TENANT_UUID",
      "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
      "agent_key": "researcher"
    },
    "tool_id": "http.fetch",
    "action_category": "read",
    "credential_kind": "secret_reference",
    "secret_reference_version_id": "SECRET_REFERENCE_VERSION_UUID",
    "allowed_credential_scope": {"host": "docs.example.com"},
    "activate": true,
    "reason": "Require approved API credential for documentation fetches"
  }'
```

Never paste raw secret values into workflow definitions, policy payloads,
prompt text, provenance notes, logs, or audit fields.

## 7. Preview Tool Access

```bash
curl -X POST http://127.0.0.1:8000/admin/config/preview/tool \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "TENANT_UUID",
    "workflow_lineage_id": "WORKFLOW_LINEAGE_UUID",
    "agent_key": "researcher",
    "skill_slug": "web-research",
    "tool_id": "http.fetch",
    "action_category": "read",
    "destination_url": "https://docs.example.com/reference",
    "credential_context": {"host": "docs.example.com"}
  }'
```

Expected allow response: the preview lists the skill binding, tool policy,
outbound policy, secret-reference, and credential requirement versions whose
cumulative intersection allows the request.

Change the URL to `https://unapproved.example.net/` and verify the preview is
denied with `domain_denied` before any outbound access occurs.

## 8. Start A Run And Verify Provenance

Start a workflow run through the existing runtime or channel API. Then inspect
provenance:

```bash
curl http://127.0.0.1:8000/admin/config/runs/WORKFLOW_RUN_UUID/provenance
```

Verify:

- Run-level resolvable versions were pinned at acceptance.
- Model and prompt versions were pinned for each model-backed first use.
- Skill, tool, outbound, secret-reference, and credential decisions show
  evaluated policy versions.
- Denied decisions include safe categories and reasons without secrets.

## 9. Roll Back A Bad Configuration

Rollback reactivates a prior version for future resolution. It does not delete
or mutate history and does not change already pinned run decisions.

```bash
curl -X POST http://127.0.0.1:8000/admin/config/model_routing/BAD_VERSION_UUID/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "target_version_id": "PRIOR_GOOD_VERSION_UUID",
    "expected_active_version_id": "BAD_VERSION_UUID",
    "reason": "Restore prior model after elevated error rate"
  }'
```

Verify the history page shows the rollback record, actor, timestamp, reason,
prior version, and reactivated version.

## 10. Verify Resume Stability

Start a run, let it wait or pause, change active configuration, then resume the
run. The run must continue using versions pinned at acceptance or first use.
Only an explicit audited run migration may change unused pinned configuration
for that run.

## Required Reviewer Commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Reviewer evidence must include deterministic resolver tests, policy
intersection tests, outbound denial tests, credential failure tests,
secret-reference redaction tests, rollback tests, runtime pinning tests, admin
API contract tests, minimal admin web view tests, PR review notes, testing
instructions, and README updates.
