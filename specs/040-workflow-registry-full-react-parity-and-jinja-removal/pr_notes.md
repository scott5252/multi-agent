# PR Notes: Spec 040 Workflow React Parity And Jinja Removal

## Summary

Spec 040 moves workflow browser entry, create, draft, publish gate, revision, published version, sharing, and legacy route evidence into the React admin surface. The old workflow browser URLs now redirect to `/admin/app/workflows` or a stable React child route, while backend JSON and mutation routes remain authoritative for workflow decisions.

## Deleted

- `src/multi_agent_platform/web_admin/templates/workflows/index.html`
- `src/multi_agent_platform/web_admin/templates/workflows/create.html`
- `src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`
- `src/multi_agent_platform/web_admin/templates/workflows/publish_gate.html`
- `src/multi_agent_platform/web_admin/templates/workflows/revision_history.html`
- `src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`
- `src/multi_agent_platform/web_admin/templates/workflows/components/field_help_modal.html`
- `src/multi_agent_platform/web_admin/templates/workflows/components/graph_preview.html`
- `src/multi_agent_platform/web_admin/templates/workflows/components/reference_picker.html`
- `src/multi_agent_platform/web_admin/templates/workflows/components/validation_panel.html`
- `src/multi_agent_platform/web_admin/static/workflow_studio.js`

## Redirected Or Converted

- `/admin/workflows/ui` redirects to `/admin/app/workflows`.
- `/admin/workflows/new` redirects to `/admin/app/workflows/new`.
- `/admin/workflows/drafts/{workflow_draft_id}/editor` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}`.
- `/admin/workflows/drafts/{workflow_draft_id}/revisions/ui` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}/revisions`.
- `/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui` redirects to `/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate`.
- `/admin/workflows/versions/{workflow_version_bundle_id}/detail` redirects to `/admin/app/workflows/versions/{workflow_version_bundle_id}`.
- Legacy create, save, validate, restore, copy, and publish form posts still execute backend services and then redirect to React destinations or return safe HTTP problems.

## Retained With Evidence

- `src/multi_agent_platform/web_admin/static/workflow_studio.css`
- `src/multi_agent_platform/api/ui/admin_workflows.py`

The CSS file remains because the non-Jinja local login page and shared admin styling still reference it. It is no longer paired with workflow-owned Jinja templates or `workflow_studio.js`. The workflow UI helper module remains because exported view-model tests and compatibility helpers still document legacy workflow API shapes while later Jinja infrastructure work is pending.

## React Parity Evidence

- Backend-owned schemas now include workflow registry, create, sharing, version detail, and legacy route mapping envelopes.
- React JSON routes expose workflow registry, create state, draft detail, publish gate, version detail, builder, lookups, and legacy route mapping data.
- React components render workflow registry, create state, draft editing, graph preview with list alternatives, validation, publish readiness, sharing, revision history, and published version detail from server-owned contracts.
- Admin shell navigation and command destinations point to `/admin/app/workflows`.
- Focused backend and frontend tests cover redirect behavior, React contract shape, local browser login, app routing, and graph accessibility.

## Review Focus

- Confirm no workflow-owned template file remains under `src/multi_agent_platform/web_admin/templates/workflows`.
- Confirm `workflow_studio.js` is deleted and no runtime source imports it.
- Confirm old workflow browser routes return 303 redirects or safe HTTP problems, not TemplateResponse.
- Confirm `/admin/app/workflows`, `/admin/app/workflows/new`, draft direct links, publish gate links, revision links, and version links all load through the React host.
- Confirm redirect query preservation only keeps safe tenant, filter, saved-filter, status, revision, and conflict values.
- Confirm responses, screenshots, logs, QA docs, and reviewer notes contain no raw secrets, prompts, completions, memory contents, raw tool payloads, stack traces, local filesystem paths, or unauthorized tenant labels.

## Rollback

If React workflow parity fails, restore only the deleted workflow templates and `workflow_studio.js` from git and re-enable the old workflow browser handlers behind tests that label the restoration as temporary. Keep the React JSON routes and generated TypeScript contracts unless those specific contracts are the failure source. Do not restore shared shell templates or global Jinja infrastructure as part of the Spec 040 rollback.
