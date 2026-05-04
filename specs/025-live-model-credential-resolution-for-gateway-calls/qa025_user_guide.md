# QA025 User Guide: Missing Feature 6 - Live Model Credential Resolution For Gateway Calls

## Detailed Overview

This guide explains QA025 in plain language for manual reviewers.

QA025 protects model provider credentials.

The platform lets administrators configure model providers.

A provider can be OpenAI.

A provider can be a local OpenAI-compatible endpoint.

Provider records should never store raw credentials.

Provider records should store safe secret reference ids.

A secret reference id is a label.

The real value lives in the configured secret provider.

The application should resolve the value only when it is about to call a provider.

That call-time behavior is the main point of QA025.

Before QA025, some probe and gateway paths could ignore configured references.

That made provider health less trustworthy.

It also risked moving credential behavior into the wrong layer.

QA025 makes probes use the same secret provider boundary as runtime calls.

QA025 makes runtime gateway calls use the same boundary.

QA025 also checks safe failure evidence.

If a credential is missing, the system should fail clearly.

It should not make a provider call with an empty key.

It should not expose a raw value.

It should not show authorization headers.

It should not store provider request bodies.

The safe failure category is `secret_reference_invalid`.

OpenAI providers require a credential reference.

Local OpenAI-compatible providers can be no-auth in local QA.

That no-auth behavior is allowed only for allowlisted local endpoints.

If a local provider does have a reference, the reference should resolve at call time.

The resolved value is passed only to the adapter request.

The resolved value should disappear after the call.

Reviewers do not need to know the internal Python classes.

Focus on records, screens, test results, and redaction.

The provider admin page is the main browser surface.

The gateway tests are the main runtime evidence.

The QA environment uses fake static secrets.

Do not use real OpenAI credentials.

Do not use production endpoints.

Do not paste raw credentials into forms.

## Who Should Use This Guide

Use this guide if you are a QA reviewer.

Use this guide if you are a product reviewer.

Use this guide if you are checking a pull request.

Use this guide if you need browser screenshots.

Use this guide if you are not comfortable reading Python source.

Use this guide if you want to verify redaction behavior.

Developers can also use this guide as a manual smoke test.

Security reviewers should focus on the redaction sections.

Operations reviewers should focus on diagnostic outcomes.

Tenant-isolation reviewers should focus on visible provider rows.

The companion `qa025.md` includes command-line checks.

The companion `qa025_ui.md` includes a shorter browser flow.

The companion `testing-instructions.md` lists automated tests.

## Manual QA Prerequisites

You need the repository checkout.

You need Docker available.

You need the `uv` command.

You need a browser.

You need permission to run local shell commands.

You do not need Auth0 credentials.

You do not need real OpenAI credentials.

You do not need a real local model server.

You do not need Telegram credentials.

You do not need customer data.

Use the file `.env.qa025`.

Use the database `multi_agent_platform_qa025`.

Use fake `qa025/` references only.

Start from the repository root.

Back up any existing `.env` file.

Copy the QA025 environment file into `.env`.

Install dependencies with `uv sync`.

Start PostgreSQL with Docker Compose.

Reset the QA database.

Apply migrations.

Seed Acme and Globex tenants.

Start the API server.

Keep the API server running.

Start the worker in another terminal if you are also checking runtime pages.

## Step-by-Step Manual QA

Step 1: Open the local login page.

Use `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/model-providers`.

Step 2: Sign in as `platform-admin`.

You should land on the Model Providers page.

Step 3: Create an OpenAI provider.

Use provider type `openai`.

Use display name `QA025 OpenAI`.

Use model id `gpt-test`.

Use credential reference `qa025/openai-placeholder`.

Set the provider active.

Save the form.

Step 4: Review the detail page.

The safe reference id should be visible.

No raw credential value should be visible.

The page should show provider type and model id.

Step 5: Run the provider test action.

The result should be safe.

A mocked success is acceptable.

A normalized provider failure is acceptable when no mock server is present.

A raw credential value is never acceptable.

Step 6: Create a local provider.

Use provider type `local_openai_compatible`.

Use display name `QA025 Local`.

Use base URL `http://localhost:11434`.

Use model id `local-test`.

Leave credential references empty.

Set the provider active.

