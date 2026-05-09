# QA069 User Guide: Spec 069 - Workflow Document Authoring Contracts And Mutation APIs

## Detailed Overview
1. QA069 gives authorized admins a browser-facing contract for complete workflow document saves.
2. The durable document is still the canonical `WorkflowDraftDocument`.
3. The React builder now receives that canonical document in its draft editor state.
4. The React builder also receives safe section summaries for metadata, roles, references, contracts, graph, joins, approvals, subworkflows, tests, annotations, and publish readiness.
5. Save requests include revision, idempotency key, safe client context, metadata, and the complete document.
6. Accepted saves append a durable workflow draft revision.
7. Exact duplicate saves replay without creating another revision.
8. Stale saves return safe recovery guidance.
9. Invalid documents return validation findings mapped to sections and field paths.
10. Lower-level workflow registry routes remain supported.
11. Raw prompt text remains outside this general workflow save diagnostic path.
12. Raw completions remain outside this general workflow save diagnostic path.
13. Credential values remain outside responses, audit summaries, docs, screenshots, and curl evidence.
14. Provider payloads remain outside responses, audit summaries, docs, screenshots, and curl evidence.
15. Tool payloads remain outside responses, audit summaries, docs, screenshots, and curl evidence.
16. Private channel content remains outside responses, audit summaries, docs, screenshots, and curl evidence.
17. Local filesystem paths remain outside responses, audit summaries, docs, screenshots, and curl evidence.
18. The primary reviewer route is `/admin/app/workflows`.
19. The primary JSON load route is `/admin/app/workflows/drafts/{workflow_draft_id}/detail.json`.
20. The primary mutation route is `/admin/app/workflows/drafts/{workflow_draft_id}/save`.
21. The QA tenant is Acme.
22. The cross-tenant negative tenant is Globex.
23. The deterministic draft ID is `69696969-6669-4669-8669-000000000069`.
24. The deterministic save payload is `.data/qa069-artifacts/workflow-document-save.json`.
25. The deterministic environment file is `.env.qa069`.
26. The deterministic artifact root is `.data/qa069-artifacts`.
27. The deterministic screenshot root is `output/playwright/qa069_ui`.
28. The deterministic curl output root is `.data/curl_test_runs/qa069-after-spec`.
29. Use local-principal auth for all QA069 checks.
30. Do not use live provider, Telegram, Auth0, or connector calls for QA069.

## Who Should Use This Guide
This guide is for product reviewers, QA reviewers, and engineers validating the browser workflow setup path.
Reviewers do not need to edit database rows by hand.
Reviewers should be comfortable running local commands from the repository root.
Reviewers should be able to sign in with local-principal auth.
Reviewers should stop and ask for engineering help if protected raw data appears.

## Manual QA Prerequisites
The repository dependencies must be installed with `uv sync`.
Docker must be available for the local PostgreSQL container.
The QA database must be migrated to Alembic head.
The `.env` file must be copied from `.env.qa069`.
The QA069 seed script must run successfully.
The API must be reachable at `http://127.0.0.1:8000`.
The browser must allow local cookies for local-principal login.

## Step-by-Step Manual QA
31. Copy `.env.qa069` to `.env`.
32. Start Postgres with Docker Compose.
33. Run Alembic migrations to head.
34. Run `scripts/qa/seed_workflow_document_authoring_qa069.py`.
35. Confirm the seed script prints the QA069 workflow draft ID.
36. Start FastAPI on `127.0.0.1:8000`.
37. Open `http://127.0.0.1:8000/auth/local-login`.
38. Choose `tenant-admin-acme`.
39. Navigate to `/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111`.
40. Confirm the workflow registry appears.
41. Confirm the workflow builder appears.
42. Confirm the draft revision appears.
43. Confirm the section count appears in draft facts.
44. Confirm the section rail or section summaries appear.
45. Confirm the graph panel renders.
46. Confirm the validation panel renders.
47. Confirm the publish panel renders.
48. Edit the workflow name.
49. Edit the workflow description.
50. Confirm the dirty state appears.
51. Open the browser Network panel.
52. Click `Save draft`.
53. Confirm the save response has status `accepted`.
54. Confirm the save response has a new revision.
55. Confirm the save request body includes `document.workflow_key`.
56. Confirm the save request body includes `document.roles`.
57. Confirm the save request body includes `document.nodes`.
58. Confirm the save request body includes `document.edges`.
59. Confirm the save request body includes `revision`.
60. Confirm the save request body includes `idempotency_key`.
61. Confirm the save response includes safe validation summary data.
62. Confirm the save response includes an audit reference.
63. Confirm the save response does not include raw prompt bodies.
64. Confirm the save response does not include raw completion text.
65. Confirm the save response does not include provider payloads.
66. Confirm the save response does not include tool payloads.
67. Confirm the save response does not include credential values.
68. Confirm the save response does not include local filesystem paths.
69. Click `Simulate stale save`.
70. Confirm the stale response is visible.
71. Confirm the stale response includes current revision context.
72. Confirm the stale response does not overwrite the edited document.
73. Reload the page.
74. Confirm the saved name remains durable.
75. Confirm the saved description remains durable.
76. Confirm the section note or saved metadata remains durable when using API evidence.
77. Run the API full document save check from `qa069.md`.
78. Run the idempotent replay API check from `qa069.md`.
79. Run the stale conflict API check from `qa069.md`.
80. Run the invalid graph API check from `qa069.md`.
81. Run the cross-tenant API check from `qa069.md`.
82. Run the redaction scan from `qa069.md`.
83. Capture a full-page screenshot.
84. Record the screenshot path.
85. Run generated TypeScript freshness.
86. Run frontend typecheck.
87. Run workflow component tests.
88. Run focused backend tests.
89. Run QA document validation.
90. Run Playwright smoke.
91. Run multi-agent curl regression.
92. Record any failures with response path and command.
93. Do not copy raw protected payloads into reviewer notes.
94. Mark the manual QA pass only after all relevant checks pass.

