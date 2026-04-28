# QA010 UI Walkthrough: Admin Console Shell

## Goal

Use a real browser to validate every UI-facing feature delivered by Spec
`010-admin-console-shell`. This guide complements `qa010.md`: use `qa010.md`
for setup, HTTP evidence, SQL checks, and redaction scans; use this file for
visual, interaction, navigation, accessibility, and no-JS behavior.

## Prerequisites

Complete the setup in `specs/010-admin-console-shell/qa010.md` through
"Start The API". The API should be running at:

```text
http://127.0.0.1:8000
```

Use a real browser or the Codex in-app browser. The local browser login flow is:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin
```

When switching principals, revisit `/auth/local-login`, choose a different
principal, and submit the form.

## Reviewer Notes

Record observations in:

```text
/tmp/qa010-ui-review-notes.txt
```

For screenshots, use names like:

```text
/tmp/qa010-ui-admin-platform.png
/tmp/qa010-ui-admin-tenant.png
/tmp/qa010-ui-saved-filters.png
```

## 1. Local Browser Login

1. Open `/auth/local-login?redirect_to=/admin`.
2. Confirm the page title or heading says `Choose a local principal`.
3. Select `platform-admin`.
4. Submit the form.

Expected:

- Browser redirects to `/admin`.
- The cookie-based local-principal session unlocks the admin UI.
- No `X-Local-Principal` header is required in the browser.

## 2. Platform Shell Landing

With `platform-admin`, open:

```text
http://127.0.0.1:8000/admin
```

Expected:

- One visible admin shell frame renders.
- A skip link appears when focused and targets the main content.
- The primary navigation is labeled for admin use.
- The active scope is visibly `Platform`.
- Breadcrumbs show the current admin location.
- The main content landmark is present once.
- The shell does not expose raw secrets, prompt text, memory payloads, stack
  traces, or credential-like strings.

Navigation expectations in platform scope:

- `Console Home` is available.
- `Workflow Registry` is available.
- `Run Search` is available.
- Reliability destinations are available.
- Tenant-only configuration destinations are hidden until a tenant scope is
  selected.

## 3. Tenant Scope Selection

From platform scope:

1. Use the scope selector.
2. Select the Acme tenant scope if it is offered.
3. Confirm the redirected URL includes:

   ```text
   tenant_id=11111111-1111-1111-1111-111111111111
   ```

Expected:

- The active scope label updates within 5 seconds.
- Tenant scope is obvious without opening developer tools.
- Navigation links preserve the active `tenant_id`.
- Tenant-only configuration links are now visible.

## 4. Tenant Shell Landing

Open:

```text
http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Active scope identifies the tenant.
- Navigation groups are visible and organized:
  `Access`, `Workflows`, `Model And Skill Config`, `Run Inspection`,
  `Reliability`.
- The current page is visually active.
- Breadcrumbs are present and sanitized.
- The page remains usable at desktop and narrow mobile widths.

Responsive check:

1. Resize the browser to roughly 390 px wide.
2. Confirm navigation, scope selector, breadcrumbs, and main content do not
   overlap.
3. Confirm text fits inside buttons, navigation links, and state regions.

## 5. Three-Action Navigation Reachability

Starting from tenant `/admin`, reach each destination in three UI actions or
fewer:

- Workflow Registry: `/admin/workflows/ui`
- Configuration: `/admin/config/ui`
- Configuration History: `/admin/config/ui/history`
- Run Search: `/admin/runs`
- Reliability Dashboard: `/admin/reliability/ui/`
- Circuit Breakers: `/admin/reliability/ui/breakers`
- Dead Letters: `/admin/reliability/ui/dead-letters`

Expected:

- Every destination keeps its original route.
- The shared shell remains visible.
- The active nav item changes appropriately.
- Tenant scope stays in the URL where relevant.

## 6. Direct Bookmarked Routes

Paste each URL directly into the browser while logged in as `tenant-admin-acme`:

```text
http://127.0.0.1:8000/admin/workflows/ui?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/config/ui?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/config/ui/history?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/runs?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/breakers?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/dead-letters?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Every page renders inside the shell.
- No route is replaced by a generic shell-only URL.
- Empty pages show shared empty-state UI rather than blank content.

Data-dependent routes to check when matching records exist:

- `/admin/workflows/drafts/{workflow_draft_id}/editor`
- `/admin/workflows/versions/{workflow_version_bundle_id}/detail`
- `/admin/config/ui/runs/{workflow_run_id}/provenance`
- `/admin/runs/{workflow_run_id}`
- `/admin/runs/{workflow_run_id}/replay`

Expected for data-dependent routes:

- The page keeps the direct route.
- The shell context, breadcrumbs, active scope, and sanitized state handling
  still render around the page content.

## 7. Common Empty And Error States

Open these tenant-scoped pages:

```text
http://127.0.0.1:8000/admin/runs?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/breakers?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/dead-letters?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Empty states use the shared shell state component.
- State regions are announced with `role="status"` or `role="alert"`.
- Trace IDs may appear, but stack traces and raw payloads do not.
- Next actions, if shown, are relevant and authorized.

