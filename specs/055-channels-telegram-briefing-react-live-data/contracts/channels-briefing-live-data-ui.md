# UI Contract: Channels, Telegram, Briefing React Live Data

## Routes

- `/admin/app/channels` serves the React channel, Telegram, and briefing workspace.
- `/admin/app/channels/bootstrap.json` returns the live dashboard envelope consumed by the channel/briefing page.
- Mutation endpoints for aliases, link tokens, webhook validation, briefing preferences, imports, and exports return safe mutation results.
- Diagnostic list endpoints return bounded live delivery, webhook, notification, run, and audit evidence.

## Required States

- **Live seeded state**: qa055 seeded tenant renders persisted Telegram config, aliases, linked identities, delivery diagnostics, webhook receipts, notifications, run links, and briefing preferences.
- **Empty state**: Fresh qa055 tenant renders no rows and displays truthful empty or unavailable summaries.
- **Denied state**: Cross-tenant or unauthorized requests return safe problem details or denied states without Telegram identifiers, private messages, run payloads, preference contents, or tenant labels from the forbidden scope.
- **Mutation accepted/replayed**: A visible result panel shows persisted alias, token audit, webhook validation, briefing preference, import, or export evidence.

## Redaction Contract

The browser contract must not include bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, authorization headers, private channel messages, raw webhook payloads, raw run payloads, raw briefing content, local paths, stack traces, or unauthorized tenant labels.

## Playwright Contract

- Playwright loads the workspace with local-principal authentication.
- The flow must render seeded live state.
- The flow must perform one visible persisted action.
- Post-UI verification confirms persisted action and audit evidence through the backend API or redaction-safe qa055 database query.
