# QA025 UI Walkthrough: Live Model Credential Resolution For Gateway Calls

## Purpose

Use this browser walkthrough to verify the visible provider configuration and
diagnostic surfaces for QA025.

## Start

1. Copy `.env.qa025` to `.env`.
2. Start PostgreSQL and run migrations.
3. Start the API server.
4. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/model-providers`.
5. Sign in as `platform-admin`.

## Provider List

Expected:

- The page title is `Model Providers`.
- Existing provider rows show display name, type, health, model count, and safe status.
- No raw credential value appears.

## Create OpenAI Provider

Open the create page.

Use:

- Provider type: `openai`
- Display name: `QA025 OpenAI`
- Model ids: `gpt-test`
- Credential secret references: `qa025/openai-placeholder`
- Active: enabled

Save the form.

Expected:

- The detail page shows the safe reference id.
- The detail page does not show any raw credential value.
- The connection is active and initially untested unless a probe has run.

## Test OpenAI Provider

Run the provider test action.

Expected:

- If the local test harness uses a mocked adapter, the result can succeed.
- If no mocked provider endpoint exists, the result may show a normalized provider failure.
- A missing or unresolved reference must show a safe credential failure.
- The diagnostic text does not show authorization headers.
- The diagnostic text does not show raw credential values.

## Create Local Provider Without Credentials

Open the create page again.

Use:

- Provider type: `local_openai_compatible`
- Display name: `QA025 Local`
- Base URL: `http://localhost:11434`
- Model ids: `local-test`
- Credential secret references: empty
- Active: enabled

Save the form.

Expected:

- The form saves because the local endpoint is allowlisted.
- The detail page shows no credential reference.
- The page does not warn about a missing credential for the local no-auth case.

## Unsafe Local Provider Check

Try a local provider URL with userinfo or a secret-like query string.

Expected:

- Save is rejected.
- The error message is safe.
- The rejected URL secret-like pieces are not reflected back in the page body.

## Tenant Visibility Check

Sign out or open a new session.

Sign in as `tenant-admin-acme`.

Open `/admin/model-providers`.

Expected:

- Tenant users can see only provider rows visible to their tenant.
- Tenant users cannot create, edit, activate, deactivate, test, or sync provider connections.

Sign in as `tenant-admin-globex`.

Expected:

- Globex cannot see Acme-only provider rows.
- No denied row leaks credential references or raw credential values.

## Screenshot Evidence

Capture:

- Provider list.
- OpenAI detail page with safe reference id.
- Local no-auth detail page.
- Safe failure state for missing credential reference if tested.
- Tenant denied or limited visibility state.

Do not capture raw values from `.env.qa025`.

## Completion

Run the redaction scan from `qa025.md` after screenshots are saved.
