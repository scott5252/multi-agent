---
name: "speckit-autopilot"
description: "Run a file-backed autonomous Spec Kit cycle with Codex: specify, clarify-auto, plan, tasks, analyze-auto, implement, API/curl validation, and Playwright UI validation."
compatibility: "Requires spec-kit project structure with .specify/ directory and Codex Spec Kit skills installed"
metadata:
  author: "multi-agent-project"
  source: "templates/commands/autopilot.md"
---

# Speckit Autopilot

Use this skill when the user asks Codex to run Spec Kit from one or more files,
auto-resolve clarification and analysis gaps, implement tasks, and validate API
and browser behavior.

## Required Input

Accept either:

- A manifest file path such as `specs/_autopilot/my-feature/autopilot.yml`
- A feature prompt file path such as `specs/_autopilot/my-feature/prompt.md`

The manifest may be JSON, TOML, or YAML. JSON syntax inside `.yml` is supported
without extra dependencies and is the preferred portable format.

Recommended manifest fields:

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

## Autopilot Phases

Run these eight phases in order:

1. **Preflight**: load the manifest, prompt files, policy, validation plan,
   `.specify/feature.json`, `.specify/extensions.yml`, git status, and current
   constitution.
2. **Specify**: run the equivalent of `/speckit.specify` from the combined
   prompt files. Persist the resolved feature directory.
3. **Clarify Auto**: run the clarification scan. Auto-select recommended
   answers only when policy allows and the answer is low-risk. Record each
   auto-choice in `spec.md`.
4. **Plan**: run the equivalent of `/speckit.plan`, producing `plan.md`,
   `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`.
5. **Tasks**: run the equivalent of `/speckit.tasks` and verify every task is
   dependency ordered, traceable, and independently testable.
6. **Analyze Auto**: run the equivalent of `/speckit.analyze`. Remediate
   critical/high findings when policy allows, then rerun analysis until the
   configured loop limit or clean result.
7. **Implement**: run the equivalent of `/speckit.implement`, marking tasks
   complete as work lands. If the user explicitly requested sub-agents, split
   independent `[P]` tasks by disjoint files and integrate results locally.
8. **Validate**: run generated QA-doc validation, API/curl checks, Playwright UI
   flows, screenshots, and quality gates from the validation plan.

## Auto-Decision Policy

Default to autonomy for low-risk choices, but stop and ask the user for:

- Security, tenant-isolation, secret, credential, or outbound-tool uncertainty.
- Destructive data changes, irreversible retention, or migration ambiguity.
- Approval/resume semantics that materially change durable state.
- Requirements that conflict with `.specify/memory/constitution.md`.
- Any command marked `requires_confirmation: true` in the policy or validation
  file.

When auto-selecting a clarification, add a concise audit line to the spec:

```markdown
- Q: <clarification question> -> A: <auto-selected answer> (autopilot)
```

## Validation

Use these project scripts when the validation file requests them:

```bash
uv run python scripts/qa/run_spec_qa.py <validation-file>
uv run python scripts/qa/run_playwright_ui.py <validation-file> --start-processes
```

Always report:

- Feature directory and generated artifacts.
- Clarifications auto-selected and any skipped decisions.
- Analyze findings remediated or left outstanding.
- Implementation task counts.
- API/curl and Playwright evidence paths.
- Quality commands run and their results.
