# Reviewer Notes: Spec 055 Channels Telegram Briefing React Live Data

## Scope

Spec 055 replaces deterministic channel, Telegram, and briefing React data with
live repository and service-backed projections for tenant Telegram
configuration, command aliases, linked identities, link-token audits, webhook
receipts, delivery attempts, workflow run links, briefing preference profiles,
and preference mutation evidence.

## Implementation Notes

- Channel dashboard builders now depend on Telegram configuration services,
  briefing preference services, channel repositories, and runtime repositories.
- Channel and briefing routes now construct live dependencies from the request
  database session and container instead of returning fixed QA036 projections.
- Repository helpers provide bounded recent webhook receipt, delivery attempt,
  and runtime run queries.
- QA055 seed data persists a minimal workflow version and runtime run so
  delivery and run status evidence is valid under PostgreSQL foreign keys.
- Scanner guardrails now treat old QA036 channel markers as blocking in
  production channel surfaces.

## QA Notes

- QA environment: `specs/055-channels-telegram-briefing-react-live-data/.env.qa055`
- Seed script: `scripts/qa/seed_channels_briefing_qa055.py`
- Post-UI verifier: `scripts/qa/verify_channels_briefing_qa055.py`
- Main browser route: `/admin/app/channels`
- Playwright action: sign in as `tenant-user-acme`, click `Save Preferences`,
  verify `Preference profile saved with redacted summaries.`, and confirm the
  verifier sees a second preference revision plus `profile_updated` audit.

## Safety Notes

- No real provider calls are used.
- No real Telegram calls are used.
- QA secrets use the `qa055/` static reference prefix.
- Browser and API output must not include bot tokens, webhook secrets, raw
  Telegram identifiers, raw messages, raw preferences, raw run payloads,
  provider tokens, credential values, local paths, stack traces, or
  unauthorized tenant labels.

## Commit Notes

No intermediate commit is required for this spec. The autopilot is intentionally
continuing in the dirty worktree until the full remove-mock-data sequence is
complete and the user commits.
