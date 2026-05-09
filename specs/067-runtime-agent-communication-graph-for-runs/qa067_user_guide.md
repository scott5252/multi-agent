# QA067 User Guide: Spec 067 - Runtime Agent Communication Graph For Runs

## Detailed Overview

1. QA067 adds a read-only runtime communication graph to the operations workbench.
2. The graph is for authorized admin inspection of a specific workflow run.
3. The graph is backend-owned and is not editable from the browser.
4. The graph uses existing durable runtime evidence only.
5. No new interaction evidence table is required for this spec.
6. Runtime topology comes from the execution bundle and published workflow version.
7. Runtime node status comes from existing run step rows.
8. Runtime edge status is inferred from source and target run steps plus handoffs.
9. Timeline events are rendered only as safe references.
10. Handoffs are rendered only as safe references and status summaries.
11. Approval gates are rendered only as safe references and status summaries.
12. Tool and side-effect evidence is rendered only as safe summaries.
13. The route is `GET /admin/runs/{workflow_run_id}/agent-graph`.
14. The route requires local-principal or Auth0-shaped admin authorization.
15. Tenant admins can inspect only runs in their tenant.
16. Platform admins can inspect tenant runs when they provide the tenant scope.
17. Cross-tenant requests must fail closed.
18. Missing runs must return a safe not-found problem.
19. Partial evidence must remain truthful.
20. Partial evidence must not invent nodes or edges.
21. Unmapped evidence is counted at graph level.
22. Unmapped evidence is not transformed into synthetic topology.
23. The React workbench keeps the existing timeline panel.
24. The React workbench keeps reliability, export, and log panels.
25. The runtime graph appears as an additive panel after timeline evidence.
26. The canvas is supported by keyboard-readable node and edge lists.
27. Selecting a list item shows the same safe details as selecting the canvas item.
28. Status badges use visible text and do not rely on color alone.
29. Edge details can include references just like node details.
30. The QA seed creates one representative Acme run.
31. The seeded run ID is `67676767-6666-4767-8767-000000000067`.
32. The seeded tenant ID is `11111111-1111-1111-1111-111111111111`.
33. The seeded workflow version ID is `67676767-4444-4767-8767-000000000067`.
34. The seeded run includes a succeeded coordinator step.
35. The seeded run includes a retry-scheduled specialist step.
36. The seeded run includes a paused approval step.
37. The seeded run includes a queued terminal step.
38. The seeded run includes timeline references.
39. The seeded run includes a handoff reference.
40. The seeded run includes a read-only side-effect reference.
41. The seeded run includes an approval gate reference.
42. The seeded run includes one graph-level partial evidence item.
43. The expected graph state can be partial because graph-level evidence is unmapped.
44. The graph should still show mapped runtime nodes and edges.
45. Safe graph copy must never include raw prompts.
46. Safe graph copy must never include raw completions.
47. Safe graph copy must never include provider payloads.
48. Safe graph copy must never include private channel messages.
49. Safe graph copy must never include memory contents.
50. Safe graph copy must never include raw external tool payloads.
51. Safe graph copy must never include secrets or secret values.
52. Safe graph copy must never include stack traces.
53. Safe graph copy must never include local user filesystem paths.
54. Safe graph copy may include stable IDs.
55. Safe graph copy may include statuses.
56. Safe graph copy may include timestamps.
57. Safe graph copy may include safe summaries.
58. Safe graph copy may include links to safe admin surfaces.
59. The desktop screenshot must show the graph, lists, and selected detail.
60. The mobile screenshot must show stacked, readable graph regions.

## Step-by-Step Manual QA

