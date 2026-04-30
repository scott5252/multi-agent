# Contract: Skill Manifest Schema

Skill manifests are declarative JSON documents. A published package version
pins the canonical manifest JSON digest. The canonical digest is computed from
UTF-8 JSON with sorted keys, no insignificant whitespace, and no omitted
required fields.

## Required Top-Level Shape

```json
{
  "schema_version": "1.0",
  "slug": "calendar-assistant",
  "semantic_version": "1.2.3",
  "description": "Safe operator-facing description.",
  "entrypoint": {
    "type": "approved_tool_ref",
    "approved_integration_ref": "tool:calendar:v1"
  },
  "tools": [],
  "action_categories": [],
  "network_requirements": [],
  "credential_requirements": [],
  "runtime_permissions": [],
  "test_fixtures": [],
  "compatibility": {},
  "safe_documentation": {}
}
```

## Entrypoint

Allowed:

- `approved_tool_ref`: references an existing platform-approved tool
  integration.
- `approved_mcp_ref`: references an existing platform-approved MCP
  integration.

Rejected:

- Python, shell, container, wasm, or other executable package code.
- Standalone external HTTP service endpoints.
- Inline MCP server definitions.
- Dynamic tool discovery from package-provided code.
- Embedded raw secrets, tokens, credentials, or tenant data.

## Tool Declarations

Each item in `tools` declares:

- `tool_id`: stable id unique within the manifest.
- `approved_integration_ref`: approved integration id.
- `display_name` and `description`: safe admin-facing text.
- `action_categories`: recognized categories from Spec 007 policy vocabulary.
- `input_contract_ref` and `output_contract_ref`: optional safe schema refs.
- `side_effect_profile`: one of `read_only`, `idempotent_write`,
  `non_idempotent_write`, or `external_notification`.
- `safe_usage`: short safe guidance with no secret or unsafe payload content.

Validation requires every declared tool to map to the approved integration and
every action category to be allowed by platform vocabulary.

## Network Requirements

Each item declares:

- `tool_id`
- `action_category`
- `allowed_schemes`
- `allowed_domain_patterns`
- `allowed_ports`
- `required`
- `safe_description`

Domains are lowercased and IDNA-normalized before validation. Embedded
credentials, IP literals unless explicitly allowed by platform policy,
ambiguous wildcards, missing schemes, and undeclared destinations are blocking
findings.

## Credential Requirements

Each item declares:

- `requirement_key`
- `credential_kind`: `secret_reference` or `delegated_credential`
- `tool_id`
- `action_category`
- `required`
- `allowed_secret_reference_scopes`
- `delegated_credential_scopes`
- `rotation_policy`
- `safe_description`

Raw secret values, example tokens, passwords, API keys, OAuth refresh tokens,
and package-provided credential material are forbidden. Tenant installations
must satisfy requirements with existing approved secret references or delegated
credential links.

## Runtime Permissions

Each item declares:

- `permission_key`
- `permission_type`: `tool_access`, `network_access`, `credential_access`, or
  `tenant_data_access`
- `tool_id`
- `action_category`
- `data_scope`
- `side_effect_level`
- `required`
- `safe_description`

Runtime permissions must be satisfiable by existing Spec 007 allowed tool
policies, outbound domain policies, and credential requirement policies.

## Test Fixtures

Each item declares:

- `fixture_key`
- `tool_id`
- `action_category`
- `fixture_kind`: `static_input`, `policy_preview`, or `safe_probe`
- `safe_input_summary`
- `fixture_artifact_ref`
- `fixture_digest`
- `requires_credentials`
- `expected_outcome`
- `timeout_seconds`

Fixtures must be classified safe. Raw tenant data, raw secrets, credential
values, provider tokens, unsafe docs, and undeclared network calls are
blocking findings.

## Compatibility Metadata

Compatibility may include:

- `platform_min_version`
- `platform_max_version`
- `required_capabilities`
- `approved_integration_versions`
- `policy_vocabulary_version`
- `workflow_role_constraints`
- `agent_profile_constraints`
- `deprecation`

Validation blocks packages whose compatibility metadata cannot be satisfied by
the platform or by tenant policy at install/binding time.

## Safe Documentation

Safe docs declare:

- `summary`
- `artifact_ref`
- `documentation_digest`
- `redaction_classification`
- `support_contacts`
- `operator_notes`

Documentation is displayed only after validation marks it safe. Later
classification changes can restrict display without mutating the immutable
package version.

## Publication Validation Rules

Publication is blocked when:

- Required manifest fields are missing or malformed.
- Slug or semantic version does not match the package/version request.
- The semantic version already exists for the package slug.
- Entrypoint type is not `approved_tool_ref` or `approved_mcp_ref`.
- Approved integration references are missing, retired, unknown, or not
  platform-approved.
- Tool ids or action categories are unknown or duplicate.
- Network requirements include undeclared or disallowed destinations.
- Runtime permissions cannot be expressed through existing policies.
- Credential requirements include raw values or cannot be satisfied by
  approved secret/delegated credential mechanisms.
- Fixtures or documentation include unsafe content.
- Artifact, manifest, documentation, or fixture digests do not match pinned
  content.
