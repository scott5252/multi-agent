# QA022 User Guide: Missing Feature 3 - Telegram Natural-Language Trigger, Delivery, And Persistence

## Detailed Overview

This guide explains the QA022 feature in plain language.
QA022 lets a tenant administrator create Telegram aliases.
An alias is a phrase or command that starts a published workflow.
The main example is `Morning briefing`.
Another example is `/briefing`.
The alias belongs to one tenant.
The alias points to one published workflow version.
The alias can require a linked Telegram identity.
Protected aliases should always require a linked identity.
The linked identity connects a Telegram user and chat to a platform identity.
The link starts with a one-time link token.
The token is shown once.
Future admin views show only a fingerprint.
When a Telegram user sends `/link TOKEN`, the platform consumes the token.
The platform stores the identity link in PostgreSQL.
The platform stores masked identity summaries for the admin console.
When the same user sends `Morning briefing`, the platform checks the link.
The platform checks the tenant Telegram configuration.
The platform checks the alias.
The platform starts the configured published workflow version.
The platform sends the final result back to the same Telegram chat.
Local QA uses a mock Bot API client.
Local QA must not call the real Telegram Bot API.
The delivery attempt is still persisted.
The persisted attempt uses safe fingerprints.
The delivery evidence does not store raw bot tokens.
The delivery evidence does not store full Telegram identifiers.
The delivery evidence does not store prompt bodies.
The delivery evidence does not store raw run payloads.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer.
Use this guide if you validate tenant Telegram setup.
Use this guide if you validate natural-language workflow triggers.
Use this guide if you validate redaction behavior.
Use this guide if you validate tenant isolation.
You do not need to understand the source code.
You should be comfortable copying commands into a terminal.
You should be comfortable opening a browser page.
You should save screenshots and command output as evidence.

## Manual QA Prerequisites

Start from a clean checkout.
Use the branch that contains QA022.
Copy `.env.qa022` to `.env`.
Install dependencies with `uv sync`.
Start PostgreSQL with Docker Compose.
Reset only the `multi_agent_platform_qa022` database.
Run Alembic migrations.
Seed the Acme and Globex tenant rows.
Start the API on `127.0.0.1:8000`.
Keep the API terminal visible while testing.
Open a second terminal for commands.
Open a browser for UI checks.
Use `tenant-admin-acme` for Acme tests.
Use `tenant-admin-globex` for isolation tests.
Use `platform-admin` only when reviewing platform-scope navigation.
Do not use real Telegram credentials.
Do not use a real personal chat.
Do not paste real bot tokens into any form.

## Step-by-Step Manual QA

