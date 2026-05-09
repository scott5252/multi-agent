# Contract: Prompt Profile Creation And Per-Agent Binding UI

## Existing Prompt Runtime JSON APIs

Spec 071 reuses these protected APIs and generated frontend types:

- `GET /admin/prompt-runtime/api/prompts`
- `POST /admin/prompt-runtime/api/prompts`
- `GET /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft`
- `PUT /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft`
- `POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate`
- `POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview`
- `POST /admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish`

Required browser behavior:

- Create prompt lineages for the active tenant or authorized platform scope.
- Save prompt draft content only inside authorized edit forms.
- Validate prompt variables and fixture sets through backend validation.
- Publish immutable prompt versions.
- Keep raw prompt content out of safe summary surfaces and screenshots.

## Existing Runtime Profile JSON APIs

Spec 071 reuses these protected APIs and generated frontend types:

- `GET /admin/prompt-runtime/api/profiles`
- `POST /admin/prompt-runtime/api/profiles`
- `GET /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft`
- `PUT /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft`
- `POST /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/validate`
- `POST /admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/activate`

Required browser behavior:

- Create profile drafts for workflow roles.
- Bind published prompt versions to profile prompt references.
- Store safe model routing hints and readiness expectations.
- Validate and activate immutable profile versions.
- Keep provider credentials, provider payloads, raw prompts, and raw completions out of safe display surfaces.

## Workflow Builder Lookup Contract

The workflow builder lookups contract must include safe prompt/profile catalog entries or links/actions sufficient for the UI to fetch them.

Minimum safe catalog fields:

```json
{
  "prompt_catalog": [
    {
      "prompt_lineage_id": "uuid",
      "latest_published_prompt_version_id": "uuid-or-null",
      "scope_type": "tenant",
      "tenant_id": "uuid-or-null",
      "display_name": "Support triage prompt",
      "status": "active",
      "validation_status": "passed"
    }
  ],
  "profile_catalog": [
    {
      "agent_runtime_profile_id": "uuid",
      "active_profile_version_id": "uuid-or-null",
      "agent_key": "triage-agent",
      "agent_kind": "agent",
      "display_name": "Triage profile",
      "status": "active",
      "validation_status": "passed"
    }
  ]
}
```

Contract rules:

- Catalogs must be filtered by backend authorization.
- Catalog items must not include raw prompt template content, provider responses, credentials, raw completions, private tool payloads, or unauthorized tenant labels.
- Empty catalogs must be represented as empty lists with creation actions, not synthetic records.

## Workflow Role Binding Contract

Workflow role bindings persist through the Spec 069 save route:

- `POST /admin/app/workflows/drafts/{workflow_draft_id}/save`

Relevant document fields:

```json
{
  "roles": [
    {
      "role_key": "triage-agent",
      "profile_reference_key": "triage-profile",
      "prompt_reference_keys": ["triage-prompt"]
    }
  ],
  "prompt_profile_references": [
    {
      "reference_key": "triage-profile",
      "role_key": "triage-agent",
      "agent_key": "triage-agent",
      "agent_kind": "agent",
      "agent_profile_version_id": "uuid",
      "prompt_version_ids": ["uuid"],
      "source_scope": "tenant",
      "readiness_status": "ready",
      "resolution_digest": "safe-digest"
    }
  ]
}
```

Contract rules:

- `reference_key` values must be unique in `prompt_profile_references`.
- `roles[].profile_reference_key` must point to an existing prompt/profile reference when present.
- `roles[].prompt_reference_keys` must point to existing prompt/profile references when present.
- Backend validation must reject missing, stale, inactive, retired, unauthorized, cross-tenant, or unsafe references.
- Browser helpers may assemble a proposed document, but durable acceptance remains backend-owned.

## Generated Type Requirements

`scripts/frontend/generate_admin_react_types.py` must include prompt runtime and agent profile schemas needed by the React client:

- Prompt lineage create/save/detail/summary/version/preview/validation/publish request types.
- Runtime profile create/save/detail/summary/version/validation/activation request types.
- Any workflow lookup catalog extensions added for prompt/profile binding.

`uv run python scripts/frontend/generate_admin_react_types.py --check` must pass after generated file updates.
