# Contract Notes: Workflow Setup Wizard And Runtime Launch

## Existing Contracts Used

- `GET /admin/app/workflows/builder.json`
- `GET /admin/app/workflows/lookups.json`
- `POST /admin/app/workflows`
- `POST /admin/app/workflows/drafts/{workflow_draft_id}/save`
- `POST /admin/app/workflows/drafts/{workflow_draft_id}/validate`
- `POST /admin/app/workflows/drafts/{workflow_draft_id}/publish`
- `POST /admin/app/test-bench/suites`
- `POST /admin/app/test-bench/suites/{suite_id}/cases`
- `POST /admin/app/test-bench/suites/{suite_id}/runs`
- `GET /admin/app/design-reviews/bootstrap.json`
- `POST /runs`

## New UI-Derived Contract

No new backend JSON schema is introduced. The frontend adds a pure derived setup progress model:

```ts
type WorkflowSetupStepStatus = "complete" | "active" | "blocked";

interface WorkflowSetupStep {
  key:
    | "metadata"
    | "agents"
    | "bindings"
    | "graph"
    | "contracts"
    | "evidence"
    | "validation"
    | "publish"
    | "runtime";
  title: string;
  summary: string;
  href: string;
  status: WorkflowSetupStepStatus;
}
```

## Query Handoff Contract

### User Run Workspace

```http
GET /admin/app/channels/runs?tenant_id=<tenant-id>&workflow_id=<workflow-id>
```

Behavior:

- Prefills the workflow field with `workflow_id`.
- Does not start a run until the user submits the existing form.
- Backend `/runs` validation remains authoritative.

### Design Reviews Workspace

```http
GET /admin/app/design-reviews?tenant_id=<tenant-id>&workflow_version_bundle_id=<bundle-id>
```

Behavior:

- Selects the requested workflow only if it is present in authorized workflow options.
- Falls back to selected session workflow or first authorized option.
- Does not launch a review round until the user submits the existing form.

## Security Notes

- Query parameters carry only safe ids.
- Tenant isolation remains enforced by backend bootstrap endpoints.
- No raw prompt, completion, transcript, provider payload, credential, local path, stack trace, memory, or private channel payload appears in contract responses.
