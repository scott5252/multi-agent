# Spec Kit Autopilot

Spec Kit Autopilot lets Codex run a complete file-backed delivery cycle from a
manifest instead of a live sequence of pasted prompts.

The entrypoint is:

```text
/speckit.autopilot specs/_autopilot/<feature>/autopilot.yml
```

The manifest points at one or more prompt files, a policy file, and a validation
file. JSON syntax inside `.yml` files is supported so the default examples work
without extra parser dependencies.

## File Layout

```text
specs/_autopilot/my-feature/
├── autopilot.yml
├── prompt.md
├── policy.yml
└── validation.yml
```

`prompt.md` contains the feature request. Multiple prompt files are read in the
order listed by the manifest.

`policy.yml` controls autonomy. It allows low-risk recommended clarifications
and analysis fixes to be selected automatically, but requires Codex to stop for
constitution conflicts, tenant-isolation uncertainty, secret handling
uncertainty, destructive data changes, or approval/resume ambiguity.

`validation.yml` drives executable evidence:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/my-feature/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/my-feature/validation.yml --start-processes
```

## Reusable Configuration

Most specs should extend the shared defaults:

```json
{
  "extends": "../shared/validation.base.yml",
  "variables": {
    "spec_title": "My Feature",
    "spec_number": "016",
    "spec_slug": "my-feature",
    "feature_dir": "specs/016-my-feature",
    "autopilot_dir": "specs/_autopilot/016-my-feature",
    "branch": "codex/016-my-feature",
    "qa_id": "qa016",
    "qa_label": "QA016",
    "qa_database": "multi_agent_platform_qa016",
    "qa_env_file": "specs/016-my-feature/.env.qa016",
    "artifact_root": ".data/qa016-artifacts",
    "playwright_output_dir": "output/playwright/qa016_ui",
    "manual_qa_user_guide": "specs/016-my-feature/qa016_user_guide.md"
  },
  "playwright": {
    "flows": []
  }
}
```

The shared files live in `specs/_autopilot/shared/`:

- `policy.base.yml`
- `validation.base.yml`

Per-spec files normally only set variables and Playwright flows.

## Scaffold A New Spec

Use the `speckit-autopilot-setup` skill when you want Codex to ask for the
next spec's details and create the autopilot folder.

The skill gathers:

- spec number and title
- optional slug
- specify, plan, and tasks prompts
- primary browser QA route and expected text, if the spec has UI
- optional extra curl/API checks

It then runs:

```bash
uv run python .agents/skills/speckit-autopilot-setup/scripts/create_autopilot_spec.py \
  --config /tmp/spec-setup.json
```

The generated spec folder extends the shared policy and validation defaults, so
future specs only carry the details that change.

## Eight Phases

Autopilot runs:

1. Preflight
2. Specify
3. Clarify Auto
4. Plan
5. Tasks
6. Analyze Auto
7. Implement
8. Validate

The validation phase runs QA document validation, API/curl commands, Playwright
browser flows, screenshots, and quality gates defined by the validation file.

## Example

Start from the portable example:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/example/validation.yml --dry-run
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/example/validation.yml --dry-run
```

Then copy `specs/_autopilot/example/` to a feature-specific folder and replace
the prompt, policy, and validation details.
