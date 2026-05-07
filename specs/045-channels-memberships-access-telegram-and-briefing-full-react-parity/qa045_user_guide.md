# QA045 User Guide: Spec 045 - Channels, Memberships, Access, Telegram, And Briefing Full React Parity

## Detailed Overview

Spec 045 removes the remaining domain-specific Jinja browser pages for
memberships, Telegram configuration, and briefing preferences.

The replacement pages already exist in React.

Membership administration now lives at `/admin/app/memberships`.

Telegram configuration, delivery diagnostics, run status, and briefing
preferences now live at `/admin/app/channels`.

The old URLs still matter because users may have bookmarks, saved filters, or
old form submissions.

Old membership URLs should redirect to the React membership workspace.

Old Telegram URLs should redirect to the React channel workspace.

Old briefing preference URLs should redirect to the React channel workspace.

Retained JSON APIs stay available for React and API callers.

The deleted templates are `memberships/index.html`, `telegram/index.html`, and
`briefing_preferences/index.html`.

The admin shell Jinja templates are not part of Spec 045. They are kept for the
final infrastructure decommission spec.

The most sensitive behavior in this spec is token visibility.

Telegram link tokens may appear only in the immediate creation response.

Later token lists, diagnostics, screenshots, and logs must show fingerprints or
safe metadata only.

The second sensitive behavior is tenant isolation.

Acme users must not see Globex membership, Telegram, or briefing data.

The third sensitive behavior is private preference redaction.

Briefing preferences can include VIP sender values, delegated account
references, location labels, and schedules.

Admin summaries must show safe summaries rather than raw private values.

## Who Should Use This Guide

Use this guide if you are a QA reviewer checking browser migration behavior.

Use this guide if you are a platform admin reviewing membership and access
workflows.

Use this guide if you are a tenant admin reviewing Telegram or briefing
workflows.

Use this guide if you are a developer confirming deleted templates stay deleted.

Use this guide if you are a security reviewer checking token, Telegram,
preference, and tenant redaction.

You do not need to know the full database schema.

You should be comfortable opening local URLs, choosing a local test principal,
and recording expected results.

## Manual QA Prerequisites

1. Start from the repository root.

2. Copy `.env.qa045` from the Spec 045 directory to `.env`.

3. Run `uv sync`.

4. Start PostgreSQL with `docker compose up -d postgres`.

5. Drop and recreate only `multi_agent_platform_qa045`.

6. Run `uv run alembic upgrade head`.

7. Seed Acme and Globex tenants.

8. Start the API on `127.0.0.1:8000`.

9. Use `http://127.0.0.1:8000/auth/local-login` for local sign-in.

10. Use `platform-admin` for broad admin checks.

11. Use `tenant-admin-acme` for Acme tenant checks.

12. Use `tenant-user-acme` for user-safe briefing checks.

13. Use `tenant-admin-globex` only for cross-tenant comparison.

14. Capture notes and screenshots under `/tmp/qa045-*`.

