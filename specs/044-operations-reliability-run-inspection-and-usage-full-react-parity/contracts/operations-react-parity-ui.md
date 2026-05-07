# UI Contract: Operations, Reliability, Run Inspection, And Usage React Parity

## React Routes

- `/admin/app/operations`
- `/admin/app/operations.json`
- `/admin/app/operations/runs/{workflow_run_id}.json`
- `/admin/app/operations/export`
- `/admin/app/usage`
- `/admin/app/usage/bootstrap.json`
- `/admin/app/usage/events.json`
- `/admin/app/usage/exports`
- `/admin/app/usage/exports/{usage_export_request_id}.json`

## Legacy Browser Route Mapping

| Legacy route | Behavior | Destination |
| --- | --- | --- |
| `GET /admin/operations` | Redirect | `/admin/app/operations` |
| `GET /admin/reliability/ui/` | Redirect | `/admin/app/operations?panel=reliability` |
| `GET /admin/reliability/ui/breakers` | Redirect | `/admin/app/operations?panel=breakers` |
| `GET /admin/reliability/ui/dead-letters` | Redirect | `/admin/app/operations?panel=dead-letters` |
| `GET /admin/runs` | Redirect | `/admin/app/operations?panel=runs` |
| `GET /admin/runs/{run_id}` | Redirect | `/admin/app/operations?run_id={run_id}` |
| `GET /admin/runs/{run_id}/replay` | Redirect | `/admin/app/operations?run_id={run_id}&panel=replay` |
| `GET /runs` | Redirect | `/admin/app/channels` |
| `GET /runs/new` | Redirect | `/admin/app/channels` |
| `GET /runs/{run_id}` | Redirect | `/admin/app/channels/runs/{run_id}` |
| `GET /admin/usage` | Redirect | `/admin/app/usage` |
| `GET /admin/usage/exports/{export_id}` | Redirect | `/admin/app/usage/exports/{export_id}` |

## Safe Data Rules

- React displays operational summaries, not raw logs.
- React displays run timeline summaries, not raw prompts or completions.
- React displays artifact and export metadata, not raw payloads or storage paths.
- React displays reliability mutation results, not raw dead-letter payloads.
- Unauthorized old links fail closed and do not reveal data existence.
