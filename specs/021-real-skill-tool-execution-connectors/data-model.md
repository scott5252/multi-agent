# Data Model: Real Skill Tool Execution Connectors

## SkillToolExecutionRequest

- `tenant_id`: Required tenant identifier.
- `actor_id`: User or service principal requesting execution.
- `workflow_run_id`: Optional workflow run identifier for provenance.
- `role_node_id`: Optional graph role node identifier.
- `skill_package`: Installed package key.
- `skill_version`: Installed immutable package version.
- `tool_name`: Canonical tool identity, such as `google_calendar.events.read`.
- `execution_mode`: `mock` or `live_probe`.
- `operation`: Read-only operation metadata.
- `input`: Contract-specific request payload.
- `required_credential_kind`: Optional delegated credential kind.
- `outbound_domains`: Domains the adapter may contact in live-probe mode.
- `contract_version`: Expected output contract version.
- `policy_refs`: Versioned policy references used by the run.

## SkillToolExecutionResult

- `status`: `succeeded`, `denied`, or `failed`.
- `tool_name`: Canonical tool identity.
- `execution_mode`: Effective mode.
- `output`: Contract-shaped safe result payload.
- `request_summary`: Redacted request summary.
- `response_summary`: Redacted response summary.
- `policy_decisions`: Ordered decisions from all checks.
- `credential_summary`: Redacted credential metadata, if required.
- `artifact_refs`: Optional artifact metadata references for oversized evidence.
- `latency_ms`: Adapter and total gateway latency.
- `error_code`: Optional stable denial/failure code.
- `error_message`: Safe operator-facing message.

## SkillToolAdapter

- `tool_name`: Canonical tool identity.
- `display_name`: Admin-facing label.
- `skill_package`: Expected first-party package key.
- `read_only`: Must be true for this feature.
- `required_credential_kind`: Credential metadata kind or null for public mock fixtures.
- `allowed_domains`: Live-probe outbound domains.
- `fixture_key`: Fixture lookup key for mock mode.
- `execute_mock(input)`: Deterministic fixture execution.
- `execute_live_probe(input, credential_ref)`: Staging-only live probe path.

## CredentialResolutionSummary

- `required`: Boolean.
- `credential_kind`: Delegated credential kind.
- `tenant_id`: Tenant owning the credential metadata.
- `reference`: Redacted secret or delegated credential reference.
- `available`: Boolean.
- `safe_label`: Optional operator label with no secret value.

## ToolPolicyDecision

- `check`: Stable check identifier.
- `allowed`: Boolean.
- `reason`: Safe explanation.
- `policy_ref`: Optional versioned policy reference.

## SkillToolDiagnosticRecord

- `tool_name`: Canonical tool identity.
- `display_name`: Admin-facing label.
- `mode`: Diagnostic execution mode.
- `readiness`: `ready`, `blocked`, or `not_configured`.
- `latest_status`: Last safe mock execution status.
- `latest_summary`: Redacted response summary.
- `latest_denial`: Safe denial reason.
- `requires_credential`: Boolean.
- `allowed_domains`: Redacted domain list.

## Relationships

- A `SkillToolExecutionRequest` evaluates one installed skill package version and one tool.
- A `SkillToolExecutionResult` records zero or more `ToolPolicyDecision` values in evaluation order.
- A `SkillToolAdapter` declares credential and outbound requirements consumed by policy checks.
- A `CredentialResolutionSummary` belongs to a tenant and is never interchangeable across tenants.
- A `SkillToolDiagnosticRecord` is a projection of adapter metadata plus the latest safe gateway result.
