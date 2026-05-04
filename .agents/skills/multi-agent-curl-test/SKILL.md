---
name: multi-agent-curl-test
description: Recreate and validate the Multi-Agent Platform local curl QA environment. Use when Codex needs to run curl_testing.md end-to-end against this repository by dropping and recreating the multi_agent_curl_test PostgreSQL database, applying Alembic migrations, seeding required Acme/Globex/local-principal data, restarting the FastAPI server, executing every curl command in curl_testing.md sequentially, stopping on the first failure, and reporting succeeded and failed commands.
---

# Multi-Agent Curl Test

## Overview

Use this skill to perform the repository's full JSON/API curl walkthrough from
`curl_testing.md` against a fresh PostgreSQL database named
`multi_agent_curl_test`.

The reusable runner is:

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py
```

Run it from the repository root. It creates a timestamped run directory under
`.data/curl_test_runs/` containing the generated shell script, server log,
captured curl outputs, and pass/fail summary files.

## Workflow

1. Read `system_architecture.md`, `user_guide.md`, and `curl_testing.md` if the
   user asks for context, changes the test scope, or reports a failure that
   needs diagnosis.
2. Confirm PostgreSQL is available locally. The default connection is
   `postgres:postgres@127.0.0.1:5432`; override with flags or environment
   variables when needed.
3. Run the script from the repository root.
4. Let the script own database recreation, migrations, seed data, uvicorn
   restart, curl execution, status verification, JSON-shape checks, and
   fail-fast reporting.
5. If the script fails, stop there. Report the failed curl step, expected and
   actual status codes, the captured output, and the run directory path.
6. If the script succeeds, report the total succeeded command sections and the
   run directory path.

## Runner Behavior

The runner performs these operations in order:

- Runs `uv sync` unless `--skip-uv-sync` is provided.
- Drops and recreates the `multi_agent_curl_test` database.
- Runs `uv run alembic upgrade head`.
- Seeds active Acme and Globex tenants, local principal identities, one tenant
  membership for the optional membership-status curl step, one saved workflow
  filter for the saved-filter restore curl step, and placeholder breaker/dead
  letter ids for reliability placeholder curl steps.
- Exports a local-principal catalog for `platform-admin`, `tenant-admin-acme`,
  `tenant-admin-globex`, and `auditor`.
- Kills an existing process on the target API port unless
  `--no-kill-existing-server` is provided.
- Starts `uv run uvicorn multi_agent_platform.api.main:app`.
- Parses every `bash` code block under `###` headings in `curl_testing.md` that
  contains a `curl` command, then executes the original commands in order.
- Verifies expected HTTP status codes from each section's `Expected \`...\``
  lines. When a section has setup curl commands plus one explicit expected
  status, earlier curl commands must return 2xx/3xx and the final curl command
  must match the expected status.
- Checks JSON-looking outputs are valid JSON. It skips `curl -i` and SSE output
  bodies for JSON parsing.
- Stops on the first failed command and prints a summary of succeeded commands
  plus the failed command and captured output.

## Common Options

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py \
  --pg-host 127.0.0.1 \
  --pg-port 5432 \
  --pg-user postgres \
  --pg-password postgres \
  --db-name multi_agent_curl_test \
  --port 8000
```

Useful flags:

- `--skip-uv-sync`: skip dependency sync when the environment is already fresh.
- `--keep-server-running`: leave the uvicorn process alive after the run.
- `--no-kill-existing-server`: do not terminate an existing process on the API
  port before starting uvicorn.
- `--output-dir <path>`: write run artifacts to a specific directory.

## Reporting

Always include:

- Database name and API base URL used.
- Whether the server was restarted.
- Count and names of succeeded curl sections.
- The first failed curl section, if any.
- Expected status, actual status, and the most relevant captured output for a
  failure.
- Run artifact directory.