Save the form.

Step 7: Review the local provider detail page.

The local endpoint should be shown safely.

The credential reference area should be empty.

The page should not show a missing-credential error for this no-auth local case.

Step 8: Try an unsafe local endpoint.

Use a URL with userinfo or a secret-like query string.

Save should fail.

The error should be safe.

The unsafe pieces should not be reflected into the page.

Step 9: Check tenant visibility.

Sign in as `tenant-admin-acme`.

Open the Model Providers page.

Confirm the tenant can only see allowed rows.

Confirm tenant users cannot create or test providers.

Sign in as `tenant-admin-globex`.

Confirm Globex cannot see Acme-only rows.

Step 10: Run automated focused tests.

Use the focused command in `qa025.md`.

All tests should pass.

Step 11: Run the redaction scan.

Use the redaction command in `qa025.md`.

There should be no matches outside intentional env or test fixtures.

Step 12: Run full quality gates if you are approving the PR.

Run Ruff.

Run format check.

Run mypy.

Run full pytest coverage.

## Expected Results

OpenAI provider records store references only.

OpenAI probes use the configured secret provider at call time.

OpenAI runtime gateway calls use the configured secret provider at call time.

OpenAI missing credentials fail before provider calls.

Missing credentials use `secret_reference_invalid`.

Unresolved credentials use `secret_reference_invalid`.

Empty resolved credentials use `secret_reference_invalid`.

Local no-auth provider setup works for allowlisted local endpoints.

Local providers with references resolve those references at call time.

Provider test evidence is safe.

Gateway attempt evidence is safe.

Gateway operation evidence is safe.

Physical attempt evidence is safe.

Retry and breaker summaries are still present.

Usage evidence does not contain raw credentials.

Admin pages do not render raw credentials.

JSON APIs do not return raw credentials.

Logs do not contain raw credentials.

README and quickstart docs do not contain raw credentials.

Screenshots do not contain raw credentials.

## Evidence To Capture

Capture the Model Providers list.

Capture the OpenAI provider detail page.

Capture the safe reference id on the detail page.

Capture the provider test result area.

Capture the local provider detail page with empty credential references.

Capture the unsafe local endpoint rejection if tested.

Capture tenant-limited visibility for Acme.

Capture tenant-limited visibility for Globex if relevant.

Save focused test output.

Save redaction scan output.

Save full quality gate output when available.

Do not capture raw values from `.env.qa025`.

Do not paste raw values into notes.

## Security And Redaction Checks

Check provider forms.

Check provider detail pages.

Check provider test result text.

Check JSON responses if you use API tools.

Check terminal logs.

Check screenshots.

Check QA artifacts.

Check README and quickstart text.

Raw credentials should not appear.

Authorization headers should not appear.

Provider request bodies should not appear.

Provider response bodies should not appear.

Raw prompts should not appear.

Raw completions should not appear.

Safe reference ids may appear.

Provider connection ids may appear.

Model ids may appear.

Tenant ids may appear.

Trace ids may appear.

Normalized categories may appear.

## Tenant Isolation Checks

Platform administrators can manage provider connections.

Tenant administrators cannot mutate provider connections.

Tenant users can see only visible provider rows.

Acme-only rows should not appear to Globex.

Globex-only rows should not appear to Acme.

Denied rows should not leak credential references unless the row is visible.

Denied rows should never leak raw credential values.

Runtime gateway evidence should keep the tenant id from the invocation context.

Retry and breaker summaries should not cross tenant scopes.

## Troubleshooting

If login fails, use the local login page again.

If the Model Providers page is denied, confirm you are `platform-admin`.

If migrations fail, reset only the QA025 database.

If Docker is unavailable, start PostgreSQL another way and update `.env`.

If a provider probe fails with a provider error, that can be acceptable without a mock server.

If a provider probe fails with `secret_reference_invalid`, check the reference id.

If a local provider URL is rejected, confirm it uses an allowlisted host and port.

If the redaction scan finds a raw value in docs or logs, stop and report a failure.

If the redaction scan finds a raw value only in `.env.qa025`, that is expected.

If tests fail, collect the failing test name and output.

If full coverage fails, collect the coverage summary.

If screenshots show raw credentials, delete them from evidence and report the issue.
