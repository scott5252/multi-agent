# Data Model: Modern Admin Shell And Design System

Spec 027 introduces browser-facing presentation models only. No new durable
database tables are planned.

## Shell Chrome Metadata

Represents the global React shell presentation.

Fields:

- `product_name`: Human-readable shell name.
- `active_area`: Current admin area id or `home`.
- `breadcrumbs`: Ordered safe breadcrumb items.
- `page_actions`: Authorized contextual actions for the current shell page.
- `notifications`: Safe notification summaries.
- `design_token_version`: Version string for frontend token metadata.

Validation:

- Labels must be sanitized by the backend or by existing safe text helpers.
- URLs must pass existing safe redirect validation.
- Actions must be read-only links unless a backend-protected mutation exists.

## Breadcrumb Item

Represents one visible path segment.

Fields:

- `label`: Safe display text.
- `href`: Optional safe destination.
- `active`: Whether this item represents the current page.

Validation:

- At most one item should be active.
- Inactive items with `href` must point to authorized admin destinations.

## Page Action

Represents an authorized contextual command.

Fields:

- `action_id`: Stable action key.
- `label`: Safe display text.
- `href`: Optional safe link.
- `method`: `get` for links in Spec 027.
- `variant`: `primary`, `secondary`, `danger`, or `ghost`.
- `disabled_reason`: Optional safe reason when unavailable.

Validation:

- Spec 027 does not introduce browser-side protected mutations.
- Danger actions must remain disabled unless backed by existing server actions.

## Shell State Descriptor

Represents common UI states.

Fields:

- `state`: `loading`, `empty`, `filtered_empty`, `denied`, `not_found`,
  `validation_error`, `dependency_unavailable`, `partial_data`, or
  `unexpected_error`.
- `title`: Safe user-facing title.
- `summary`: Safe user-facing explanation.
- `action`: Optional safe page action.
- `trace_id`: Optional trace id for support.

Validation:

- Must not include raw stack traces or restricted payloads.
- Denied states must not name unauthorized tenants or hidden resources.

## Saved Filter Chip

Represents a saved filter visible in the shell.

Fields:

- `filter_id`: Stable opaque id.
- `label`: Safe display label.
- `admin_area`: Owning admin area.
- `href`: Backend-generated safe destination.
- `scope_type`: `platform` or `tenant`.
- `tenant_id`: Optional tenant id when scoped.

Validation:

- Browser does not parse raw criteria.
- Tenant id must match the active authorized scope when present.

## Command Search Result

Represents one safe command/search result.

Fields:

- `result_id`: Stable opaque id.
- `label`: Safe display label.
- `description`: Optional safe summary.
- `group`: Navigation group or command group.
- `href`: Safe destination.
- `required_scope`: `platform`, `tenant`, or `either`.
- `fallback_kind`: `jinja`, `react`, or `disabled`.

Validation:

- Results are derived from authorized navigation metadata.
- No raw object payloads, prompt text, memory content, or private messages.

## Shell Notification

Represents a safe shell-level status note.

Fields:

- `notification_id`: Stable id for rendering.
- `tone`: `info`, `success`, `warning`, or `critical`.
- `title`: Safe title.
- `summary`: Safe summary.
- `href`: Optional safe destination.

Validation:

- Critical notifications must be actionable or link to an authorized safe page.
- Notification text must never include secrets, raw provider payloads, or stack
  traces.
