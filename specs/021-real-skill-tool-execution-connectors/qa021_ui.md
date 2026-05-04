# QA021 UI Guide: Real Skill Tool Execution Connectors

## Browser Target

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/skill-execution/ui/diagnostics
```

Choose `platform-admin`.

## Expected Page

- The page title is `Skill Tool Diagnostics`.
- The Daily Briefing Tool Readiness table lists five tools.
- The tools are Google Calendar Events, Gmail Messages, News Search, Weather
  Forecast, and Commute Lookup.
- Mode is `mock`.
- Readiness is `ready`.
- Credential cells show redacted references.
- Latest summaries show safe counts or short summaries.
- Policy Decisions show allow decisions for registered tool, installed skill,
  tool policy, side-effect policy, outbound policy, execution mode, credential
  policy, and credential tenant.

## Screenshots

Capture:

- `01-local-login.png`
- `02-real-skill-tool-execution-connectors-target.png`
- `03-real-skill-tool-execution-connectors-direct-target.png`

## Playwright Validation

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/021-real-skill-tool-execution-connectors/validation.yml --start-processes
```

## Redaction Review

Inspect the screenshot text. It must not contain:

- access tokens
- API key values
- OAuth refresh tokens
- raw secret values
- raw email body text
- provider URL query strings with sensitive values

It may contain safe labels, tool names, allowed domains, counts, and redacted
markers such as `[redacted reference available]`.
