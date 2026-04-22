# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

[Extract from feature spec: primary requirement + technical approach]

## Technical Context

**Language/Version**: [e.g., Python 3.12 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, LangChain, LangGraph, SQLAlchemy or
NEEDS CLARIFICATION]  
**Storage**: [e.g., PostgreSQL + object storage or NEEDS CLARIFICATION]  
**Testing**: [e.g., pytest, contract tests, integration tests]  
**Target Platform**: [e.g., Linux server + Web UI + Telegram webhook]  
**Project Type**: [e.g., multi-service web platform]  
**Performance Goals**: [domain-specific targets]  
**Constraints**: [latency, durability, compliance, quota, or security limits]  
**Scale/Scope**: [tenant, user, or workload scale]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | [PASS/FAIL] | [Checkpoint, retry, compensation, and idempotency notes] |
| Immutable State And Memory | [PASS/FAIL] | [Snapshot and append-only state notes] |
| Contract-First Agent Coordination | [PASS/FAIL] | [Schema, validation, and versioning notes] |
| Security With Practical Development Ergonomics | [PASS/FAIL] | [Auth0, dev bypass, authz, and audit notes] |
| Operability Is A Product Requirement | [PASS/FAIL] | [Logs, metrics, traces, timeline, replay notes] |
| Spec-Driven Delivery | [PASS/FAIL] | [Spec/plan/tasks traceability notes] |
| Test And Documentation Discipline | [PASS/FAIL] | [Coverage, docs, README, and quickstart notes] |
| Clear Ownership And Small Safe Changes | [PASS/FAIL] | [File ownership, sequencing, and rollback notes] |
| Tenant Isolation And Fair Scheduling | [PASS/FAIL] | [Tenant context, quotas, fairness notes] |
| Version-Pinned Execution | [PASS/FAIL] | [Pinned bundle and resume notes] |
| Secret Hygiene And Controlled Tool Access | [PASS/FAIL] | [Secret manager and tool policy notes] |
| Tiered Storage For Large Payloads | [PASS/FAIL] | [PostgreSQL metadata vs object storage notes] |
| Human Approval Is Durable State | [PASS/FAIL] | [Approval wait-state and resume notes] |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
[Replace with the real planned directories and files for this feature]
```

**Structure Decision**: [Document the selected structure and the reasons]

## Failure Recovery And Durability Decisions

- **Checkpoint Boundaries**: [Where durable state is written and why]
- **Retry Strategy**: [Retry limits, backoff, lease handling, and stop
  conditions]
- **Compensation Strategy**: [How external side effects are reversed or
  reconciled]
- **Idempotency Strategy**: [Keys, deduplication, and replay-safe behavior]

## Tenant Isolation And Fair Use Decisions

- **Tenant Context Propagation**: [How tenant_id flows through API, workers,
  storage, audits, and child runs]
- **Isolation Controls**: [RLS, policy guards, access patterns, or boundaries]
- **Quota And Fairness Controls**: [Concurrency, rate, spend, or storage limits]

## Subworkflow And Parent-Child Lineage Decisions

- **Subworkflow Boundaries**: [What is reusable and why]
- **Parent-Child Run Model**: [How lineage is created, persisted, and queried]
- **Replay And Debug Visibility**: [How operators inspect lineage and joins]

## Version Bundle And Contract Decisions

- **Pinned Bundle Contents**: [Workflow, subworkflow, contract, prompt, model,
  tool-policy versions]
- **Resume Policy**: [Why resumes are bundle-stable and how migrations work]
- **Contract Compatibility Plan**: [Schema evolution and validation rules]

## Secret Management And Tool Policy Decisions

- **Secret Manager Integration**: [How secrets are referenced and resolved]
- **Delegated Credential Handling**: [How user-linked credentials differ from
  platform secrets]
- **Tool Access Policy**: [Allowlists, outbound egress, audit, and failure
  behavior]

## Artifact Storage Decisions

- **Transactional Metadata**: [What remains in PostgreSQL]
- **Blob Storage**: [What moves to object storage]
- **Retention And Access**: [Lifecycle, signed access, and audit controls]

## Approval And Resume Decisions

- **Approval Triggers**: [Which states require human action]
- **Persisted Wait State**: [How pause state is modeled and resumed]
- **Audit Trail**: [What is captured for approval, rejection, and supplemental
  input]

## Observability Requirements

- **Logs**: [Structured events, redaction, correlation IDs]
- **Metrics**: [SLOs, counters, latency, quota, or error metrics]
- **Traces**: [Distributed tracing scope and propagation]
- **Timeline And Replay**: [Workflow timeline, lineage, and replay surfaces]
- **Operational Runbooks**: [Dashboards, alerts, or operator workflows]

## Test Strategy

- **Unit Tests**: [Core logic and coverage plan, target >= 90% for relevant
  code]
- **Integration And Contract Tests**: [Interfaces, workflows, and channel paths]
- **Failure And Recovery Tests**: [Crash, retry, resume, and idempotency cases]
- **Operational Validation**: [Load, quota, observability, or replay checks]

## Documentation Tasks

- **README.md Updates**: [What repository-level guidance changes]
- **Quickstart Updates**: [What setup or validation docs must change]
- **Feature Docs**: [API, admin, operator, or runbook docs to add or revise]
- **PR Evidence Requirements**: [Coverage summary, screenshots, traces, or
  validation logs reviewers should expect]

## Security Review Notes

- **Auth/Authz Impact**: [Auth0, roles, bypass, or access control changes]
- **Tenant/Security Boundaries**: [Cross-tenant or privilege risks]
- **Secret/Tool Risk Review**: [Credential and egress review items]
- **Additional Review Needed**: [Threat model, privacy, compliance, or "None"]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., temporary exception] | [current need] | [why compliant option is not yet viable] |
