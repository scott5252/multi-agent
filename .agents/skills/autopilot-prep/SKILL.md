---
name: autopilot-prep
description: Prepare a durable Spec Kit autopilot roadmap directory from a roadmap Markdown document, such as docs/wizard_ui.md. Use when Codex needs to read a document with numbered Spec sections and create a specs/_autopilot roadmap queue with per-spec phase prompts, queue.json, policy.yml, validation.yml, and status files for a later autonomous implementation run.
---

# Autopilot Prep

## Overview

Use this skill to turn a roadmap document into a reusable file-backed queue for
`autopilot-implement`. It generalizes the existing
`speckit-react-ui-autopilot`, `speckit-react-ui2-autopilot`, and
`speckit-workflow-setup-autopilot` preparation pattern.

The roadmap document must contain sections like:

````markdown
## Global Prompt Prefix

```text
Shared guidance for every generated phase prompt.
```

## Spec 074 - Console Home Onboarding Wizard Entry

### Specify Prompt

```text
...
```

### Plan Prompt

```text
...
```

### Tasks Prompt

```text
...
```

### Implement Prompt

```text
...
```
````

`Clarify Prompt` and `Analyze Prompt` blocks are optional. When absent, the
prep script generates autonomous clarification and analysis prompts from the
roadmap context and repo guardrails.

## Inputs

Require one parameter: the roadmap Markdown file. Example:

```bash
uv run python .agents/skills/autopilot-prep/scripts/prepare_autopilot_roadmap.py \
  docs/wizard_ui.md
```

By default the output directory is:

```text
specs/_autopilot/<normalized-document-name>-roadmap
```

For `docs/wizard_ui.md`, the output is:

```text
specs/_autopilot/wizard-ui-roadmap
```

Accept `--output` only when the user explicitly wants a different
`specs/_autopilot/...` directory.

## Preparation Workflow

1. Read the roadmap document, `AGENTS.md`, and the latest plan referenced by
   `AGENTS.md` when present.
2. Confirm the roadmap has numbered `## Spec NNN - Title` sections and
   `Specify`, `Plan`, `Tasks`, and `Implement` fenced prompt blocks for every
   spec.
3. Optionally dry-run the parser without writing files:

   ```bash
   uv run python .agents/skills/autopilot-prep/scripts/prepare_autopilot_roadmap.py \
     <roadmap-file> --dry-run
   ```

4. Run the prep script:

   ```bash
   uv run python .agents/skills/autopilot-prep/scripts/prepare_autopilot_roadmap.py \
     <roadmap-file>
   ```

5. Inspect the generated `queue.json`. Confirm:
   - `next_spec` points at the first pending spec.
   - Every spec has `specify.md`, `clarify.md`, `plan.md`, `tasks.md`,
     `analyze.md`, `implement.md`, `autopilot.yml`, `policy.yml`,
     `validation.yml`, and `status.json`.
   - Feature directories are deterministic: `specs/NNN-slug`.
   - Branch names use `codex/NNN-slug`.
6. Run dry-runs for every validation manifest:

   ```bash
   for f in specs/_autopilot/<roadmap-dir>/*/validation.yml; do
     uv run python scripts/qa/run_spec_qa.py "$f" --dry-run
     uv run python scripts/qa/run_playwright_ui.py "$f" --dry-run --start-processes
   done
   ```

7. If a generated Playwright route hint is too generic, edit only the relevant
   `validation.yml` route and expected text. The implement skill may also
   tighten route hints after each spec creates real UI.
8. Report the generated directory and the command to run next:

   ```text
   Use autopilot-implement with specs/_autopilot/<roadmap-dir>
   ```

## Generated Contract

The prep script writes a roadmap root containing:

- `queue.json`: durable roadmap queue, per-spec phase status, run contract, and
  final stability gate commands.
- `status.json`: roadmap-level state for resumes.
- `NNN-slug/`: one directory per spec with phase prompts and validation config.

Each per-spec directory contains:

- `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`,
  `implement.md`
- `autopilot.yml`
- `policy.yml`
- `validation.yml`
- `status.json`

The script preserves existing queue phase/status/validation values when
rerun, so it can safely refresh prompts without losing completed-state
bookkeeping.

## Stop Conditions

Stop and ask the user before generating if:

- The document lacks numbered Spec sections.
- A spec lacks `Specify`, `Plan`, `Tasks`, or `Implement` prompt blocks.
- The requested output directory is outside `specs/_autopilot`.
- Existing generated files conflict with unrelated user edits that cannot be
  reconciled by preserving queue/status state.