15. Do not use real Telegram, real Auth0, real provider calls, real credentials,
or external connectors.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels`.

2. Select `platform-admin`.

3. Confirm the browser lands on `/admin/app/channels`.

4. Confirm the page is the React channel workspace.

5. Capture `/tmp/qa045-channels-screen.png`.

6. Open `/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111`.

7. Confirm the browser redirects to `/admin/app/channels`.

8. Confirm the URL keeps the Acme tenant id.

9. Confirm the URL includes `panel=telegram`.

10. Record the source and destination in `/tmp/qa045-legacy-redirect-notes.txt`.

11. Create a Telegram link token through the React control or old form route.

12. Confirm the raw token appears only in the immediate creation result.

13. Refresh or list link token audits.

14. Confirm only fingerprint or metadata remains visible.

15. Confirm full Telegram ids are not visible in diagnostics or identities.

16. Open `/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111`.

17. Confirm the browser redirects to `/admin/app/channels`.

18. Confirm the URL includes `panel=briefing`.

19. Save a briefing preference profile for Acme.

20. Confirm the old form route redirects to React.

21. Confirm admin summaries do not show raw VIP sender or delegated account
references.

22. Open `/admin/app/memberships`.

23. Confirm the page is the React membership workspace.

24. Capture `/tmp/qa045-memberships-screen.png`.

25. Open `/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111&q=reviewer`.

26. Confirm the browser redirects to `/admin/app/memberships`.

27. Confirm the URL keeps the Acme tenant id and query.

28. Create an invitation through the old form route.

29. Confirm the old form route redirects to React memberships.

30. Confirm retained API output masks the email address.

31. Create or inspect a principal link.

32. Confirm raw Auth0 subjects are not visible in browser evidence.

33. Create or inspect a role grant.

34. Confirm tenant admins cannot assign platform roles.

35. Suspend or reactivate a principal in a safe fixture.

36. Confirm status actions redirect to React memberships.

37. Switch local login to `tenant-admin-acme`.

38. Open the Acme channel route.

39. Confirm Acme tenant views are allowed.

40. Open the Globex channel route while still signed in as Acme.

41. Confirm the request fails closed or shows a safe denied state.

42. Open the Globex membership route while signed in as Acme.

43. Confirm the request fails closed.

44. Open the Globex briefing preference route while signed in as Acme.

45. Confirm the request fails closed.

46. Run the focused backend tests.

47. Run the focused frontend tests.

48. Run QA document validation.

49. Run Spec QA.

50. Run Playwright validation.

51. Open `output/playwright/qa045_ui/qa045-react-ui2-smoke.png`.

52. Confirm the screenshot shows the React channel workspace.

53. Stop if any deleted Jinja template renders.

54. Stop if a raw token appears outside immediate creation.

55. Stop if cross-tenant data appears.

56. Stop if private preference values appear in admin summaries.

## Expected Results

Expected: `/admin/memberships` redirects to `/admin/app/memberships`.

Expected: old membership form routes redirect after retained service behavior.

Expected: membership APIs keep masking raw email values.

Expected: raw Auth0 subjects are not visible in browser evidence.

Expected: tenant admins cannot assign platform roles.

Expected: cross-tenant membership requests fail closed.

Expected: `/admin/telegram` redirects to `/admin/app/channels`.

Expected: Telegram config, webhook, alias, token, identity, and diagnostic APIs
stay available for React.

Expected: link-token creation shows the raw token only once.

Expected: token lists show fingerprints or metadata only.

Expected: full Telegram ids and private message text are absent.

Expected: `/admin/briefing-preferences` redirects to `/admin/app/channels`.

Expected: old briefing save and import routes redirect after retained service
behavior.

Expected: old briefing export browser links redirect to React export metadata.

Expected: `/admin/briefing-preferences/api/export` remains available for
authorized API callers.

Expected: admin summaries do not show raw private preference values.

Expected: the retirement scanner proves deleted templates are absent.

## Evidence To Capture

Capture `/tmp/qa045-env-summary.txt`.

Capture `/tmp/qa045-channels-screen.png`.

Capture `/tmp/qa045-memberships-screen.png`.

Capture `/tmp/qa045-telegram-token-notes.txt`.

Capture `/tmp/qa045-briefing-screen.png`.

Capture `/tmp/qa045-legacy-redirect-notes.txt`.

Capture `/tmp/qa045-focused-backend.txt`.

Capture `/tmp/qa045-frontend-tests.txt`.

Capture `/tmp/qa045-frontend-build.txt`.

Capture QA document validator output.

Capture Spec QA output.

Capture Playwright screenshot `output/playwright/qa045_ui/qa045-react-ui2-smoke.png`.

Do not capture real secrets, real tokens, private message text, raw customer
content, or production identifiers.

## Security And Redaction Checks

Search QA evidence for `auth0|`.

Search QA evidence for `authorization`.

Search QA evidence for `bearer`.

Search QA evidence for raw Telegram ids such as long unmasked numeric ids.

Search QA evidence for raw VIP sender email values.

Search QA evidence for delegated account references.

Search QA evidence for raw link tokens after the immediate creation file.

Search QA evidence for stack traces.

Search QA evidence for local filesystem paths that should not be exported.

Confirm old routes use redirects or safe JSON errors.

Confirm deleted templates do not render.

Confirm screenshots do not show raw private payloads.

Confirm logs do not show raw link tokens.

Confirm docs do not include live credentials.

## Tenant Isolation Checks

Acme tenant id is `11111111-1111-1111-1111-111111111111`.

Globex tenant id is `22222222-2222-2222-2222-222222222222`.

Use `tenant-admin-acme` for same-tenant checks.

Use `tenant-admin-globex` for comparison only.

Acme membership routes should not expose Globex memberships.

Acme Telegram routes should not expose Globex configuration.

Acme briefing routes should not expose Globex preferences.

Platform admin can select tenant context when authorized.

Tenant users should see only user-safe briefing behavior.

Unauthorized routes should fail closed without confirming whether the target
resource exists.

Redirect query strings may preserve safe tenant ids and panel names.

Redirect query strings must not preserve raw tokens, raw messages, or private
payload values.

## Troubleshooting

If local login fails, confirm `.env` uses `AUTH_MODE=local_principal`.

If channels do not load, rebuild React with `cd frontend/admin && npm run build`.

If the API serves stale assets, restart the API after rebuilding React.

If the database contains old data, recreate only `multi_agent_platform_qa045`.

If link-token evidence fails, check whether the raw token was copied into a
persisted list or screenshot.

If a route returns a JSON validation error, that can be expected for invalid
old form data.

If a route returns a Jinja page, stop validation.

If a cross-tenant route returns data, stop validation.

If a command tries to drop a database other than `multi_agent_platform_qa045`,
stop validation.

If Playwright cannot find the channels page, open local login manually and
confirm `platform-admin` is available.
