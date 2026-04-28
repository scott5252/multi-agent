# Admin Web View Contract: Model Providers

## Navigation

Add a shared admin shell item:

```text
Label: Model Providers
Path: /admin/model-providers
Surface policy: platform-admin mutation, tenant-scoped read visibility
```

## Pages

### List

`GET /admin/model-providers`

Shows provider connections visible to the active admin scope with filters for
provider type, health state, active state, tenant visibility, and model id.

Required columns:

- Display name
- Provider type
- Active state
- Health state
- Last test outcome
- Model count
- Tenant visibility summary
- Catalog sync status
- Updated timestamp

### Create

`GET /admin/model-providers/new`

Platform administrators only. Renders a form for provider type, display name,
base URL when applicable, model definitions, capability metadata, cost
metadata, timeout policy, tenant visibility, secret references, and active
state.

### Edit

`GET /admin/model-providers/{connection_id}/edit`

Platform administrators only. Renders the same fields as create, preserving
existing values. Secret references are displayed as safe reference ids only.

### Detail

`GET /admin/model-providers/{connection_id}`

Shows safe connection metadata, latest health snapshot, last test result,
model definitions, tenant visibility, catalog entries, sync records, and
audit/debug links.

### Test Results

`GET /admin/model-providers/{connection_id}/tests`

Shows retained safe probe results with timestamp, actor/source, latency,
tested model, outcome, normalized reason, and safe diagnostics.

### Catalog

`GET /admin/model-providers/catalog`

Shows tenant-visible model provider catalog entries with tenant scope,
provider type, display name, model id, health state, availability, governing
connection, collision warnings, and routing selectability.

## Form Actions

- `POST /admin/model-providers`
- `POST /admin/model-providers/{connection_id}`
- `POST /admin/model-providers/{connection_id}/activate`
- `POST /admin/model-providers/{connection_id}/deactivate`
- `POST /admin/model-providers/{connection_id}/test`
- `POST /admin/model-providers/{connection_id}/sync-catalog`

All form actions require platform administrator authority and must audit denied
attempts.

## Safe States

The shared shell must render:

- Empty list with no cross-tenant hints.
- Validation errors without raw provider responses or secret values.
- Audit persistence unavailable state when security/governance evidence cannot
  be stored.
- Catalog collision warnings with model id and tenant scope only.
- Probe failure summaries with normalized category and safe action text.

## Accessibility And UX

- All forms use labels, help text, and server-rendered validation messages.
- Buttons for activation, deactivation, testing, and sync show current disabled
  state when the actor lacks authority.
- Test and sync actions provide shared-shell flash results and return to the
  connection detail page.
- Pages remain usable without optional JavaScript; `model_providers.js`
  enhances dynamic model rows and test result refresh only.
