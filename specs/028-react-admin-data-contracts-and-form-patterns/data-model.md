# Data Model: React Admin Data Contracts And Form Patterns

## AdminPageEnvelope

Carries a backend-authorized page response for a React admin page.

Fields:

- `page_id`: stable page key.
- `title`: safe page title.
- `description`: safe page summary.
- `scope`: active platform or tenant scope.
- `state`: optional common state descriptor.
- `data`: typed safe payload for the page.
- `filters`: allowed filter profile and active chips.
- `pagination`: bounded page or cursor metadata.
- `sorting`: allowed sort fields and active sort.
- `actions`: backend-defined actions.
- `evidence`: safe audit or operational evidence summaries.
- `refresh`: optional polling or refresh hint.

Rules:

- Created only after authentication, tenant scoping, and authorization pass.
- Must not include raw prompts, completions, memory, private channel messages, provider payloads, tool payloads, secrets, stack traces, local filesystem paths, or unauthorized tenant labels.

## SafeProblemDetail

Browser-facing error contract.

Fields:

- `type`: stable reason URI or category key.
- `title`: safe title.
- `status`: HTTP status.
- `detail`: safe user-facing detail.
- `reason_category`: safe reason category.
- `field_errors`: optional field validation details.
- `retry_after_seconds`: optional retry hint.
- `audit_reference_id`: optional safe audit reference.

Rules:

- No raw exceptions or stack traces.
- Field paths must map to rendered fields or safe global form errors.

## ValidationFieldError

Describes a form validation issue.

Fields:

- `field`: form field key.
- `label`: safe display label.
- `message`: safe validation message.
- `code`: stable validation code.

Rules:

- Message must be safe for all authorized viewers in the active scope.

## AdminAction

Describes an action React may render.

Fields:

- `action_id`: stable action key.
- `label`: safe label.
- `method`: `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`.
- `href`: protected backend URL.
- `variant`: visual priority.
- `requires_confirmation`: boolean.
- `confirmation`: optional confirmation requirement.
- `requires_idempotency_key`: boolean.
- `action_token`: optional backend-issued token reference.
- `enabled`: boolean.
- `disabled_reason`: optional safe reason.

Rules:

- React must not enable disabled actions.
- React must not synthesize unlisted actions.

## MutationResult

Describes the outcome of a sample or future domain mutation.

Fields:

- `status`: accepted, validation-error, stale-conflict, replayed, confirmation-required, dependency-unavailable, or unexpected-error.
- `summary`: safe outcome summary.
- `toast`: optional safe toast metadata.
- `field_errors`: optional field validation details.
- `stale_conflict`: optional revision conflict details.
- `idempotency`: optional replay metadata.
- `confirmation`: optional confirmation requirement.
- `audit_reference_id`: optional safe audit reference.
- `next_action`: optional safe follow-up action.

Rules:

- Domain side effects remain backend-owned.
- Idempotency replay metadata must not expose raw request bodies.

## RevisionConflict

Describes optimistic concurrency failure.

Fields:

- `submitted_revision`: caller revision token.
- `current_revision`: safe current revision token.
- `message`: safe recovery guidance.
- `reload_href`: safe page reload URL.

Rules:

- Must not expose raw previous or current object payloads.

## FilterProfile

Describes allowed filters and active filter chips.

Fields:

- `profile_id`: stable filter profile key.
- `criteria`: allowed filter criteria.
- `active_chips`: safe active filter chips.
- `saved_filters`: safe saved filter summaries.

Rules:

- Unknown criteria are rejected by backend validation.
- Saved filter chips expose safe labels and links only.

## PaginationState

Describes bounded result navigation.

Fields:

- `page_size`: current bounded size.
- `page_size_options`: allowed page sizes.
- `next_cursor`: optional safe cursor.
- `previous_cursor`: optional safe cursor.
- `total_known`: boolean.
- `total_items`: optional count.

Rules:

- Page size must be capped.
- Cursors must be opaque and safe.

## SortingState

Describes allowed sort fields.

Fields:

- `active`: active sort key and direction.
- `allowed`: safe sort field labels and directions.

Rules:

- Unknown sort fields are rejected.

## ExportSnapshot

Describes a safe export status.

Fields:

- `export_id`: safe export key.
- `status`: queued, running, complete, failed, or expired.
- `summary`: safe summary.
- `artifact_reference_id`: optional artifact reference.
- `progress_label`: optional progress label.
- `expires_at`: optional expiry timestamp.
- `audit_reference_id`: optional safe audit reference.

Rules:

- No local filesystem paths.
- No raw export content.

## EvidenceSummary

Describes safe audit, delivery, runtime, gateway, or export evidence.

Fields:

- `evidence_id`: safe identifier.
- `label`: safe label.
- `summary`: safe summary.
- `reference_type`: audit, export, delivery, runtime, gateway, or validation.
- `href`: optional authorized link.

Rules:

- Evidence summaries must be redacted before reaching React.

## PatternsSamplePage

Harmless demo payload for Spec 028.

Fields:

- `records`: sample rows derived from current scope.
- `form`: sample form descriptor and default values.
- `export_snapshot`: sample export status.
- `details`: safe details panel data.

Rules:

- Must not mutate real domain state.
- Must be independently testable by local-principal Playwright flows.