## 8. Saved Filter UI

Open Workflow Registry as `tenant-admin-acme`:

```text
http://127.0.0.1:8000/admin/workflows/ui?tenant_id=11111111-1111-1111-1111-111111111111
```

Create or use visible filter controls for a simple workflow status filter,
then save it as:

```text
Drafts
```

If the list page does not have seeded workflow rows, use the saved-filter page:

```text
http://127.0.0.1:8000/admin/filters/workflows?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Saved-filter UI is inside the shared shell.
- The `Drafts` filter appears with a safe criteria summary.
- Restore links preserve tenant scope.
- Delete is available with a safe fallback if JavaScript is disabled.
- No filter criteria can leak secret, prompt, memory, credential, or raw
  payload text into the UI.

Restore check:

1. Click the `Drafts` restore link.
2. Confirm the destination returns to Workflow Registry.
3. Confirm query parameters reflect the restored criteria and tenant scope.

Delete check:

1. Delete `Drafts`.
2. Confirm the filter no longer appears.
3. Refresh the page and confirm it is still gone.

## 9. Scope Isolation For Saved Filters

1. Save a tenant-scoped filter as `tenant-admin-acme`.
2. Switch to `platform-admin` platform scope.
3. Open `/admin/filters/workflows`.
4. Switch back to Acme tenant scope.

Expected:

- Tenant filter does not appear in platform scope.
- Tenant filter reappears only in the matching tenant scope for the same
  principal/scope rules.
- Cross-tenant filter restoration is not offered.

## 10. Fail-Closed Denials

Forged tenant check:

```text
http://127.0.0.1:8000/admin?tenant_id=22222222-2222-2222-2222-222222222222
```

Use `tenant-admin-acme`.

Expected:

- The response is denied or unavailable in the shell-safe error style.
- The UI does not show unauthorized tenant labels, saved filters, or page
  content.
- The message is sanitized and does not include stack traces.

Non-admin check:

1. Open `/auth/local-login?redirect_to=/admin`.
2. Select `operator-acme`.
3. Submit.

Expected:

- Admin shell access is denied.
- Protected navigation does not render.
- The denial is understandable but does not reveal sensitive internals.

## 11. Breadcrumbs And Active State

Visit these pages and inspect the header/nav:

- `/admin`
- `/admin/workflows/ui`
- `/admin/config/ui/history`
- `/admin/runs`
- `/admin/reliability/ui/breakers`

Expected:

- Breadcrumbs start at `Admin`.
- The final breadcrumb is the active/current page.
- The active nav item has a clear visual state and `aria-current` behavior.
- Breadcrumb and nav labels never include raw IDs unless the page requires
  them and they are safe to display.

## 12. Accessibility Pass

Keyboard-only check:

1. Reload `/admin`.
2. Press `Tab` until the skip link is focused.
3. Activate the skip link.
4. Continue tabbing through scope selector, navigation links, saved-filter
   controls, and page actions.

Expected:

- Focus is visible on every interactive element.
- The skip link moves focus to main content.
- Tab order follows the visible page order.
- Buttons and links have understandable labels.
- No keyboard trap appears.

Screen-reader structure check, using browser accessibility tooling if
available:

- One main landmark.
- Admin navigation has an accessible label.
- State messages use status/alert semantics.
- Form fields and saved-filter controls have labels.

## 13. No-JS Browser Fallback

Disable JavaScript in the browser, then reload:

```text
http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Server-rendered navigation still works.
- Scope links still work.
- Breadcrumbs render.
- Saved-filter forms and delete fallback still work.
- Main content is not blank.

Re-enable JavaScript after this section.

## 14. Optional Enhancement Checks

With JavaScript enabled:

- Scope selector interactions should feel immediate but still navigate through
  safe server routes.
- Saved-filter delete prompts should prevent accidental deletion.
- Enhancement failures should not block baseline navigation or forms.

Expected:

- Reloading the page preserves server-rendered state.
- Browser back/forward works across shell destinations.
- There is no duplicate shell, duplicate main region, or blank page after
  enhanced interactions.

## 15. Visual Polish Checks

Review desktop and mobile widths for:

- No overlapping text or controls.
- Navigation labels do not overflow their containers.
- Cards and panels use restrained admin-console styling.
- Common states are visible but not oversized.
- Saved-filter controls are compact and readable.
- Focus states are visible against the background.
- The UI is not dominated by a single decorative color palette.

Expected:

- The console feels like a dense operational admin tool, not a landing page.
- Existing admin page content remains usable inside the shell.

## 16. Completion Criteria

The UI walkthrough passes when:

- Platform and tenant browser logins both work.
- Active scope can be identified within 5 seconds.
- All primary destinations are reachable in three actions or fewer.
- Direct bookmarked routes preserve their paths and render inside the shell.
- Authorization-aware navigation hides denied destinations.
- Forged tenant and non-admin paths fail closed.
- Common states, breadcrumbs, and safe messages render consistently.
- Saved filters can be created, restored, deleted, and verified as
  scope-bound.
- No-JS fallback remains functional.
- Keyboard navigation and landmarks are usable.
- No sensitive strings appear in visible UI.
