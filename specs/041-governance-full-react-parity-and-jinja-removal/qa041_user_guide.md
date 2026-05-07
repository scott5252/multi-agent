# QA041 User Guide: Spec 041 - Governance Full React Parity And Jinja Removal

## Detailed Overview

Spec 041 changes where governance reviewers do their browser work.

Before this change, provider governance, prompt governance, runtime profile governance, and model-skill configuration had several server-rendered browser pages.

After this change, reviewers use the React admin workspace at `/admin/app/governance`.

The old browser URLs still exist as compatibility entries.

They redirect to React destinations instead of rendering old governance templates.

This matters because the project is retiring Jinja browser surfaces in controlled slices.

Spec 041 only removes governance-owned templates.

It does not remove shared Jinja infrastructure.

It does not remove unrelated admin pages.

It does not change the backend services that enforce tenant scope, role checks, credential safety, provider probe policy, prompt preview safety, profile resolution, routing preview, or audit summaries.

The React page is a reviewer workspace.

It shows provider readiness.

It shows credential reference readiness.

It shows direct-call guardrail evidence.

It shows prompt status and safe preview evidence.

It shows runtime profile resolution.

It shows model-skill routing preview.

It shows policy history.

It shows run provenance.

It shows a legacy route redirect ledger.

The goal of manual QA is to prove that reviewers can still perform these tasks after the old governance templates are gone.

The second goal is to prove the new route behavior is safe.

Old links should redirect.

Unauthorized users should not learn private data from old direct links.

Tenant users should not see another tenant's data.

No screenshot or log should include a raw secret, credential value, raw prompt, raw completion, raw provider payload, memory content, stack trace, local filesystem path, or unauthorized tenant label.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer.

Use it if you need plain-language steps rather than source-code details.

Use it if you are validating screenshots for a release review.

Use it if you are checking old bookmarks and direct links.

Use it if you are checking tenant and platform role behavior.

Use it if you are checking security and redaction expectations.

You do not need to understand FastAPI, React, SQLAlchemy, or Vite to complete the browser walkthrough.

You do need access to the local repository checkout.

You do need the ability to run the local API.

You do need the ability to select local-principal users from the login page.

## Manual QA Prerequisites

Start from the repository root.

Copy the QA environment file to `.env`.

Run `uv sync`.

Start PostgreSQL with Docker.

Reset only the database named `multi_agent_platform_qa041`.

Run Alembic migrations.

Seed the Acme and Globex tenants.

Build the React admin assets.

Start the FastAPI server.

Start the worker process.

Create the evidence directories.

Use `AUTH_MODE=local_principal`.

Use `platform-admin` first.

Use `tenant-admin-acme` second.

Use `tenant-admin-globex` for the cross-tenant check.

Keep screenshots under `output/playwright/qa041_ui`.

Keep notes under `/tmp/qa041-ui-notes.md`.

Do not use live providers.

Do not use real credentials.

Do not paste private prompt text.

Do not attach evidence that contains unsafe data.

