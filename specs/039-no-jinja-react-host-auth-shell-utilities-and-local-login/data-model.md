# Data Model: No-Jinja React Host, Auth, Shell Utilities, And Local Login

## ReactHostDocument

- **Purpose**: Non-Jinja HTML response that bootstraps the React admin app.
- **Fields**:
  - `mount_path`: React mount path, currently `/admin/app`.
  - `bootstrap_url`: Authorized backend bootstrap contract URL, including safe tenant query when applicable.
  - `config_url`: React configuration contract URL.
  - `asset_manifest`: Safe summary of entrypoint and stylesheet assets.
  - `unavailable_reason`: Redaction-safe reason when built assets are unavailable.
- **Validation Rules**:
  - Asset URLs must be relative to the configured React static base.
  - HTML must not contain raw principal payloads, secrets, stack traces, or local filesystem paths.
  - Response must be produced without `TemplateResponse`.

## LocalLoginEnvelope

- **Purpose**: Backend-owned data needed for React local-principal login.
- **Fields**:
  - `auth_mode`: Must be `local_principal` when available.
  - `principals`: Enabled local-principal choices with catalog key, safe display name, scope type, role summaries, and tenant label when authorized.
  - `current_principal_key`: Current local principal cookie key when present.
  - `redirect_to`: Sanitized admin return URL.
  - `action_token`: CSRF/action token or equivalent protected nonce.
  - `unavailable_problem`: Safe problem detail when local login is disabled.
- **Validation Rules**:
  - Principal catalog excludes disabled entries.
  - Redirect targets must be same-origin admin paths and must not preserve unsafe external URLs.
  - Token failures return non-Jinja safe problems and do not set cookies.

## LocalLoginSubmission

- **Purpose**: Request to create a deterministic local-principal session.
- **Fields**:
  - `principal_key`: Selected enabled principal catalog key.
  - `redirect_to`: Requested admin return URL.
  - `action_token`: Token issued by the envelope.
- **Validation Rules**:
  - `principal_key` must exist and be enabled.
  - `action_token` must be valid for the session/request context.
  - Response sets only the configured local-principal cookie and redirects to a sanitized admin path.

## ShellRedirectDecision

- **Purpose**: Documents how an old shell/admin browser URL is handled after template removal.
- **Fields**:
  - `source_path`: Old browser path.
  - `target_path`: React route or null for non-Jinja problem/retirement response.
  - `status_code`: Redirect or problem status.
  - `preserved_values`: Tenant, route params, filters, saved-filter intent, and return destination values preserved.
  - `reason`: Safe decision reason.
  - `requires_authentication`: Whether principal validation is required before redirecting.
- **Validation Rules**:
  - Unsafe or ambiguous redirects fail closed to a non-Jinja problem.
  - Cross-tenant destinations must not disclose tenant labels or resource existence.

## SavedFilterReactEnvelope

- **Purpose**: React-compatible saved-filter management data.
- **Fields**:
  - `admin_area`: Admin area the saved filters apply to.
  - `active_scope`: Platform or tenant scope.
  - `saved_filters`: Existing safe saved-filter summaries.
  - `form`: Field metadata and action URL for create/update/delete.
  - `mutation_result`: Safe result or validation errors from the last mutation.
  - `action_tokens`: CSRF/action-token metadata.
- **Validation Rules**:
  - Saved filters are tenant-scoped and principal-authorized.
  - Labels and criteria are sanitized through existing admin console helpers.
  - Mutation responses include safe summaries only.

## RetirementEvidenceRecord

- **Purpose**: Reviewer-facing record for each Spec 039 inventory item.
- **Fields**:
  - `item_id`: Spec 038 inventory item id.
  - `source_path`: Repo-relative template, route, or asset path.
  - `decision`: Deleted, redirected, converted, retained, or blocked.
  - `evidence_refs`: Tests, QA docs, screenshots, scanner output, and reviewer notes.
  - `rollback_guidance`: Safe restoration or mitigation instructions.
- **Validation Rules**:
  - Records must use repo-relative paths and redaction-safe references.
  - Deleted decisions require route/import scanner evidence and dual-auth tests.