1. Start Docker Desktop or ensure Docker is already running.
2. Start PostgreSQL with `docker compose up -d postgres`.
3. Copy `specs/067-runtime-agent-communication-graph-for-runs/.env.qa067` to `.env`.
4. Run `uv sync` if dependencies are not current.
5. Run `uv run alembic upgrade head`.
6. Run `uv run python scripts/qa/seed_runtime_agent_graph_qa067.py`.
7. Confirm the seed prints the Acme tenant ID.
8. Confirm the seed prints the QA067 workflow run ID.
9. Confirm `.data/qa067-artifacts/evidence/qa067-runtime-agent-graph-seed.json` exists.
10. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.
11. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations%3Frun_id%3D67676767-6666-4767-8767-000000000067%26tenant_id%3D11111111-1111-1111-1111-111111111111`.
12. Select the `tenant-admin-acme` local principal.
13. Wait for the operations page to load.
14. Confirm the page heading says `Operations`.
15. Confirm the operations summary cards still render.
16. Confirm the run timeline panel still renders.
17. Confirm the runtime graph panel appears after timeline evidence.
18. Confirm the graph panel heading says `Runtime run communication`.
19. Confirm the graph summary mentions runtime agent graph status counts.
20. Confirm a `partial` badge appears when the seeded graph-level evidence is unmapped.
21. Confirm the canvas is visible and nonblank.
22. Confirm the node list is visible below or beside the canvas.
23. Confirm the edge list is visible below or beside the canvas.
24. Select the `Coordinator` node from the node list.
25. Confirm the selected detail title is `Coordinator`.
26. Confirm the selected detail status is `succeeded`.
27. Confirm coordinator references include a run step reference.
28. Confirm coordinator references include safe timeline or tool evidence when present.
29. Select the `Specialist` node from the node list.
30. Confirm the selected detail title is `Specialist`.
31. Confirm the selected detail status is `retry_scheduled`.
32. Confirm the selected detail summary is safe and does not show raw payloads.
33. Select the `Approval` node from the node list.
34. Confirm the selected detail status is `paused`.
35. Confirm approval references include a safe approval status.
36. Select the coordinator-to-specialist edge from the edge list.
37. Confirm the selected detail is an edge detail.
38. Confirm the edge has a runtime status badge.
39. Confirm the edge references include the safe handoff summary.
40. Select the specialist-to-approval edge from the edge list.
41. Confirm the edge reflects retry or waiting evidence truthfully.
42. Resize the browser to a mobile width around `390x900`.
43. Confirm graph regions stack without horizontal overflow.
44. Confirm list buttons wrap long status text.
45. Confirm selected detail text does not overlap following panels.
46. Sign out or open a fresh private browser session.
47. Sign in as `tenant-admin-globex`.
48. Open the same Acme run URL.
49. Confirm the UI does not reveal Acme graph details.
50. Confirm the API returns a safe forbidden response.
51. Run the direct success API check with `tenant-admin-acme`.
52. Run the direct denied API check with `tenant-admin-globex`.
53. Run the focused unit and integration tests.
54. Run the focused React tests.
55. Run the generated TypeScript check.
56. Run the full Spec QA manifest.
57. Run the Playwright manifest with process startup.
58. Review desktop screenshot output.
59. Review mobile screenshot output.
60. Run the multi-agent curl regression.

## Expected Results

1. The API returns `200` for the Acme tenant admin graph request.
2. The API returns `403` for the Globex tenant admin graph request.
3. The API returns `404` for an authorized request to a missing run.
4. The graph response has `source` equal to `runtime_run`.
5. The graph response has `provenance.workflow_run_id` equal to the seeded run.
6. The graph response has `provenance.run_bundle_id`.
7. The graph response has `provenance.evidence_counts.run_steps`.
8. The graph response has `provenance.evidence_counts.timeline_events`.
9. The graph response has `provenance.evidence_counts.handoffs`.
10. The graph response has `provenance.evidence_counts.side_effects`.
11. The graph response has `provenance.evidence_counts.approvals`.
12. The coordinator node status is `succeeded`.
13. The specialist node status is `retry_scheduled`.
14. The approval node status is `paused`.
15. The done node status is `queued`.
16. Edges include runtime statuses.
17. Edge details include references when handoff evidence exists.
18. Node details include run-step references.
19. Node details include timeline references when mapped.
20. Node details include approval references when mapped.
21. Node details include tool-call references when mapped.
22. The workbench timeline remains visible.
23. Reliability panels remain visible.
24. Export controls remain visible.
25. Redacted log panels remain visible.
26. The graph panel loading state is truthful.
27. The graph panel error state is truthful.
28. The graph panel partial state is truthful.
29. The graph panel empty state remains supported.
30. The graph canvas has an accessible label.
31. Node list buttons have readable names.
32. Edge list buttons have readable names.
33. Selected details update when list items are clicked.
34. Desktop screenshot is legible.
35. Mobile screenshot is legible.
36. No raw prompt text appears.
37. No raw completion text appears.
38. No provider payload text appears.
39. No private channel message text appears.
40. No memory content text appears.
41. No raw tool payload text appears.
42. No secret value appears.
43. No traceback appears.
44. No local user filesystem path appears.
45. Curl section `16.5a` passes.
46. Curl section `16.8` passes.
47. Generated React types remain fresh.
48. Frontend typecheck passes.
49. Frontend tests pass.
50. Backend focused tests pass.

## Troubleshooting

1. If the graph panel is missing, confirm the operations URL includes `run_id`.
2. If the graph panel is missing, confirm the operations URL includes `tenant_id`.
3. If the API returns `404`, rerun `scripts/qa/seed_runtime_agent_graph_qa067.py`.
4. If the API returns `403` for Acme, confirm the local principal is `tenant-admin-acme`.
5. If the API returns `403` for platform admin, add the Acme `tenant_id` query parameter.
6. If the graph is empty, inspect the runtime execution bundle topology JSON.
7. If nodes are unavailable, inspect `runtime_run_steps` for matching `step_key` values.
8. If timeline references are missing, inspect `runtime_timeline_events`.
9. If handoff references are missing, inspect `runtime_handoff_envelopes`.
10. If approval references are missing, inspect `runtime_approval_gates`.
11. If tool references are missing, inspect `runtime_side_effect_intents`.
12. If the graph is partial, inspect graph badges for the exact partial reason.
13. If text appears unsafe, check `safe_agent_graph_text` blocked markers.
14. If generated types are stale, run `uv run python scripts/frontend/generate_admin_react_types.py`.
15. If React tests fail on edge references, confirm edge objects include `status` and `references`.
16. If Playwright cannot log in, confirm `LOCAL_PRINCIPAL_CATALOG_JSON` in `.env.qa067`.
17. If Playwright sees a blank canvas, confirm `@xyflow/react` assets are built.
18. If mobile text overlaps, inspect `.agent-graph-layout` and list button wrapping.
19. If curl graph checks fail, confirm `seed_runtime_audit_fixture` ran after section `4.1`.
20. If curl denial checks fail, confirm Globex uses `tenant-admin-globex`.
21. If Docker is unavailable, start Docker Desktop and rerun the manifest.
22. If the QA database has stale rows, drop and recreate `multi_agent_platform_qa067`.
23. If static assets are stale, run `npm --prefix frontend/admin run build`.
24. If mypy fails, confirm runtime schema fields and generated contracts are aligned.
25. If route ordering breaks, ensure `/agent-graph` is registered before the generic run page redirect.