Expected setup commands are documented in `qa041.md` and `qa041_ui.md`.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance`.

2. Select `platform-admin`.

3. Confirm the browser lands on `/admin/app/governance`.

4. Confirm the page title says `Governance`.

5. Confirm the page is visibly a React admin workspace.

6. Capture the landing page screenshot.

7. Review the setup summary.

8. Confirm the summary mentions safe provider, prompt, profile, routing, or provenance readiness.

9. Review provider cards.

10. Confirm provider health is summarized.

11. Confirm credential references show fingerprints or labels only.

12. Confirm no credential value is visible.

13. Confirm direct-call guardrail text is visible.

14. Run the provider probe if the button is enabled.

15. Confirm the result is a safe diagnostic.

16. Review prompt cards.

17. Confirm prompt status and render-test status are visible.

18. Run the prompt preview action.

19. Confirm the preview is summarized.

20. Confirm no raw prompt body is visible.

21. Confirm no raw completion is visible.

22. Review runtime profile cards.

23. Confirm model binding, provider binding, prompt binding, and skill requirements are visible as summaries.

24. Run profile resolution.

25. Confirm selected profile version and policy reasons are visible.

26. Confirm no raw runtime payload is visible.

27. Run routing preview.

28. Confirm model decision, provider decision, skill decision, credential reference status, and direct-call guardrail are visible.

29. Confirm the preview does not make a live provider call.

30. Review policy history.

31. Confirm history rows include actor label, scope label, outcome, safe diff, and audit reference.

32. Review run provenance.

33. Confirm provider, model, prompt, profile, routing, credential, usage, and audit evidence are safe summaries.

34. Review the legacy route redirects section.

35. Confirm old path, React path, compatibility status, authorization behavior, and evidence summary are shown.

36. Open `/admin/model-providers`.

37. Confirm it redirects to `/admin/app/governance/providers`.

38. Open `/admin/prompt-runtime/prompts`.

39. Confirm it redirects to `/admin/app/governance/prompts`.

40. Open `/admin/prompt-runtime/profiles`.

41. Confirm it redirects to `/admin/app/governance/profiles`.

42. Open `/admin/config/ui/history`.

43. Confirm it redirects to `/admin/app/governance/history`.

44. Sign out or return to local login.

45. Select `tenant-admin-acme`.

46. Open `/admin/app/governance`.

47. Confirm Acme governance content loads.

48. Confirm platform-only provider mutation controls are absent or disabled.

49. Confirm tenant read-only governance summaries remain visible.

50. Return to local login.

51. Select `tenant-admin-globex`.

52. Attempt to open an Acme-scoped governance URL with the Acme tenant id.

53. Confirm the response is denied or safely scoped.

54. Review screenshots and notes.

55. Run the redaction scan from `qa041.md`.

56. Attach only safe screenshots and notes.

## Expected Results

The React governance page loads for platform admin.

The React governance page loads for Acme tenant admin with tenant-safe behavior.

Old provider routes redirect to React provider routes.

Old prompt routes redirect to React prompt routes.

Old profile routes redirect to React profile routes.

Old model-skill config routes redirect to React governance routing, history, or provenance routes.

The legacy redirect ledger is visible in React.

Provider mutation remains platform-admin only.

Tenant-admin users can review authorized summaries.

Cross-tenant access fails closed.

Prompt preview uses safe fixture output.

Profile resolution uses safe policy summaries.

Routing preview is read-only.

Run provenance shows evidence summaries only.

Deleted governance templates are not needed for the browser walkthrough.

No screenshot contains raw secrets.

No screenshot contains raw prompt text.

No screenshot contains raw completion text.

No screenshot contains raw provider payloads.

No screenshot contains stack traces.

No screenshot contains local filesystem paths.

## Evidence To Capture

Capture the governance landing page.

Capture provider readiness and credential reference summaries.

Capture prompt preview results.

Capture runtime profile resolution.

Capture routing preview results.

Capture policy history.

Capture run provenance.

Capture the legacy redirect ledger.

Record the old provider redirect.

Record the old prompt redirect.

Record the old profile redirect.

Record the old model-skill history redirect.

Record tenant-admin provider controls.

Record cross-tenant denial or safe scoping.

Record the final redaction scan result.

Record focused backend test results.

Record focused frontend test results.

Record Playwright screenshot paths.

## Security And Redaction Checks

Look for raw secret values.

Look for provider authorization headers.

Look for raw prompt bodies.

Look for raw completions.

Look for raw provider request payloads.

Look for raw provider response payloads.

Look for private channel messages.

Look for memory contents.

Look for raw external tool payloads.

Look for stack traces.

Look for local filesystem paths.

Look for unauthorized tenant labels.

If any of these appear, stop QA.

Do not attach the unsafe evidence.

File the issue as a redaction blocker.

## Tenant Isolation Checks

Use `tenant-admin-acme` to view Acme governance content.

Use `tenant-admin-globex` to attempt an Acme-scoped URL.

Confirm Globex cannot see Acme-specific governance data.

Confirm the response does not disclose whether private Acme records exist.

Confirm old direct links behave the same way as React JSON routes.

Confirm safe query parameters are preserved only when authorized.

Confirm provider platform mutation controls do not appear for tenant admin.

Confirm tenant users cannot create or edit provider connections.

Confirm prompt and profile summaries stay scoped to the authorized tenant.

## Troubleshooting

If the login page is missing principals, `.env.qa041` may not be copied to `.env`.

If the governance page loads stale JavaScript, run the React build again.

If the API is unavailable, inspect `/tmp/qa041-ui/api.log`.

If the worker is unavailable, inspect `/tmp/qa041-ui/worker.log`.

If old URLs return `404`, confirm the server restarted after the route changes.

If old URLs render old pages, the deleted templates or route handlers were restored.

If provider probe output looks live, stop QA and inspect the environment flags.

If tenant switching is confusing, clear the `map_local_principal` cookie and sign in again.

If Playwright fails at login, confirm `AUTH_MODE=local_principal`.

If evidence contains unsafe text, do not attach it.

If you cannot determine whether a behavior is expected, compare with `qa041.md`, `qa041_ui.md`, and `pr_notes.md`.
