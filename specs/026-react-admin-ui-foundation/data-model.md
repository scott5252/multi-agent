# Data Model: React Admin UI Foundation

Spec 026 adds no durable PostgreSQL tables. The data model is a set of
backend-owned API contracts derived from existing principal, tenant, navigation,
settings, and version sources.

## ReactAdminBootstrap

Represents the safe payload required to render the minimal React admin shell.

Fields:
- `principal`: `ReactAdminPrincipal`
- `active_scope`: `ReactAdminScope`
- `available_scopes`: list of `ReactAdminScopeOption`
- `navigation`: list of `ReactAdminNavigationGroup`
- `feature_flags`: `ReactAdminFeatureFlags`
- `version`: `ReactAdminVersion`
- `asset_manifest`: `ReactAdminAssetManifestSummary`
- `action_tokens`: `ReactAdminActionTokens`

Validation rules:
- Must be returned only for an authorized admin principal.
- Must omit raw identity claims, raw tokens, secrets, credentials, prompts,
  completions, memory contents, provider payloads, tool payloads, and stack
  traces.
- Must reflect the selected tenant/platform scope resolved by the backend.

## ReactAdminPrincipal

Safe display summary for the current authenticated principal.

Fields:
- `principal_id`: safe principal identifier
- `display_name`: optional safe display name
- `role_codes`: allowed role codes required for UI visibility decisions
- `auth_mode`: `auth0` or `local_principal`
- `trace_id`: safe trace/correlation identifier

Validation rules:
- Must not include raw JWT claims, bearer tokens, provider identifiers beyond
  approved safe IDs, or private profile fields.
- `auth_mode` must be explicit so QA can prove dual-mode coverage.

## ReactAdminScope

Backend-resolved active admin scope.

Fields:
- `scope_type`: `platform` or `tenant`
- `tenant_id`: UUID when `scope_type` is `tenant`, otherwise null
- `label`: redaction-safe label

Validation rules:
- Tenant scope requires a tenant ID granted to the principal.
- Platform scope is available only to platform-admin principals.
- Inactive or unauthorized tenants produce fail-closed denied/unavailable
  responses.

## ReactAdminScopeOption

Safe switch target for an available scope.

Fields:
- `scope`: `ReactAdminScope`
- `label`: safe label
- `href`: backend-generated admin scope link
- `selected`: boolean

Validation rules:
- Options include only scopes available to the principal.
- Links must be relative admin paths.

## ReactAdminNavigationGroup

Authorized navigation group for the shell.

Fields:
- `label`: safe group label
- `items`: list of `ReactAdminNavigationItem`

Validation rules:
- Empty groups are omitted.
- Group and item labels pass existing sanitization rules.

## ReactAdminNavigationItem

Authorized destination rendered in the React shell.

Fields:
- `item_id`
- `label`
- `group`
- `href`
- `route_surface_key`
- `required_scope`
- `admin_area`
- `preserve_tenant_scope`
- `active`
- `fallback_kind`: `jinja`, `react`, or `disabled`

Validation rules:
- Items are omitted when policy denies the principal.
- `href` must be a relative admin path.
- Future React domain items remain `disabled` or point to Jinja fallback until
  their feature flag is enabled by later specs.

## ReactAdminFeatureFlags

Backend-owned rollout state.

Fields:
- `react_admin_enabled`: boolean
- `react_domain_routes`: map of route key to boolean
- `source`: safe label such as `settings`

Validation rules:
- Unknown domain route flags default to false.
- The browser may display flags but cannot use them as authorization proof.

## ReactAdminAssetManifestSummary

Safe built asset metadata.

Fields:
- `available`: boolean
- `base_path`: `/admin/static/react`
- `entrypoints`: list of safe asset URLs
- `version`: optional manifest hash or app version

Validation rules:
- Must never expose local filesystem paths.
- Missing or malformed manifests produce safe unavailable states.

## ReactAdminActionTokens

Server-owned action protection placeholders for future React mutations.

Fields:
- `csrf_token`: nullable string
- `issued_at`: nullable ISO timestamp

Validation rules:
- Tokens are scoped to the authenticated session and must not contain provider
  credentials.
- Spec 026 only proves transport and redaction boundaries; domain mutation use
  arrives in later specs.
