# Research: No-Jinja React Host, Auth, Shell Utilities, And Local Login

## Decision: Serve React Host Without TemplateResponse

- **Decision**: Replace `container.workflow_ui_templates.TemplateResponse(..., "admin_react/app.html", ...)` with a small backend renderer that returns `HTMLResponse` assembled from the React asset manifest and safe configuration values.
- **Rationale**: The current React host is still a Jinja template even when the visible UI is React. A focused renderer keeps the backend source of truth for asset paths, CSP/cache headers, bootstrap/config URLs, and unavailable text while removing server-side Jinja from the admin entry route.
- **Alternatives considered**: Keep `admin_react/app.html` until Spec 047; rejected because Spec 039 explicitly owns the app host. Serve a checked-in static HTML file; rejected because it would duplicate dynamic asset manifest and bootstrap URL handling.

## Decision: Local Login Uses React Plus Server-Owned JSON/Action Contracts

- **Decision**: Convert `/auth/local-login` GET to a non-Jinja React host/route and expose local-principal login metadata and submit/logout actions through backend-owned contracts. Keep local mode unavailable as a non-Jinja 404/problem outside `AUTH_MODE=local_principal`.
- **Rationale**: Playwright validation for later specs depends on local-principal auth, but the existing page is a Jinja template and accepts unsafe redirect defaults. Server-owned contracts preserve principal catalog filtering, action-token validation, session cookie issuance, redirect sanitization, and audit evidence.
- **Alternatives considered**: Render a plain non-Jinja HTML form; acceptable as a fallback but weaker for long-term React-only UI. Move principal selection fully into browser fixtures; rejected because auth decisions must remain server-owned.

## Decision: Redirect Old Shell URLs To React When Safe

- **Decision**: Convert `/admin`, `/admin/scope`, and saved-filter/shell utility browser routes to redirects or JSON/non-Jinja responses that preserve tenant id, query filters, saved-filter intent, and safe return URL where authorized.
- **Rationale**: Direct-link compatibility matters for bookmarks and QA docs. Redirects keep users on the React-only browser surface while retaining backend authorization and audit checks.
- **Alternatives considered**: Return 410 for all old shell routes; rejected because it would break safe admin bookmarks and support links. Keep Jinja fallbacks; rejected because this spec must remove server-side Jinja rendering from the entry path.

## Decision: Saved Filters Become React-Managed Shell Utilities

- **Decision**: Reuse the existing admin saved-filter repository and shell bootstrap chips, add React management/list/mutation affordances, and keep mutations behind backend validation/action-token checks.
- **Rationale**: Saved filters are a shared shell workflow and appear in current shell templates. Moving management into React prevents each later domain spec from carrying shell fallback dependencies.
- **Alternatives considered**: Defer saved filters to domain-specific specs; rejected because `admin_shell/saved_filters*.html` is part of the shell/auth inventory group.

## Decision: Denied And Unavailable States Stay Redaction-Safe

- **Decision**: Authenticated React routes render denied/unavailable states through existing `StatePanel`/common state primitives when bootstrap is available; early bootstrap failures return non-Jinja `SafeProblem` or minimal HTML with trace id only.
- **Rationale**: Existing Jinja unavailable pages centralize fail-closed behavior. React-only replacements must keep the same privacy posture and avoid leaking resource existence, tenant labels, local paths, or stack traces.
- **Alternatives considered**: Expose raw HTTP exception details for easier debugging; rejected by redaction and security rules.

## Decision: Delete Only Spec 039-Proven Shell/Auth Files

- **Decision**: Delete `admin_react/app.html`, `auth/local_login.html`, `admin_shell/*.html`, and `web_admin/static/admin_shell.js` only after route/import scanners, backend tests, frontend tests, QA docs, and Playwright evidence prove they are obsolete.
- **Rationale**: Spec 038 classified these items as shell/auth-owned and not yet safe. Spec 039 can convert them, but global `Jinja2Templates`, domain templates, and `jinja2` dependencies remain until later specs and final decommissioning.
- **Alternatives considered**: Delete all templates extending `admin_shell/base.html`; rejected because Specs 040 through 046 own domain-specific parity and deletion.
