# QA011 UI Guide: Model Provider Gateway

## Purpose

Use this guide to review the Spec 011 Web UI from the shared admin shell. It
explains what each page does, what fields mean, and how to verify that the new
model provider features are understandable to a platform administrator.

## Entry Point

Open:

```text
http://127.0.0.1:8000/admin/model-providers
```

Use local-principal `platform-admin` for mutation flows. Use
`tenant-admin-acme` or `tenant-admin-globex` for read-only visibility checks.

## Navigation

The shared admin shell has a **Model Providers** item under **Model And Skill
Config**. The item opens the provider list and preserves active tenant scope
when the shell is in tenant mode.

Expected behavior:

- Platform admins can see the list, create button, catalog link, detail pages,
  edit pages, activation controls, test controls, and sync controls.
- Tenant admins can see only visible provider metadata and catalog entries.
- Tenant admins do not see working mutation controls.

## Provider List

The list page shows operational columns a reviewer needs before opening a row:

- Display name.
- Provider type.
- Active state.
- Health state.
- Last test outcome.
- Model count.
- Tenant visibility summary.
- Catalog sync status.
- Updated timestamp.

Use the filter strip to narrow by provider type, health state, and model id.
An empty state must avoid revealing whether hidden cross-tenant providers exist.

## Create Provider

Open **New provider** as a platform administrator.

The form covers:

- Display name.
- Provider type: `openai` or `local_openai_compatible`.
- Base URL for local providers.
- Secret reference ids.
- Active checkbox.
- Model ids.
- Timeout policy: connect, read, and total seconds.
- Tenant visibility: platform default or tenant allowlist.
- Tenant ids for allowlist visibility.

For OpenAI:

- Use `openai`.
- Leave base URL empty unless reviewing an explicit safe override.
- Enter one or more model ids.
- Use a secret reference such as `qa011/openai-placeholder`.

For local providers:

- Use `local_openai_compatible`.
- Enter an allowlisted URL such as `http://127.0.0.1:11434`.
- Enter one or more local model ids.
- Use a secret reference such as `qa011/local-placeholder`.

## Edit Provider

Open a detail page, then choose **Edit**.

The edit form should preserve safe values:

- Display name.
- Provider type.
- Safe base URL.
- Secret reference ids only.
- Active state.
- Model ids.
- Timeout policy.
- Visibility mode.

Secret values must never appear. Only reference ids are acceptable.

## Detail Page

The detail page is the main operations surface. It shows:

- Provider type.
- Active state.
- Health state.
- Visibility mode.
- Safe base URL or default endpoint.
- Model definitions.
- Latest test result.
- Tenant visibility entries.
- Activate, deactivate, run test, and sync catalog actions for platform admins.

Reviewers should confirm that latest-test diagnostics are safe summaries, not
raw provider responses.

## Test Action

Use **Run test** on a configured connection.

Expected behavior:

- The action is available only for platform admins.
- The UI disables the action while the request runs when JavaScript is enabled.
- The response shows outcome, normalized reason, latency, tested model, and
  safe diagnostic summary.
- Failures are actionable categories such as authorization failure, timeout,
  rate limit, provider unavailable, invalid model, malformed response, or
  policy denial.

## Catalog Sync Action

Use **Sync catalog** after a connection is healthy.

Expected behavior:

- Healthy active models become gateway-governed catalog entries.
- Inactive or unhealthy entries are marked unavailable rather than deleted.
- Collision warnings must identify only model id and tenant scope.
- No credential, prompt, completion, token, or endpoint secret appears.

## Catalog Page

Open:

```text
http://127.0.0.1:8000/admin/model-providers/catalog
```

The catalog page explains routing readiness with:

- Tenant scope.
- Provider type.
- Model id.
- Health state.
- Availability.
- Selectability.
- Governing connection.

Only healthy, active, tenant-visible, gateway-governed entries are selectable.

## Tenant Visibility Check

Switch to `tenant-admin-acme`.

Expected behavior:

- Acme sees platform-default provider rows.
- Acme sees allowlisted Acme rows.
- Acme cannot see Globex-only rows.
- Create, edit, activate, deactivate, test, and sync actions are unavailable.

Switch to `tenant-admin-globex`.

Expected behavior:

- Globex sees platform-default rows.
- Globex does not see Acme-only rows.
- No hidden connection names or model ids leak through empty states.

## Responsive Review

Check desktop and narrow browser widths.

Expected behavior:

- Tables remain readable.
- Provider action buttons wrap instead of overlapping.
- Detail summary and action panels stack on small screens.
- Form labels stay attached to their inputs.
- No text overlaps in buttons, filters, or status pills.

## No-JavaScript Review

Disable JavaScript or ignore the enhancement script.

Expected behavior:

- List, create, edit, detail, and catalog pages still render.
- Save, activate, and deactivate form posts still work.
- Test and sync actions remain server endpoints.
- JavaScript only improves async result display and model-entry editing.

## Security Review

Look for prohibited content in the UI:

- Raw API keys.
- Provider tokens.
- Authorization headers.
- URL userinfo.
- Secret query parameters.
- Customer prompts.
- Model completions.
- Raw provider response bodies.

Expected behavior: none of these appear. Secret references are allowed.

## Quick Reviewer Path

1. Open `/admin/model-providers` as `platform-admin`.
2. Create an OpenAI provider using `qa011/openai-placeholder`.
3. Create a local provider using `http://127.0.0.1:11434` and
   `qa011/local-placeholder`.
4. Open each detail page and confirm safe metadata.
5. Run a test and confirm normalized evidence.
6. Sync catalog and open `/admin/model-providers/catalog`.
7. Switch to `tenant-admin-acme` and confirm read-only visibility.
8. Switch to `tenant-admin-globex` and confirm Acme-only rows are hidden.
9. Search saved HTML for `sk-`, `Bearer`, `Authorization`, `prompt`, and
   `completion`.

## Related QA

Use `qa011.md` for copy/paste setup, database evidence, redaction scans, and
automated test commands. Use `.env.qa011` for the deterministic environment.
