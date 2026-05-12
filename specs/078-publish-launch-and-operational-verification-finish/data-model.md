# Data Model: Publish, Launch, And Operational Verification Finish

## Existing Entities Used

### Console Home Quick Action
- Source: backend Console Home envelope.
- Fields: action id, label, href, variant, enabled state, tenant-scoped URL.
- Ownership: backend route and authorization policies.

### Workflow Scenario Intake
- Source: React wizard state until create/save action is submitted.
- Fields: workflow name, workflow key, purpose, launch mode, inputs, outputs, channel preferences, agent count, coordination pattern, approval needs, evidence preference.
- Ownership: React helper for editable scaffolding only; backend owns durable draft after submission.

### Workflow Draft Document
- Source: existing workflow draft and full document save contracts.
- Fields: workflow metadata, roles, contracts, prompt/profile references, skill references, nodes, edges, join policies, approval gates, test requirements, annotations.
- Ownership: workflow registry service and revision-token save route.

### Wizard Step State
- Source: derived from current draft document plus backend validation and publish readiness.
- Fields: key, label, status, summary, blocking reason, recovery target.
- Ownership: React display state only; validation and readiness remain backend-owned.

### Launch Handoff
- Source: existing Admin routes for user runs, Design Reviews, operations, and graph evidence.
- Fields: tenant query, workflow id or published bundle id, safe label.
- Ownership: target workspace authorization and routing.

## Validation Rules

- Spec 078 must not add raw secret, credential, transcript, provider payload, prompt body, completion, memory, stack trace, local path, or unauthorized tenant label fields to UI contracts.
- Workflow key normalization must produce stable lowercase hyphenated keys.
- Draft saves must include revision tokens and idempotency metadata.
- Publish and evidence completion may be summarized but not synthesized in the browser.
