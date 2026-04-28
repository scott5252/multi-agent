# QA010 UI Walkthrough: Admin Console Shell

## Goal

Use a real browser to validate every UI-facing feature delivered by Spec
`010-admin-console-shell`. This guide complements `qa010.md`: use `qa010.md`
for setup, HTTP evidence, SQL checks, and redaction scans; use this file for
visual, interaction, navigation, accessibility, and no-JS behavior.

This walkthrough is written for manual review. You do not need to inspect code
or use browser developer tools unless a step explicitly says they are optional.
The main question to answer on every page is: can an authorized admin clearly
see where they are, what scope they are working in, and what actions are
available without exposing information they should not see?

## Prerequisites

Complete the setup in `specs/010-admin-console-shell/qa010.md` through
"Start The API". The API should be running at:

```text
http://127.0.0.1:8000
```

The base URL is the server origin, not a UI page. Opening
`http://127.0.0.1:8000` directly may return `{"detail":"Not Found"}` because
the app does not define a root route. Start the browser walkthrough with the
local login URL below, then continue to `/admin`.

Use a real browser or the Codex in-app browser. The local browser login flow is:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin
```

When switching principals, revisit `/auth/local-login`, choose a different
principal, and submit the form.

Recommended principal flow:

- Sections 1-3 use `platform-admin`.
- Sections 4-9 use `tenant-admin-acme` in the Acme tenant scope unless the step
  says otherwise.
- Section 10 intentionally uses `tenant-admin-acme` for a denied cross-tenant
  check, then `operator-acme` for a non-admin denial.
- Sections 11-16 should be run after switching back to an admin principal,
  preferably `tenant-admin-acme`.

## Reviewer Notes

Use this section as your review log. The goal is to capture enough evidence
that someone else can understand what you saw without repeating the whole
walkthrough.

Record observations in:

```text
/tmp/qa010-ui-review-notes.txt
```

For each numbered section, add a short note with:

- `Pass` or `Fail`.
- The browser URL you tested.
- The principal you used, such as `platform-admin` or `tenant-admin-acme`.
- What you saw on screen in plain language.
- Any confusing wording, missing navigation, layout issue, or unexpected error.
- A screenshot filename when the visual state matters.

Example note:

```text
Section 4 - Pass
Principal: tenant-admin-acme
URL: http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111
Saw: Admin shell with Acme tenant scope, navigation groups, breadcrumbs, and
main content. Nothing overlapped at desktop width.
Screenshot: /tmp/qa010-ui-admin-tenant.png
```

For screenshots, use names like:

```text
/tmp/qa010-ui-admin-platform.png
/tmp/qa010-ui-admin-tenant.png
/tmp/qa010-ui-saved-filters.png
```

What the main review terms mean:

- `Principal` means the test user identity selected on the local login page.
  `platform-admin` represents a top-level administrator. `tenant-admin-acme`
  represents an administrator limited to the Acme tenant.
- `Scope` means the data boundary the admin is working inside. Platform scope
  is broad. Tenant scope should clearly show the selected tenant and should
  keep tenant-specific pages inside that tenant.
- `Shell` means the shared admin frame around each page: header, scope selector,
  navigation, breadcrumbs, main content area, common states, and shared styling.
- `Breadcrumbs` are the small location trail, starting with `Admin`, that tell
  the reviewer where the current page sits.
- `Sensitive text` means secrets, API keys, raw prompts, raw memory payloads,
  stack traces, credential values, or internal error dumps. These should not be
  visible in normal UI or denial pages.
- `Fail closed` means a denied or broken admin request shows a safe error
  instead of showing protected data, partial navigation, raw internals, or a
  blank confusing page.

If a step fails, record the visible message exactly enough to identify it, but
do not paste any value that looks like a secret, credential, token, prompt, or
private payload into the notes.

## 1. Local Browser Login

Purpose: confirm a browser user can sign in with a local test identity and then
enter the admin console without manually adding API headers.

1. Open:

   ```text
   http://127.0.0.1:8000/auth/local-login?redirect_to=/admin
   ```

2. Confirm the page title or heading says `Choose a local principal`.
3. Select `platform-admin`. This identity is used first because it should be
   allowed to open the platform-level admin console.
4. Submit the form.

Expected:

- Browser redirects to `/admin`.
- The cookie-based local-principal session unlocks the admin UI.
- No `X-Local-Principal` header is required in the browser.

What this means:

- Passing this step means the manual browser session is authenticated and ready
  for the rest of the walkthrough.
- If you still see a login page, a browser error, or `Not Found`, record the URL
  and stop. The later UI checks depend on this login working.

## 2. Platform Shell Landing

With `platform-admin`, open:

```text
http://127.0.0.1:8000/admin
```

Expected:

- One visible admin shell frame renders. You should see one shared page frame,
  not a duplicated header or nested admin layout.
- A skip link appears when focused and targets the main content. To check this,
  click near the top of the page or reload the page and press `Tab`; a link for
  skipping to the main content should become visible.
- The primary navigation is labeled for admin use. It should be clear that the
  links belong to the admin console, not to public product navigation.
- The active scope is visibly `Platform`. This should be readable on screen
  without inspecting HTML or network calls.
- Breadcrumbs show the current admin location, starting at `Admin`.
- The main content landmark is present once. In plain terms, the page should
  have one obvious central content area, not multiple competing main areas.
- The shell does not expose raw secrets, prompt text, memory payloads, stack
  traces, or credential-like strings.

Navigation expectations in platform scope:

- `Console Home` is available.
- `Workflow Registry` is available.
- `Run Search` is available.
- Reliability destinations are available.
- Tenant-only configuration destinations are hidden until a tenant scope is
  selected.

What this means:

- Platform scope is for broad administrative work. Tenant-only links should be
  hidden here because they require a specific tenant boundary.
- If the platform page exposes tenant-only configuration before a tenant is
  selected, record it as a failure because the navigation is not scope-aware.

## 3. Tenant Scope Selection

Purpose: confirm the console can move from platform scope into a specific
tenant scope and make that change obvious to the reviewer.

From platform scope:

1. Find the scope area in the shell. It is in the top bar of the main content
   area, above the breadcrumbs and to the right of the left-hand admin
   navigation. It has the heading `Scope`.
2. On the initial `/admin` page for `platform-admin`, confirm the scope area
   shows `Platform scope` and includes a `Switch scope` dropdown.
3. Open the dropdown, choose the Acme tenant option, and submit with the
   `Switch` button if the page does not switch automatically.
4. If you need to enter the scope directly, open:

   ```text
   http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111
   ```

5. After the Acme tenant page loads, the same top-bar scope area should identify
   the tenant and keep the `Switch scope` dropdown available.
6. Confirm the browser address includes:

   ```text
   tenant_id=11111111-1111-1111-1111-111111111111
   ```

Expected:

- The active scope label updates within 5 seconds.
- Tenant scope is obvious without opening developer tools.
- Navigation links preserve the active `tenant_id`.
- Tenant-only configuration links are now visible.

What this means:

- The `tenant_id` in the URL is how this walkthrough confirms that the browser
  is reviewing the Acme tenant boundary.
- The absence of a `Switch scope` dropdown on the first platform page is a
  failure when active tenants were seeded during QA010 setup. A platform admin
  should not have to type a tenant URL to discover an available tenant scope.
- If the page appears to change tenant but the URL does not preserve the
  `tenant_id`, later navigation may silently leave the selected tenant. Record
  that as a failure.

## 4. Tenant Shell Landing

Switch to `tenant-admin-acme` if you are not already using it. Use the local
login page, choose `tenant-admin-acme`, and submit the form. This confirms the
tenant admin experience, not only the platform admin viewing a tenant.

Open:

```text
http://127.0.0.1:8000/admin?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Active scope identifies the tenant. The page should clearly communicate that
  you are no longer in platform scope.