1. Copy the environment file.
2. Confirm the copied file is named `.env`.
3. Confirm it uses `APP_ENV=test`.
4. Confirm it uses `AUTH_MODE=local_principal`.
5. Confirm it uses `multi_agent_platform_qa022`.
6. Confirm it uses `.data/qa022-artifacts`.
7. Confirm the secret reference is `static:qa022/telegram-provider-token`.
8. Run `uv sync`.
9. Start PostgreSQL.
10. Reset the QA database.
11. Run `uv run alembic upgrade head`.
12. Seed the Acme and Globex tenants.
13. Start the API.
14. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/telegram`.
15. Select `tenant-admin-acme`.
16. Confirm `Telegram Configuration` appears.
17. Confirm `Telegram Command Aliases` appears.
18. Confirm token references are redacted.
19. Enable tenant Telegram configuration.
20. Save the tenant configuration.
21. Confirm enabled commands are visible.
22. In the alias form, enter `Morning briefing`.
23. Enter workflow version `22222222-2222-2222-2222-222222222222`.
24. Enter description `Daily Intelligence Briefing`.
25. Keep `Protected` checked.
26. Keep `Enabled` checked.
27. Save the alias.
28. Confirm the alias row appears.
29. Confirm the alias row says linked identities are required.
30. Confirm the alias row shows the workflow version.
31. Issue a one-time link token.
32. Confirm the raw token is visible only in the immediate response.
33. Refresh the page.
34. Confirm only a fingerprint remains.
35. Use the webhook to send `/link TOKEN`.
36. Confirm the link response names `tenant-admin-acme`.
37. Return to the identity list.
38. Confirm the Telegram user is masked.
39. Confirm the Telegram chat is masked.
40. Send `Morning briefing` to the webhook.
41. Confirm the response includes an alias.
42. Confirm the response includes a run id.
43. Confirm the response says delivery succeeded.
44. Repeat the same update id.
45. Confirm the repeated response is identical.
46. Review database delivery attempts.
47. Confirm a Telegram terminal delivery attempt exists.
48. Confirm destination fingerprint is present.
49. Confirm raw chat id is absent.
50. Disable tenant Telegram configuration.
51. Send `Morning briefing` again with a new update id.
52. Confirm the response is a safe unavailable-channel message.
53. Send `Morning briefing` from an unlinked chat.
54. Confirm the response is unauthorized.
55. Sign out or return to local login.
56. Select `tenant-admin-globex`.
57. Open the Globex Telegram page.
58. Confirm Acme alias data is not shown.
59. Try to request Acme tenant id as Globex.
60. Confirm access is denied.

## Expected Results

The Acme Telegram page loads.
The alias section is visible.
The alias can be saved.
The alias is normalized as `morning briefing`.
The alias remains tenant-scoped.
The link token is one-time.
The link token audit shows only a fingerprint after refresh.
The linked identity shows masked user and chat values.
The webhook accepts `/link TOKEN`.
The webhook accepts `Morning briefing` from the linked chat.
The webhook starts one run.
The duplicate update starts no extra run.
The mock Bot API receives one message.
The message goes to the same chat id in the mocked client.
The delivery attempt is persisted.
The delivery attempt stores safe fingerprints.
The disabled-tenant check blocks alias execution.
The unlinked-chat check blocks alias execution.
The Globex principal cannot see Acme aliases.
No raw bot token appears.
No webhook secret appears.
No full Telegram user id appears.
No full Telegram chat id appears.
No raw prompt body appears.
No raw run payload appears.

## Evidence To Capture

Capture a screenshot of the local login page.
Capture a screenshot of the Acme Telegram configuration page.
Capture a screenshot of the alias table.
Capture a screenshot of the one-time token message.
Capture a screenshot after refresh showing only token fingerprints.
Capture a screenshot of masked linked identities.
Capture a screenshot of diagnostics.
Capture a screenshot of the Globex isolation view.
Save the config API response.
Save the alias API response.
Save the link token API response.
Save the `/link` webhook response.
Save the `Morning briefing` webhook response.
Save the duplicate webhook response.
Save the delivery attempt SQL output.
Save the disabled-tenant denial response.
Save the unlinked-chat denial response.
Save the redaction scan output.
Save the focused test output.
Save the full quality gate output.
Use filenames that start with `/tmp/qa022-`.

## Security And Redaction Checks

Search screenshots for `qa022-fake-token`.
Search screenshots for `local-dev-secret`.
Search screenshots for the full user id `987654321`.
Search screenshots for the full chat id `123456789`.
Search API outputs for raw token values after the one-time response.
Search diagnostics for raw provider tokens.
Search diagnostics for raw private messages.
Search delivery attempts for raw Telegram chat ids.
Search delivery attempts for raw prompt bodies.
Search database output for unauthorized tenant data.
If a raw value appears, stop review.
Record the exact file where the raw value appeared.
Do not continue until the leak is triaged.

## Tenant Isolation Checks

Use Acme to create the alias.
Use Acme to issue the link token.
Use Acme to link the Telegram identity.
Use Acme to trigger `Morning briefing`.
Use Globex to open the Telegram page.
Confirm Globex sees no Acme alias.
Use Globex to request Acme alias API data.
Confirm the response is forbidden.
Use an unlinked Telegram chat.
Confirm the alias is rejected.
Disable Acme Telegram configuration.
Confirm the alias is rejected even for the linked chat.
Re-enable only when continuing positive-path tests.

## Troubleshooting

If the login page is missing, confirm the API is running.
If the Acme principal is missing, confirm `.env.qa022` was copied.
If the database connection fails, restart PostgreSQL.
If migrations fail, reset only `multi_agent_platform_qa022`.
If the alias form rejects the workflow version, confirm it is a valid UUID.
If the stale revision error appears, refresh the page.
If `/link` fails, issue a fresh token.
If `Morning briefing` is missing input, confirm the alias is enabled.
If `Morning briefing` is unavailable, confirm tenant Telegram is enabled.
If duplicate replay differs, inspect `telegram_update_receipts`.
If no delivery attempt appears, inspect API logs for the trace id.
If the UI shows raw secrets, stop review and file a security defect.
If Playwright fails, verify `http://127.0.0.1:8000` is reachable.

## Related Files

- `specs/022-telegram-natural-language-trigger-delivery-persistence/spec.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/plan.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/tasks.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022_ui.md`
- `specs/022-telegram-natural-language-trigger-delivery-persistence/testing-instructions.md`
- `src/multi_agent_platform/channels/telegram.py`
- `src/multi_agent_platform/channels/telegram_delivery.py`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `tests/integration/api/test_telegram_webhook.py`
