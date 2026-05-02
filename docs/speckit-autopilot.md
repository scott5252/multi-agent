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
