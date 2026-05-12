# Contract Notes: Generic Scenario Intake And Durable Draft Blueprint

## API Strategy

Spec 075 relies on existing workflow draft create action, full document save action, validation refresh, and generated React API contracts. These are existing backend-owned contracts exposed through generated React Admin TypeScript types.

## Request And Response Boundaries

- Console Home quick action responses may include a Set up workflow action when the principal is authorized for workflow registry access.
- Workflow draft create requests use the existing workflow draft create request body.
- Workflow draft saves use the existing full document save request body with revision token and idempotency key.
- Validation and publish calls use existing builder actions and return backend-owned readiness state.
- Handoff links carry tenant scope and safe workflow identifiers only.

## Compatibility

- No new route family is introduced.
- No database migration is required.
- Generated React types remain authoritative.
- Existing advanced workflow pages remain compatible and linkable.

## Redaction

- Responses and docs must not include raw credentials, provider headers, prompt bodies outside authorized editors, raw completions, private channel payloads, raw external tool payloads, memory contents, raw test transcripts, local paths, stack traces, or unauthorized tenant labels.
