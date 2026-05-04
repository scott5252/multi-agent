# PR Review Notes: User Briefing Preferences And Context

## Scope

- Adds first-class Daily Intelligence Briefing preferences.
- Adds immutable preference revisions and safe audit events.
- Adds browser and API surfaces under `/admin/briefing-preferences`.
- Adds runtime resolver context for Daily Intelligence Briefing runs.
- Wires Telegram `Morning briefing` alias dispatch to include resolved context.

## Security And Privacy

- Account fields accept safe references only.
- Admin summaries show masked VIP senders and reference labels only.
- Cross-tenant access fails closed.
- Runtime resolver records safe audit metadata without logging raw credentials.

## Durability

- Profile heads and immutable revisions persist in PostgreSQL.
- Runtime context includes the profile revision id and digest used for run input.
- The migration is additive and does not rewrite existing data.

## Test Evidence

Review:

- `tests/unit/db/test_briefing_preferences_repository.py`
- `tests/unit/admin/briefing_preferences/test_briefing_preference_service.py`
- `tests/integration/api/test_admin_briefing_preferences_api.py`
- `tests/integration/api/test_admin_briefing_preferences_ui.py`
- `tests/integration/runtime/test_briefing_preference_resolution.py`

## Residual Limits

- Scheduled dispatch execution is stored as preference state only.
- Delegated credential creation is out of scope.
- Live Calendar/Gmail/news/weather tool calls remain covered by other specs.
