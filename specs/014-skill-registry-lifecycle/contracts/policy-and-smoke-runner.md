# Contract: Policy Integration And Smoke Test Runner

## Runner Purpose

The smoke-test runner verifies that a tenant installation can use the
package-declared approved tool/MCP references, safe fixtures, required
credential references, and network/runtime permissions under the same policy
rules that will govern runtime use.

The runner is not a full behavior certification system. It produces readiness
evidence for declared safe fixtures and required policy checks.

## Runner Input

```json
{
  "test_run_id": "uuid",
  "tenant_id": "uuid",
  "installation_id": "uuid",
  "installation_version": 2,
  "package": {
    "slug": "calendar-assistant",
    "semantic_version": "1.2.3",
    "manifest_digest": "sha256:...",
    "artifact_digest": "sha256:..."
  },
  "fixtures": [
    {
      "fixture_key": "list-calendars",
      "tool_id": "calendar.list",
      "action_category": "read",
      "fixture_digest": "sha256:...",
      "timeout_seconds": 10
    }
  ],
  "credential_readiness": [],
  "policy_context": {
    "workflow_lineage_id": null,
    "agent_key": null,
    "step_key": null
  },
  "idempotency_key": "tenant-installation-run-key",
  "trace_id": "trace-id"
}
```

## Runner Output

```json
{
  "test_run_id": "uuid",
  "tenant_id": "uuid",
  "installation_id": "uuid",
  "outcome": "passed",
  "fixture_results": [
    {
      "fixture_key": "list-calendars",
      "outcome": "passed",
      "policy_decision_summary": {
        "tool": "allow",
        "outbound_domain": "allow",
        "credential": "allow"
      },
      "safe_output_summary": {
        "message": "Probe completed without storing response content."
      }
    }
  ],
  "failure_reasons": [],
  "evidence_artifact_id": null,
  "duration_ms": 1200,
  "trace_id": "trace-id"
}
```

## Isolation Rules

- Runner jobs are tenant-scoped and accepted through existing reliability
  admission controls.
- Runner jobs receive only safe fixture inputs, manifest summaries, approved
  integration refs, secret-reference/delegated-credential metadata, and
  policy context.
- Raw secret values are resolved only through existing runtime secret
  providers when the underlying approved integration requires them and are
  never persisted in runner input, output, logs, metrics, audit records, or
  evidence artifacts.
- Undeclared network access, undeclared tools, cross-tenant data access, and
  persistent side effects outside the declared fixture scope are denied.
- Retryable infrastructure failures may be retried under existing retry
  budget policy. Non-repeatable side-effect fixtures are skipped unless
  explicitly marked idempotent and allowed by policy.

## Spec 007 Binding Eligibility

The registry exposes an eligibility adapter that returns allow/deny evidence
for a tenant installation. Eligibility requires:

- Installation readiness is `ready`.
- Package version and tenant installation are not quarantined or runtime
  blocked.
- Tenant still has authorization to use the installed package version.
- Manifest-declared tools map to approved tool/MCP integrations.
- Manifest action categories match Spec 007 allowed tool policy vocabulary.
- Required outbound domains are allowed by active outbound domain policies for
  the binding scope.
- Required credentials are satisfied by active secret reference versions or
  delegated credential links in the tenant scope.
- Compatibility metadata permits the selected agent profile, workflow role,
  and platform capability set.

Spec 007 remains authoritative for creating `SkillBindingVersion` records and
runtime `RuntimePolicyDecision` outcomes. The registry supplies exact
installation evidence and denial reasons.

## Workflow Publish Validation

Workflow publish validation must call the eligibility adapter for every
installed skill referenced by workflow roles or agent profiles.

Publish is blocked when any installed skill reference is:

- Missing or invisible to the workflow tenant.
- Not `ready`.
- Stale compared with the supplied installation version or manifest digest.
- Quarantined or runtime blocked.
- Withdrawn in a way that policy blocks future runtime use.
- Incompatible with the workflow role, agent profile, or required action
  categories.
- Missing required credential readiness, smoke-test evidence, allowed tool
  policy, outbound domain policy, or credential requirement policy.

On success, the published workflow bundle pins installation id, installation
version, package slug, semantic version, manifest digest, package artifact
digest, and matched policy version ids.

## Upgrade And Rollback Semantics

- Upgrade creates a new tenant installation version and links
  `previous_installation_id`.
- Existing Spec 007 skill bindings remain pinned to the original installation.
- Runtime runs continue to use their pinned execution bundle.
- Rollback is explicit: an admin creates or reactivates a binding to a prior
  eligible installation version or republishes a workflow referencing that
  prior installation.
- Quarantined prior installations cannot be rollback targets until resolved.

## Reliability Controls

- Validation and smoke-test jobs use idempotency keys.
- Artifact I/O uses existing artifact throughput limits and records safe
  failure summaries.
- Retry schedules are used for retryable object storage, approved integration,
  or runner infrastructure failures.
- Circuit breakers protect unhealthy approved tool/MCP integrations and block
  readiness promotion when probes are unavailable beyond policy.
- Tenant quota and fairness policies apply to concurrent validation and
  smoke-test jobs.

## Audit Events

The runner and policy adapter emit safe audit events for:

- Job accepted, started, passed, failed, skipped, errored, retried, and
  dead-lettered.
- Credential readiness evaluated.
- Tool, outbound domain, and credential policy preview allowed or denied.
- Readiness promotion allowed or blocked.
- Binding preview allowed or denied.
- Workflow publish validation allowed or denied.
- Stale revision token rejected.
- Runtime use blocked by quarantine.

Audit payloads must never include raw secrets, credential values, provider
tokens, raw fixture payloads, unsafe docs, or cross-tenant data.