- Navigation groups are visible and organized:
  `Access`, `Workflows`, `Model And Skill Config`, `Run Inspection`,
  `Reliability`.
- The current page is visually active. The selected navigation item should look
  different from the other links.
- Breadcrumbs are present and sanitized. They should use normal page names and
  should not show raw database errors, secrets, or long internal payloads.
- The page remains usable at desktop and narrow mobile widths.

Responsive check:

1. Resize the browser to roughly 390 px wide.
2. Confirm navigation, scope selector, breadcrumbs, and main content do not
   overlap.
3. Confirm text fits inside buttons, navigation links, and state regions.

What this means:

- Passing this step means the shared shell works for the most important tenant
  view and remains understandable on a small screen.
- If anything covers another control, disappears off screen, or becomes
  unreadable, record the screen width and include a screenshot.

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

For each destination, start from the tenant admin home page, then click through
the visible navigation. Count only deliberate user actions such as opening a
menu, clicking a link, or selecting a tab. Typing the URL directly does not
count for this section.

Expected:

- Every destination keeps its original route.
- The shared shell remains visible.
- The active nav item changes appropriately.
- Tenant scope stays in the URL where relevant.

What this means:

- Admin users should not need to hunt through the application to reach primary
  tools. Three actions or fewer confirms the shell navigation is usable for
  repeated operational work.
- If you can only reach a destination by typing the URL directly, record it as a
  navigation failure for this section.

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

What this means:

- These URLs represent bookmarked pages or links shared between admins. Opening
  them directly should preserve the requested page and still wrap it in the
  shared shell.
- A page with no data may show an empty state. That is acceptable when it
  explains what is missing and what the user can do next. A blank white page is
  not acceptable.

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

What this means:

- Only test the data-dependent routes when you have real IDs from seeded or
  created records. Do not invent placeholder IDs and treat the resulting error
  as a UI failure.

## 7. Common Empty And Error States

Open these tenant-scoped pages:

```text
http://127.0.0.1:8000/admin/runs?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/breakers?tenant_id=11111111-1111-1111-1111-111111111111
http://127.0.0.1:8000/admin/reliability/ui/dead-letters?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected:

- Empty states use the shared shell state component. The message should look
  like part of the admin console, not an unstyled browser error.
- State regions are announced with `role="status"` or `role="alert"`. If you do
  not use accessibility tooling, confirm at minimum that the message is plainly
  visible and placed near the relevant content.
- Trace IDs may appear, but stack traces and raw payloads do not.
- Next actions, if shown, are relevant and authorized.

What this means:

- Empty or unavailable data should help the admin understand the situation
  without leaking internals. A trace ID is acceptable because it helps support
  investigate; stack traces and raw payloads are not.

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

This section verifies the browser UI for saved filters. If the saved-filter page
shows `No saved filters`, complete the saved-filter setup in
`specs/010-admin-console-shell/qa010.md`, then refresh this page. The expected
test filter is named `Drafts`; it represents a reusable Workflow Registry view
for draft workflows.

Expected:

- Saved-filter UI is inside the shared shell.
- The `Drafts` filter appears with a safe criteria summary.
- Restore links preserve tenant scope.
- Delete is available with a safe fallback if JavaScript is disabled.
- No filter criteria can leak secret, prompt, memory, credential, or raw
  payload text into the UI.

What this means:

- Saved filters are tenant-scoped shortcuts. They should make it easy to return
  to common filtered views without exposing hidden criteria or crossing into a
  different tenant.
- If the Workflow Registry page has no rows or visible filter controls, use the
  saved-filter page as the fallback path and note that in your review log. If
  the fallback page also has no saved filters, mark the saved-filter creation
  portion as blocked until the setup data exists, then continue with the rest of
  the walkthrough.

Restore check:

1. Click the `Drafts` restore link.
2. Confirm the destination returns to Workflow Registry.
3. Confirm query parameters reflect the restored criteria and tenant scope.

Delete check:

1. Delete `Drafts`.
2. Confirm the filter no longer appears.
3. Refresh the page and confirm it is still gone.

What this means:

- Restore proves a saved filter can be reused.
- Delete proves the UI can remove stale filters and does not make them reappear
  after a page refresh.

## 9. Scope Isolation For Saved Filters

Purpose: confirm saved filters do not leak between platform and tenant scopes.

1. Save a tenant-scoped filter as `tenant-admin-acme`.
2. Switch to `platform-admin` platform scope by returning to the local login
   page, choosing `platform-admin`, and opening `/admin`.
3. Open:

   ```text
   http://127.0.0.1:8000/admin/filters/workflows
   ```

4. Switch back to Acme tenant scope as `tenant-admin-acme`.

Expected:

- Tenant filter does not appear in platform scope.
- Tenant filter reappears only in the matching tenant scope for the same
  principal/scope rules.
- Cross-tenant filter restoration is not offered.

What this means:

- A saved filter created for one tenant must not become visible in another
  scope. This protects tenant boundaries and prevents confusing navigation.

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

What this means:

- This intentionally asks the Acme tenant admin to open another tenant's URL.
  The correct behavior is a safe denial. Seeing protected page content here is a
  serious failure.

Non-admin check:

1. Open `/auth/local-login?redirect_to=/admin`.
2. Select `operator-acme`.
3. Submit.

Expected:

- Admin shell access is denied.
- Protected navigation does not render.
- The denial is understandable but does not reveal sensitive internals.

What this means:

- `operator-acme` is intentionally not an admin for this walkthrough. The user
  should receive a clear denial, not partial access to admin pages.

## 11. Breadcrumbs And Active State

Switch back to `tenant-admin-acme` before continuing if Section 10 left the
browser signed in as `operator-acme`.

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

What this means:

- Breadcrumbs and active navigation are orientation aids. They should help the
  reviewer answer "where am I?" immediately after landing on a page.

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

What this means:

- A keyboard-only user should be able to reach every important control, see
  where focus is, and leave every component without getting stuck.

Screen-reader structure check, using browser accessibility tooling if
available:

- One main landmark.
- Admin navigation has an accessible label.
- State messages use status/alert semantics.
- Form fields and saved-filter controls have labels.

What this means:

- These checks confirm the page has enough structure for assistive technology
  to describe the admin shell accurately.

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

What this means:

- JavaScript may improve interactions, but the server-rendered admin console
  should still be usable without it. This protects basic admin workflows when a
  script fails or is blocked.

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

What this means:

- Enhanced interactions should feel smoother, but they must not replace or
  break the baseline server-rendered experience.

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

What this means:

- This spec is for an operational console. The UI should prioritize clarity,
  scanability, and repeated use over marketing-style presentation.

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

When finished, add a final summary to `/tmp/qa010-ui-review-notes.txt` with:

- Overall result: `Pass`, `Pass with issues`, or `Fail`.
- The principals tested.
- Any sections skipped and why.
- Screenshot paths for the most important evidence.
- A short list of follow-up issues, if any.
