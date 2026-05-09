# Data Model: Admin Design Review Workspace

## DesignReviewWorkspaceEnvelope

- `title`: Product heading for the workspace.
- `description`: Safe summary of the workspace purpose.
- `active_scope`: Existing React admin scope projection.
- `state`: Existing shell state projection for loading/empty/denied/error.
- `provenance`: Live-data provenance for reviewer evidence.
- `summary_cards`: Counts and statuses derived from live sessions.
- `sessions`: Tenant-scoped session summaries.
- `selected_session`: Detailed selected session, or null.
- `workflow_options`: Authorized published workflow bundles.
- `quorum_policies`: Supported policy labels and descriptions.
- `actions`: Safe action hrefs for create, refresh, launch, and manual decision.

## DesignReviewWorkspaceSessionDetail

- `session`: Existing safe session response.
- `revisions`: Existing safe revision responses.
- `rounds`: Round details with assignments, verdict summaries, and quorum decision.
- `manual_decisions`: Durable manual decisions.
- `handoff`: Existing safe handoff response.
- `coordinator`: Latest coordinator state.

## DesignReviewWorkspaceRoundDetail

- `round`: Existing safe round response.
- `assignments`: Reviewer assignment summaries.
- `verdicts`: Safe verdict summaries.
- `quorum_decision`: Latest decision for the round.

## DesignReviewWorkflowOption

- `workflow_version_bundle_id`: Published bundle ID.
- `label`: Display version and workflow key.
- `workflow_key`: Safe workflow key from the bundle summary.
- `display_version`: Published display version.
- `tenant_id`: Owning tenant when tenant-scoped.
- `status`: Published/hidden/retired status.

## Relationships

- A workspace envelope belongs to exactly one active scope.
- A selected session belongs to the active tenant scope.
- Round details belong to the selected session.
- Workflow options are tenant or global published bundles authorized for the active scope.

## Validation Rules

- Do not include raw provider/model payloads, prompts, completions, secrets, private messages, memory contents, unauthorized payloads, or external tool payloads.
- Do not synthesize sessions, rounds, verdicts, decisions, or handoffs when the database is empty.
- Do not expose cross-tenant records.
- Action links must include tenant scope when required.
