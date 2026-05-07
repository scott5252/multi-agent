# QA046 User Guide: Spec 046 - User-Facing Run UI React Port And Jinja Removal

## Detailed Overview

QA046 moves the user-facing workflow run browser experience away from old server-rendered pages and into the React run workspace. The old addresses still work, but they now redirect safely. `/runs` and `/runs/new` open the React start workspace. `/runs/{run_id}` opens the React detail workspace after the backend confirms the signed-in user can see that run.
The browser does not own authorization, tenant scoping, approval state, artifacts, or callback behavior. It calls the retained `/runs` JSON APIs and shows safe summaries returned by the backend.
This guide is written for reviewers who need to know what to click, what to expect, and what evidence to capture.

## Who Should Use This Guide

- Manual QA reviewers checking React migration evidence.
- Product reviewers confirming that old run links still work.
- Security reviewers checking tenant isolation and redaction.
- Engineers performing a final sanity pass before Spec 047 removes global template infrastructure.

## Manual QA Prerequisites

- A local checkout of the repository.
- Docker available for PostgreSQL.
- The QA environment file `specs/046-user-facing-run-ui-react-port-and-jinja-removal/.env.qa046`.
- Built React admin assets.
- A browser that can open `http://127.0.0.1:8000/auth/local-login`.

## Step-by-Step Manual QA
1. Copy `.env.qa046` to `.env`, run migrations, and start the API and worker.
2. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/runs`.
3. Choose `tenant-admin-acme` from the local-principal login page.
4. Confirm the route becomes `/admin/app/channels/runs`.
5. Confirm the page heading is `Run workspace`.
6. Click `Start Run` with the default safe workflow and request summary.
7. Confirm the route changes to `/admin/app/channels/runs/{run_id}`.
8. Confirm the status card says `Run accepted through channel facade.`.
9. Review the timeline list and confirm only safe event summaries are visible.
10. Review the actions list and confirm controls are enabled or disabled by backend state.
11. Click `Subscribe` and confirm only the subscription status is shown.
12. Click `Register Callback` and confirm no callback URL or secret is echoed.
13. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
14. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
15. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
16. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
17. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
18. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
19. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
20. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
21. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
22. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
23. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
24. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
25. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
26. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
27. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
28. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
29. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
30. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
31. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
32. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
33. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
34. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
35. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
36. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
37. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
38. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
39. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
40. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
41. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
42. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
43. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
44. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
45. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
46. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
47. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
48. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
49. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
50. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
51. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
52. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
53. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
54. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
55. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
56. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
57. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
58. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
59. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
60. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
61. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
62. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
63. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
64. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
65. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
66. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
67. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
68. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
69. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.
70. Continue reviewing the visible run workspace and record whether the React page keeps safe summaries only.

## Expected Results

- Expected: QA046 result 1 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 2 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 3 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 4 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 5 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 6 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 7 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 8 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 9 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 10 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 11 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 12 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 13 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 14 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 15 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 16 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 17 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 18 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 19 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 20 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 21 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 22 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 23 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 24 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 25 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 26 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 27 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.
- Expected: QA046 result 28 confirms React-only run behavior, safe backend-owned data, or deletion-grade Jinja evidence.

## Evidence To Capture

- Screenshot of `/admin/app/channels/runs`.
- Screenshot of `/admin/app/channels/runs/{run_id}` after starting a run.
- Reviewer note for `/runs` redirect behavior.
- Reviewer note for `/runs/{run_id}` redirect behavior.
- Browser-visible run id and trace reference.
- Output path `output/playwright/qa046_ui/qa046-react-ui2-smoke.png`.

## Security And Redaction Checks

- Confirm no raw prompt text is visible.
- Confirm no raw run payload is visible.
- Confirm no callback secret or full callback details are visible.
- Confirm no local filesystem path is visible.
- Confirm no stack trace is visible.
- Confirm no cross-tenant label appears when testing a denied run.

## Tenant Isolation Checks

- Use `tenant-admin-acme` to create a run.
- Use `tenant-admin-globex` with the same run id through curl status checks.
- Expected: Globex receives a safe unavailable or not-found response.
- Expected: Acme labels or data are not revealed to Globex.

## Troubleshooting

- If login fails, confirm `.env.qa046` is loaded.
- If React assets are missing, run `cd frontend/admin && npm run build`.
- If the route opens the old console, confirm `/runs` redirects to `/admin/app/channels/runs`.
- If a raw payload appears, stop and record it as a security regression.
- If a test fails only because the in-memory run disappeared, recreate the QA run and repeat the browser step.
- Reviewer note 158: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 159: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 160: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 161: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 162: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 163: Expected: qa046 remains React-only and redaction-safe.
- Reviewer note 164: Expected: qa046 remains React-only and redaction-safe.
