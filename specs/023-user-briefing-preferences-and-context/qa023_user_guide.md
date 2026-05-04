# QA023 User Guide: Missing Feature 4 - User Briefing Preferences And Context

## Detailed Overview

This guide helps a non-developer reviewer validate the User Briefing
Preferences And Context feature.

The feature lets an authorized tenant user save the information needed to make
a Daily Intelligence Briefing personal and useful.

The profile includes location, timezone, news topics, VIP sender hints, workday
hours, commute mode, calendar account reference, email account reference,
output style, and optional scheduled briefing time.

The feature also gives admins a safe way to inspect whether profiles are ready.

Admin summaries must never show raw credentials, raw account identifiers, or
private VIP sender values.

Runtime code can resolve the latest profile by tenant and principal id.

When a Telegram user triggers `Morning briefing`, the runtime can attach the
resolved preference context to the run input.

Each saved profile update creates an immutable revision.

The current profile is stored as a head projection for fast lookup.

The resolver returns the revision id and content digest so future runs can prove
which preference version they used.

The QA environment uses fake local credentials and local principals.

Do not use real Gmail, Calendar, Telegram, news, weather, maps, or provider
credentials for this guide.

## Who Should Use This Guide

Use this guide if you are reviewing the browser behavior.

Use this guide if you are checking API evidence for a pull request.

Use this guide if you need to confirm tenant isolation between Acme and Globex.

Use this guide if you need to confirm redaction on admin summary pages.

Use this guide if you need to confirm runtime preference resolution.

You do not need to know Python to complete the manual browser checks.

You should be comfortable copying commands into a terminal.

Ask an engineer for help if Docker, PostgreSQL, or dependency installation
fails before the app starts.

## Manual QA Prerequisites

1. Open a terminal at the repository root.

2. Confirm you are in `multi-agent`.

3. Copy the QA environment file:

```bash
cp specs/023-user-briefing-preferences-and-context/.env.qa023 .env
```

4. Confirm `.env` references `multi_agent_platform_qa023`.

5. Confirm `.env` has `AUTH_MODE=local_principal`.

6. Confirm `.env` contains `tenant-admin-acme`.

7. Confirm `.env` contains `tenant-admin-globex`.

8. Confirm `.env` contains `platform-admin`.

9. Confirm no real credential values are present.

10. Install dependencies:

```bash
uv sync
```

11. Start PostgreSQL:

```bash
docker compose up -d postgres
```

12. Reset the QA database:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa023 && createdb -U postgres multi_agent_platform_qa023'
```

13. Apply migrations:

```bash
uv run alembic upgrade head
```

14. Seed Acme and Globex:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa023 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING;"
```

15. Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

16. Keep the API terminal open.

17. Open a second terminal for curl checks.

18. Open a browser for UI checks.

## Step-by-Step Manual QA

1. Navigate to `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/briefing-preferences`.

2. Confirm the page shows `Local Login`.

3. Capture a screenshot named `qa023-01-local-login.png`.

4. Select `tenant-admin-acme`.

5. Confirm the browser lands on `Briefing Preferences`.

6. Confirm the admin shell navigation is visible.

7. Confirm the page includes a profile form.

8. In `Location`, enter `Providence, RI`.

9. In `Timezone`, enter `America/New_York`.

10. In `News topics`, enter `AI, markets, product launches`.

11. In `VIP senders`, enter `sarah@example.com, legal@example.com`.

12. In `Workday start`, enter `09:00`.

13. In `Workday end`, enter `17:30`.

14. Select `driving` for commute mode.

15. In `Calendar ref`, enter `delegated:calendar:primary`.

16. In `Email ref`, enter `delegated:gmail:primary`.

17. Select `standard` for style.

18. Check `Scheduled`.

19. In `Scheduled time`, enter `08:00`.

20. Click `Save profile`.

21. Confirm the page redirects back to the Acme scoped page.

22. Confirm the saved values appear in the form.

23. Capture a screenshot named `qa023-02-profile-saved.png`.

24. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111`.

25. Select `platform-admin`.

26. Confirm the platform admin can see `Safe Admin Summaries`.

27. Confirm the summary shows `tenant-admin-acme`.

28. Confirm the summary shows `America/New_York`.

29. Confirm the summary shows a topic count.

30. Confirm the summary shows a VIP count.

31. Confirm the summary shows `s***@example.com`.

32. Confirm the summary shows `delegated:***`.

33. Confirm the summary does not show `delegated:calendar:primary`.

34. Confirm the summary does not show `delegated:gmail:primary`.

35. Confirm the summary does not show `legal@example.com`.

36. Capture a screenshot named `qa023-03-safe-summary.png`.

37. Sign in as `tenant-admin-globex`.

38. Try to open the Acme scoped URL directly.

39. Confirm the request is denied or shows a safe blocked state.

40. Capture a screenshot named `qa023-04-cross-tenant-denied.png`.

41. Return to a terminal.

42. Save the profile through the API if the browser save was skipped.

43. Run:

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/briefing-preferences/api/profile?tenant_id=11111111-1111-1111-1111-111111111111'
```

44. Confirm the profile response contains `revision_token`.

45. Confirm the profile response contains `current_revision_id`.

46. Confirm the profile response contains `content_digest`.

47. Run the safe summary API.

48. Confirm the summary response masks VIP senders.

49. Confirm the summary response masks account references.

50. Run the runtime resolve API.

51. Confirm `available` is true.

52. Confirm the resolver returns the same timezone.

53. Confirm the resolver returns a revision id.

54. Confirm the resolver returns a content digest.

55. Confirm the resolver returns safe summary metadata.

56. Export the profile JSON.

57. Confirm the export belongs to Acme.

58. Confirm the export belongs to `tenant-admin-acme`.

59. Try to import the same JSON after changing the principal id.

60. Confirm the import is rejected.

## Expected Results

The Acme tenant admin can save a complete profile.

The saved profile survives page reload.

Every save produces a new revision token.

The profile response includes a revision id and digest.

The platform admin summary shows safe profile readiness evidence.

The platform admin summary does not reveal raw account references.

The platform admin summary does not reveal raw VIP sender values.

The Globex tenant admin cannot read Acme profile data.

The runtime resolver returns the latest Acme profile for the Acme principal.

The runtime resolver returns no private data for a missing profile.

Invalid timezones are rejected.

Invalid workday hours are rejected.

Credential-looking account values are rejected.

## Evidence To Capture

Save a screenshot of the local login page.

Save a screenshot after the Acme profile is saved.

Save a screenshot of the platform admin safe summary.

Save a screenshot or note for the Globex denial.

Save `/tmp/qa023-profile.json` if using curl.

Save `/tmp/qa023-summaries.json` if using curl.

Save `/tmp/qa023-resolve.json` if using curl.

Save terminal output for the focused automated tests.

Save terminal output for Ruff, mypy, and pytest coverage gates.

Record the exact date of validation.

Record the branch name under review.

## Security And Redaction Checks

Check that no real provider credentials appear in `.env.qa023`.

Check that `sarah@example.com` is not visible in platform admin summaries.

Check that `legal@example.com` is not visible in platform admin summaries.

Check that `delegated:calendar:primary` is not visible in platform admin summaries.

Check that `delegated:gmail:primary` is not visible in platform admin summaries.

Check that safe summaries show `delegated:***`.

Check that safe summaries show masked sender evidence.

Check that denied requests do not reveal whether another tenant has a profile.

Check that runtime missing results have no `preferences` object.

Check that audit metadata is redaction safe.

## Tenant Isolation Checks

Acme tenant id is `11111111-1111-1111-1111-111111111111`.

Globex tenant id is `22222222-2222-2222-2222-222222222222`.

Acme admin may save Acme preferences.

Globex admin may save Globex preferences.

Acme admin must not read Globex preferences.

Globex admin must not read Acme preferences.

Platform admin may inspect safe summaries for authorized tenant scopes.

Platform admin summary inspection must not reveal raw private values.

Import documents must match the authenticated tenant.

Import documents must match the authenticated principal.

Runtime resolution must use both tenant id and principal id.

## Troubleshooting

If local login is missing, confirm the API is running on port 8000.

If the page says unauthorized, confirm the selected local principal has briefing
preference permissions.

If the tenant scope is missing, reseed the Acme and Globex tenant rows.

If profile save fails, check the timezone spelling.

If profile save fails, check that workday start is before workday end.

If profile save fails, check that scheduled time uses `HH:MM`.

If profile save fails, check account references use allowed prefixes.

If summary rows are empty, confirm the Acme profile was saved first.

If Globex can read Acme data, stop the review and report a tenant isolation bug.

If raw account references appear in admin summaries, stop the review and report
a redaction bug.

If raw VIP senders appear in admin summaries, stop the review and report a
redaction bug.

If QA scripts cannot start PostgreSQL, confirm Docker is running.

If migrations fail, verify `.env` points to `multi_agent_platform_qa023`.

If tests fail, attach the failing command and output to the review notes.
