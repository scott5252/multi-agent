# /speckit.constitution

Update `.specify/memory/constitution.md` as the governing policy for the
repository and synchronize all dependent artifacts in the same change.

## Mandatory Requirements

- Read the existing constitution, the spec, plan, and tasks templates, the
  command prompt files in this directory, `README.md`, and `docs/quickstart.md`
  before finalizing changes.
- Replace every placeholder in the constitution with concrete repository
  guidance. Leave no unresolved bracket tokens.
- Use semantic versioning for constitution changes and explain the bump.
- Add a Sync Impact Report as an HTML comment at the top of the constitution.
- Use ISO dates. If a historical ratification date is truly unknown, insert
  `TODO(RATIFICATION_DATE): ...` and mention it in the Sync Impact Report.

## Synchronization Rules

When the constitution changes, update these files when affected:

- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`
- `.specify/templates/commands/*.md`
- `README.md`
- `docs/quickstart.md`
- any feature-specific quickstart or operator docs whose meaning changed

## Validation

- Principles MUST use direct enforceable language such as MUST, MUST NOT, and
  SHOULD with rationale.
- Governance MUST define amendment rules, semantic-versioning rules,
  constitution-check expectations in plans, and synchronization requirements for
  templates, command files, and docs.
- The updated constitution MUST require future plan outputs to include
  constitution checks, durability decisions, tenant decisions, lineage
  decisions, version-bundle decisions, secret/tool-policy decisions,
  artifact-storage decisions, approval/resume decisions where relevant,
  observability requirements, test strategy, documentation tasks, and security
  review notes where relevant.
- The updated constitution MUST require future tasks outputs to include
  test-first tasks where practical, documentation tasks, `README.md` update
  tasks, in-scope platform-governance tasks, and operational validation tasks.