## Expected Results
95. The React builder load route returns a draft object.
96. The draft object includes `document`.
97. The draft object includes `section_summaries`.
98. The save request accepts a full document.
99. The save request accepts a safe client context.
100. The save request accepts a change summary.
101. The save route enforces the base revision token.
102. The save route enforces a required idempotency key.
103. The save route persists roles.
104. The save route persists prompt and profile references as references only.
105. The save route persists skill installation references.
106. The save route persists contracts.
107. The save route persists graph nodes.
108. The save route persists graph edges.
109. The save route persists join policies.
110. The save route persists approval gates.
111. The save route persists subworkflow references.
112. The save route persists required test requirements.
113. The save route persists editor annotations.
114. Exact duplicate saves return `idempotent_replay`.
115. Exact duplicate saves do not add duplicate revisions.
116. Same-key different-payload saves return `validation_error`.
117. Stale saves return `stale_conflict`.
118. Invalid graph saves return `validation_error`.
119. Invalid graph findings map to the graph section.
120. Duplicate or malformed documents return safe findings.
121. Cross-tenant reads are denied.
122. Cross-tenant writes are denied.
123. Tenant admins cannot mutate platform drafts without authorization.
124. Platform admins retain authorized platform scope behavior.
125. Mutation summaries are safe.
126. Audit references are safe.
127. Field paths are safe.
128. Graph element IDs are safe when present.
129. Browser screenshots are safe.
130. Curl output is safe.
131. Generated TypeScript contracts are fresh.
132. Backend contract tests pass.
133. Backend integration tests pass.
134. Backend service tests pass.
135. Frontend workflow tests pass.
136. Playwright smoke passes.
137. The curl regression passes.
138. The QA document validator passes.
139. The final evidence tells a reviewer what changed and how to verify it.
140. The feature is ready to support Spec 070 graph controls.

## Evidence To Capture
Capture the API detail response path.
Capture the accepted save response path.
Capture the replay response path.
Capture the stale conflict response path.
Capture the invalid graph response path.
Capture the cross-tenant denial response path.
Capture a full-page workflow UI screenshot.
Capture the Playwright output directory.
Capture the curl regression output directory.
Record the exact branch name in reviewer notes.

## Security And Redaction Checks
Search API output for raw prompt text.
Search API output for raw completion text.
Search API output for provider payload text.
Search API output for tool payload text.
Search API output for credential-like text.
Search API output for stack trace text.
Search API output for local filesystem paths.
Search browser screenshots for the same protected markers.
Treat any protected marker as a failed QA result.

## Tenant Isolation Checks
Use `tenant-admin-acme` for the positive path.
Use `tenant-admin-globex` for the cross-tenant negative path.
Confirm Globex cannot read the Acme draft detail route.
Confirm Globex cannot save the Acme draft.
Confirm denial responses do not contain Acme document summaries.
Confirm platform scope is not accidentally introduced into the tenant draft.

## Troubleshooting
141. If the workflow draft is missing, rerun the QA069 seed script.
142. If the route returns 403 for Acme, confirm the `tenant-admin-acme` principal was selected.
143. If the route returns 403 for Globex, that is expected for cross-tenant negative checks.
144. If the save returns stale unexpectedly, reload the page and read the latest revision.
145. If replay returns accepted, confirm the exact same idempotency key and payload were reused.
146. If idempotency conflict does not appear, confirm the key is reused while the payload changes.
147. If invalid graph saves are accepted, inspect Pydantic validation and authoring validation mapping.
148. If a response contains raw prompt text, stop and treat it as a redaction defect.
149. If a response contains provider payload text, stop and treat it as a redaction defect.
150. If a response contains tool payload text, stop and treat it as a redaction defect.
151. If generated types are stale, run the generator and inspect the diff.
152. If frontend typecheck fails, inspect the generated `WorkflowDraftSaveRequest` type.
153. If Vitest fails, inspect the workflow builder save payload assertion.
154. If Playwright fails at login, clear the local-principal cookie.
155. If Playwright fails at workflow text, confirm React assets were built or dev-mode settings are correct.
156. If curl regression fails, keep `.data/curl_test_runs/qa069-after-spec` for review.
157. If mypy fails, inspect the route and service helper signatures.
158. If Ruff format fails, run the project formatter only after reviewing unrelated user edits.
159. If database migrations fail, confirm `0023_workflow_document_authoring` follows `0022_runtime_interactions`.
160. If evidence is inconclusive, rerun only the failed check and record the exact command.
161. If protected markers appear in screenshots, delete the screenshot from evidence and file a defect.
162. If the UI appears empty, confirm the Acme tenant ID in the URL.
163. If the QA payload file is missing, rerun the seed script.
164. If the save payload uses revision `1` after a prior save, reset the QA database or update the payload revision.
165. If the server logs include stack traces, preserve `/tmp/qa069-ui-api.log` for debugging.
166. If this guide and `qa069.md` disagree, follow `qa069.md` for command syntax.
167. If a reviewer needs route details, use `contracts/workflow-document-authoring.md`.
168. If a reviewer needs implementation details, use `implementation_notes.md`.
169. If a reviewer needs PR focus areas, use `pr_notes.md`.
170. If all checks pass, record the date, branch, commit state, and evidence paths in the acceptance notes.
