# Quickstart: Channels, Telegram, Briefing React Live Data

## Local Validation

1. Generate updated backend and frontend contracts after schema changes:

   ```bash
   uv run python scripts/frontend/generate_admin_react_types.py
   ```

2. Run focused backend tests:

   ```bash
   uv run pytest --no-cov tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py -k "channel_telegram_briefing or react_channels or live_data_inventory" -q
   ```

3. Run frontend channel and briefing checks:

   ```bash
   npm run --prefix frontend/admin test -- --run ChannelTelegramBriefing
   npm run --prefix frontend/admin typecheck
   npm run --prefix frontend/admin build
   ```

4. Run scanner and contract checks:

   ```bash
   uv run pytest --no-cov tests/unit/admin/test_live_data_inventory_scanner.py tests/contract/test_admin_react_contract.py -q
   ```

## Required qa055 Validation

1. Validate QA docs:

   ```bash
   bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/055-channels-telegram-briefing-react-live-data
   ```

2. Run Spec QA:

   ```bash
   uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml
   ```

3. Run Playwright UI validation:

   ```bash
   uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml --start-processes
   ```

4. Verify the Playwright action persisted:

   ```bash
   uv run python scripts/qa/verify_channels_briefing_qa055.py
   ```

5. Run the post-spec curl test:

   ```bash
   uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa055-after-spec
   ```

## Expected Evidence

- Empty qa055 workspace returns no deterministic QA036 aliases, identities, deliveries, notifications, webhook receipts, run links, preferences, imports, exports, or audits.
- Seeded qa055 workspace returns only persisted rows authorized for the active tenant or platform scope.
- Playwright signs in as `tenant-user-acme`, clicks `Save Preferences`, verifies `Preference profile saved with redacted summaries.`, and captures a screenshot under `output/playwright/qa055_ui/`.
- Post-UI verification reports persisted action and audit evidence without bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, private messages, raw webhook payloads, raw run payloads, raw briefing content, local paths, stack traces, or unauthorized tenant labels.
