# Post-Implementation QA Documents Extension

This extension makes manual QA evidence part of the implementation completion
gate for every Spec Kit feature in this project.

## Installation

This project already has the extension installed under
`.specify/extensions/qa-docs`. To install the same extension into another
Spec Kit project from a checkout, use:

```bash
specify extension add --dev /path/to/qa-docs
```

## What It Adds

After `/speckit.implement` completes, the mandatory `after_implement` hook runs
`/speckit.qa-docs.generate-documents`. That command creates two files in the
active spec directory:

- `qaNNN.md`, where `NNN` is the spec number, for example `qa009.md`
- `.env.qaNNN`, for example `.env.qa009`

The 008 guide is the local quality bar. New guides should be written for
non-developer reviewers, include copy/paste commands, state expected outputs,
save responses under `/tmp/qaNNN-*`, cover success and failure paths, and
include automated quality evidence.

## Command

| Command | Description |
|---------|-------------|
| `speckit.qa-docs.generate-documents` | Generate the spec-specific QA guide and QA environment file after implementation |

## Hook

| Event | Command | Optional | Description |
|-------|---------|----------|-------------|
| `after_implement` | `speckit.qa-docs.generate-documents` | No | Create and validate post-implementation QA documents |

## Validation

The command finishes by running:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh "$FEATURE_DIR"
```

The validator confirms that:

- Both files exist in the active spec directory.
- The guide has the required reviewer sections.
- The guide is detailed enough to avoid placeholder output.
- The environment file includes the required application, auth, database,
  secret, and storage settings.
- Spec-specific names such as `qaNNN`, `multi_agent_platform_qaNNN`, and
  `.data/qaNNN-artifacts` are used consistently.

Thresholds live in `.specify/extensions/qa-docs/qa-docs-config.yml`.

## Permissions And File Access

The extension reads the active spec directory, the QA008 reference guide, and
the QA008 environment reference. It writes only the active spec directory's
`qaNNN.md` and `.env.qaNNN` files. The validator reads those files plus
`.specify/extensions/qa-docs/qa-docs-config.yml`.

The extension does not call external APIs, read production credentials, or write
outside the active Spec Kit project. Generated `.env.qaNNN` files must contain
only fake local QA placeholders.

## Configuration

Project thresholds are configured in:

```text
.specify/extensions/qa-docs/qa-docs-config.yml
```

Local machine overrides may be added in
`.specify/extensions/qa-docs/qa-docs-config.local.yml`; keep that file
untracked.

The validator also accepts these environment overrides:

```text
SPECKIT_QA_DOCS_MIN_GUIDE_LINES
SPECKIT_QA_DOCS_MIN_ENV_LINES
SPECKIT_QA_DOCS_MIN_CODE_FENCES
SPECKIT_QA_DOCS_MIN_EXPECTED_MARKERS
```
