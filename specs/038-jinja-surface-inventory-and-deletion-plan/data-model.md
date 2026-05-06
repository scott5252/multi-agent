# Data Model: Jinja Surface Inventory And Deletion Plan

## JinjaInventorySummary

- `generated_at`: deterministic timestamp for the projection.
- `total_items`: total inventory rows visible to the current principal.
- `template_count`: discovered Jinja template files.
- `route_count`: browser route or TemplateResponse entries.
- `static_asset_count`: legacy static JavaScript/CSS entries.
- `direct_link_count`: docs/QA direct-link references.
- `blocked_count`: items blocked pending parity, owner, route, or evidence.
- `safe_to_delete_count`: items with deletion-grade parity evidence and reviewer signoff requirement.
- `reviewer_signoff_required`: always `true` for Spec 038.

## JinjaInventoryItem

- `item_id`: stable identifier derived from type and repo-relative path or route.
- `item_type`: `template`, `template_include`, `template_response`, `jinja_import`, `template_helper`, `static_asset`, `route`, `direct_link`, `form_action`, `export`, `upload`, `filter`, `sse_progress`, `mutation`, `denied_state`, or `react_host`.
- `label`: safe human-readable name.
- `source_path`: repo-relative source path when applicable.
- `source_line`: source line number when applicable.
- `legacy_route`: legacy browser URL when applicable.
- `react_path`: replacement React route when known.
- `methods`: HTTP methods when applicable.
- `owner_category`: roadmap category such as shell/auth, workflows, governance, skills, test bench, operations/usage, channels/memberships, or user runs.
- `planned_removal_spec`: one of `039` through `047`.
- `classification`: `react_parity_proven`, `react_parity_missing`, `redirectable`, `non_jinja_compatibility_needed`, `safe_to_delete`, or `blocked_with_reason`.
- `evidence_refs`: safe QA, test, docs, or audit reference IDs.
- `blocker_refs`: safe blocker IDs when classification is blocked or missing parity.
- `redirect_preserves`: tenant id, route parameters, filters, saved-filter intent, breadcrumbs, or other safe state a redirect must preserve.
- `behaviors`: form actions, exports, uploads, filters, SSE/progress, mutations, denied states, artifacts, callbacks, subscriptions, or empty when not applicable.
- `reviewer_signoff_required`: boolean indicating later deletion requires explicit reviewer approval.
- `notes`: safe summary without secrets, private payloads, raw prompts, stack traces, local paths, or unauthorized tenant labels.

## JinjaInventoryGroup

- `group_id`: stable category ID.
- `label`: reviewer-facing group label.
- `planned_removal_spec`: roadmap spec responsible for deletion/conversion.
- `items`: grouped inventory items.
- `blocked_count`: group blocked item count.
- `safe_to_delete_count`: group safe-to-delete candidate count.

## JinjaInventoryEvidence

- `evidence_id`: stable safe ID.
- `evidence_type`: `scanner`, `contract_test`, `backend_route_test`, `frontend_test`, `playwright`, `qa_doc`, `redaction`, `tenant_isolation`, or `reviewer_note`.
- `reference`: repo-relative path, test node ID, screenshot filename, or audit-safe label.
- `status`: `pass`, `warning`, or `blocked`.

## State Rules

- `safe_to_delete` is allowed only when `evidence_refs` is non-empty, `reviewer_signoff_required` is true, and `planned_removal_spec` is set.
- Missing source evidence cannot be classified as `safe_to_delete`.
- Any item with unknown route behavior, unknown direct-link behavior, or missing owner must be `blocked_with_reason`.
- Inventory output must use repo-relative paths and safe labels only.
