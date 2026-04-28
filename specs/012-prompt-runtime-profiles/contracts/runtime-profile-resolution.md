# Runtime Profile Resolution And Pinning Contract

## Purpose

This contract describes how prompt library versions and agent runtime profile
versions integrate with workflow registry validation, Spec 007 prompt
references, published workflow bundles, run acceptance, and dynamic first-use
pinning.

## Prompt Version Id Flow Into Spec 007

1. A prompt author publishes a prompt draft.
2. The prompt library creates an immutable `prompt_versions.prompt_version_id`
   with template content digest, variable declarations, scope, validation
   evidence, author, timestamp, and publication reason.
3. A model-skill config admin creates or updates a Spec 007
   `PromptReferenceVersion` for workflow, agent, or step scope.
4. Spec 007 validation calls the prompt library repository to verify:
   - `prompt_version_id` exists.
   - The prompt version is active for new use, unless the operation is
     historical review only.
   - The prompt version is visible to the tenant through tenant ownership or a
     per-version platform grant.
   - The supplied `prompt_digest` matches the prompt library content digest.
   - Scope is compatible with the workflow, agent, or step reference.
5. The Spec 007 `PromptReferenceVersion` stores the canonical
   `prompt_version_id` and digest, then continues to participate in existing
   workflow, agent, and step prompt resolution.

Spec 007 remains the owner of prompt reference specificity. The prompt library
is the owner of prompt authoring, immutability, lifecycle status, fixture
preview, and tenant visibility for the target prompt version.

## Runtime Profile Resolution

Input:

```text
tenant_id
agent_key
agent_kind: agent | sub_agent
workflow_lineage_id optional
workflow_version_bundle_id optional
```

Resolution rules:

1. Look for an active tenant-scoped profile version matching
   `(tenant_id, agent_kind, agent_key)`.
2. If one exists and validates for the workflow context, select it.
3. If no tenant profile exists, look for an active platform-scoped profile
   version matching `(agent_kind, agent_key)`.
4. Select the platform profile only when that exact profile version has an
   active tenant grant for `tenant_id`.
5. If neither candidate resolves, return a blocking validation issue.
6. If multiple active candidates exist at the same specificity, fail closed
   with a conflict issue and require operator remediation.

Profile validation must verify referenced prompt versions, model routing hints,
memory policy, skill requirements, tool policy expectations, output contracts,
and test-suite requirements before a profile can become active.

## Workflow Registry Validation

Workflow draft and publication validation must call the prompt/profile
validation adapter with the workflow document, tenant scope, and current actor.

Validation output:

```text
agent_key
agent_kind
step_key optional
resolved_agent_profile_version_id optional
prompt_reference_version_ids
prompt_version_ids
blocking_findings
advisory_findings
safe_summary
```

Blocking findings include:

- Missing active profile for an agent or sub-agent key.
- Retired profile selected for new use.
- Platform profile version lacks tenant grant.
- Profile prompt reference points to a missing prompt version.
- Profile prompt reference points to a retired prompt version for new use.
- Prompt version is unauthorized or wrong scope.
- Spec 007 prompt digest does not match the prompt library digest.
- Model routing hints conflict with model-skill routing scope rules.
- Memory policy, skill requirement, tool policy, output contract, or test
  requirement is absent or incompatible.

## Published Workflow Bundle Pins

When a workflow version is published, the compiler stores a prompt/profile
pin summary in the immutable published bundle metadata:

```json
{
  "prompt_profile_pins": [
    {
      "agent_key": "planner",
      "agent_kind": "agent",
      "step_key": "plan",
      "agent_profile_version_id": "uuid",
      "prompt_reference_version_ids": ["uuid"],
      "prompt_version_ids": ["uuid"],
      "source_scope": "tenant",
      "resolution_digest": "sha256"
    }
  ]
}
```

Published bundle pins are immutable evidence of what workflow publication
validated. They do not replace run acceptance pinning because a run may need
additional dynamic first-use pins.

## Run Acceptance Pinning

Before a run is accepted for worker execution, runtime versioning must persist
the execution bundle with:

- Workflow version bundle id.
- Spec 007 model routing version ids.
- Spec 007 prompt reference version ids.
- Prompt library `prompt_version_id` values.
- Agent runtime `agent_profile_version_id` values.
- Skill, tool, secret-reference, credential, and memory policy version ids
  already required by the existing runtime configuration.

The run acceptance transaction must fail closed when any workflow-declared
profile or prompt reference cannot be resolved, is retired for new use, lacks
tenant authorization, or no longer matches the published bundle validation
digest.

## Dynamic First-Use Pinning

Dynamic first-use pinning is allowed only when an agent or sub-agent is selected
at runtime and was not declared in the workflow bundle.

Required behavior:

1. Resolve the profile using tenant-over-platform precedence.
2. Validate prompt references and policy expectations for the current tenant
   and run context.
3. Persist a first-use pin record and safe audit summary.
4. Add the profile and prompt version ids to the run execution configuration
   before model calls, tool calls, memory writes, or other side effects.
5. Reuse the same first-use pin on retry and resume.

Dynamic first-use pinning must not re-resolve already pinned workflow-declared
agents or mutate completed historical decisions.

## Audit And Redaction

Every validation, selection, pinning, denied resolution, and dynamic first-use
decision records safe audit metadata:

- Actor or system principal.
- Tenant and scope.
- Agent key and kind.
- Selected or considered version ids.
- Reason or denial category.
- Trace id and request id.
- Redacted summary.

Audit records must not contain raw prompt text, rendered prompt text, raw
secrets, credential values, provider tokens, unauthorized run content, or
protected cross-tenant content.
