# /speckit.autopilot

Run an autonomous, file-backed Spec Kit delivery cycle with Codex.

## User Input

```text
$ARGUMENTS
```

The argument must identify either:

- An autopilot manifest file, for example
  `specs/_autopilot/my-feature/autopilot.yml`
- A prompt file, for example `specs/_autopilot/my-feature/prompt.md`

If a prompt file is provided, use sibling `policy.yml` and `validation.yml`
when they exist. If no policy is present, use the conservative defaults below.

## Manifest Contract

The manifest may be JSON, TOML, or YAML. JSON syntax inside `.yml` is portable
and should be accepted without extra dependencies.

```json
{
  "schema_version": "1.0",
  "feature": {
    "name": "feature-short-name",
    "branch": "codex/feature-short-name"
  },
  "prompt_files": ["prompt.md"],
  "policy_file": "policy.yml",
  "validation_file": "validation.yml"
}
```

Paths are resolved relative to the manifest directory unless absolute.

Policy and validation files may use:

- `extends`: a relative or absolute path, or a list of paths, to shared base
  config files
- `variables`: string values referenced by shared configs as `${name}`

Shared defaults live under `specs/_autopilot/shared/`.

## Conservative Defaults

```json
{
  "autonomy": {
    "auto_select_clarifications": true,
    "minimum_confidence": 0.75,
    "stop_on": [
      "constitution_conflict",
      "tenant_isolation_uncertainty",
      "secret_or_credential_uncertainty",
      "destructive_data_change",
      "approval_resume_ambiguity"
    ]
  },
  "analysis": {
    "auto_remediate_severities": ["CRITICAL", "HIGH"],
    "max_remediation_loops": 2
  },
  "implementation": {
    "allow_subagents_when_user_requested": true,
    "mark_tasks_complete": true
  },
  "validation": {
    "run_qa_docs": true,
    "run_api_checks": true,
    "run_playwright": true,
    "run_quality_gates": true
  }
}
```

## Execution Workflow

Run these eight phases in order.

### Phase 1: Preflight

1. Load the manifest, policy file, validation file, and prompt files.
2. Read `.specify/memory/constitution.md`, `.specify/extensions.yml`, and
   `.specify/feature.json` when present.
3. Run `git status --short --branch`.
4. Stop if required files are missing or the worktree state conflicts with the
   policy.

### Phase 2: Specify

1. Combine prompt files in manifest order.
2. Run the equivalent of `/speckit.specify` with the combined prompt.
3. Persist `.specify/feature.json` and record the resolved feature directory.

### Phase 3: Clarify Auto

1. Run the `/speckit.clarify` ambiguity scan against the active spec.
2. For each clarification, select the recommended answer only when:
   - policy allows auto-selection
   - the recommendation is constitution-compatible
   - the choice does not hit a configured stop condition
3. Write accepted answers into `spec.md` under `## Clarifications`.
4. Stop and ask the user for any high-risk unresolved decision.

### Phase 4: Plan

Run the equivalent of `/speckit.plan`. Confirm these artifacts exist when the
feature requires them:

- `plan.md`
- `research.md`
- `data-model.md`
- `contracts/`
- `quickstart.md`

### Phase 5: Tasks

Run the equivalent of `/speckit.tasks`. Confirm:

- every task uses `- [ ] TNNN` or `- [X] TNNN`
- story tasks carry `[USN]`
- file paths are concrete
- required validation and docs tasks are present

### Phase 6: Analyze Auto

1. Run the equivalent of `/speckit.analyze`.
2. Convert findings into a remediation queue.
3. Auto-remediate only severities configured in policy.
4. Rerun plan/tasks/analyze as needed until no blocking finding remains or the
   remediation loop limit is reached.

### Phase 7: Implement

1. Run the equivalent of `/speckit.implement`.
2. Execute tasks phase by phase.
3. Mark completed tasks in `tasks.md`.
4. If the user explicitly requested sub-agents, delegate only independent
   `[P]` tasks with disjoint write sets and integrate locally.

### Phase 8: Validate

Run configured validation in this order:

1. QA document validation:
   `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"`
2. API/curl checks:
   `uv run python scripts/qa/run_spec_qa.py <validation-file>`
3. Playwright UI checks:
   `uv run python scripts/qa/run_playwright_ui.py <validation-file> --start-processes`
4. Quality gates from the validation file, normally:
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run mypy src`
   - `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`

## Completion Report

Report:

- Manifest path and feature directory.
- Files generated or changed.
- Clarifications auto-selected and any unresolved decisions.
- Analyze remediation loop count.
- Implementation task completion count.
- API/curl evidence and Playwright screenshot paths.
- Quality commands executed.
- Any validation that could not run and why.
