---
name: "speckit-autopilot-setup"
description: "Prompt for a new Spec Kit feature's per-spec details, then scaffold the reusable autopilot directory with autopilot.yml, specify.md, plan.md, tasks.md, policy.yml, and validation.yml."
compatibility: "Requires this repo's specs/_autopilot/shared policy and validation bases"
metadata:
  author: "multi-agent-project"
---

# Speckit Autopilot Setup

Use this skill when the user wants to create the file-backed autopilot setup for
a new spec.

## Ask For These Inputs

Ask only for missing values:

- Spec number, for example `016`
- Spec title, for example `Token Usage And Cost Analytics`
- Spec slug, or accept the generated slug from the title
- `/speckit.specify` prompt text
- `/speckit.plan` prompt text
- `/speckit.tasks` prompt text
- Primary browser QA path and expected text, or confirm the spec has no browser UI
- Optional extra curl/API validation commands

Default derived values:

- Autopilot directory: `specs/_autopilot/NNN-slug`
- Feature directory: `specs/NNN-slug`
- Branch: `codex/NNN-slug`
- QA id: `qaNNN`
- QA database: `multi_agent_platform_qaNNN`
- QA env: `specs/NNN-slug/.env.qaNNN`
- Artifact root: `.data/qaNNN-artifacts`
- Playwright output: `output/playwright/qaNNN_ui`
- Manual QA guide: `specs/NNN-slug/qaNNN_user_guide.md`

## Create The Files

After collecting inputs, run:

```bash
uv run python .agents/skills/speckit-autopilot-setup/scripts/create_autopilot_spec.py \
  --config /path/to/spec-setup.json
```

The config file must contain:

```json
{
  "spec_number": "016",
  "title": "Token Usage And Cost Analytics",
  "slug": "token-usage-cost-analytics",
  "prompts": {
    "specify": "/speckit.specify ...",
    "plan": "/speckit.plan ...",
    "tasks": "/speckit.tasks ..."
  },
  "playwright": {
    "path": "/admin/token-usage/ui",
    "expected_text": "Token Usage"
  },
  "extra_commands": [
    {
      "id": "token-usage-summary",
      "command": "curl --fail --silent http://127.0.0.1:8000/admin/token-usage",
      "expect_exit_code": 0
    }
  ]
}
```

Omit `playwright` when the spec has no browser UI. Omit `extra_commands` when
the shared health/version/dependency checks are enough for initial setup.

## Verify

Always run dry-runs after scaffolding:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/NNN-slug/validation.yml --dry-run
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/NNN-slug/validation.yml --dry-run --start-processes
```

Then tell the user the autopilot command:

```text
/speckit.autopilot specs/_autopilot/NNN-slug/autopilot.yml
```
