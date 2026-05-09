# QA068 User Guide: Spec 068 - Durable Agent Interaction Evidence And Replay Graph

## Detailed Overview
QA068 adds durable interaction evidence so a workflow run can be replayed as safe communication between graph nodes. The UI remains the operations workbench runtime graph, but selected edges now show replay references such as handoff, result return, approval pause, and unmapped replay evidence counts.
The feature is designed for reviewers who need to understand what happened in a run without seeing raw prompts, completions, credentials, private messages, provider responses, memory content, raw tool output, or stack traces.

## Who Should Use This Guide
Use this guide if you are validating QA068 as a product reviewer, QA reviewer, engineering reviewer, or security reviewer. You do not need production access. You only need the local repository, Docker PostgreSQL, and the local-principal login page.

## Manual QA Prerequisites
```bash
cp specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_runtime_interaction_evidence_qa068.py
```
Expected: the seed script prints the QA068 run ID and evidence path.

## Step-by-Step Manual QA
1. Open http://127.0.0.1:8000/auth/local-login and sign in as tenant-admin-acme.
Expected: step 1 shows only authorized QA068 safe-summary evidence.
2. Open the operations workbench for run 68686868-6666-4868-8868-000000000068.
Expected: step 2 shows only authorized QA068 safe-summary evidence.
3. Select the Coordinator to Specialist edge and read Replay 1: handoff.
Expected: step 3 shows only authorized QA068 safe-summary evidence.
4. Review replay graph behavior and safe summaries for checklist item 4.
Expected: step 4 shows only authorized QA068 safe-summary evidence.
5. Review replay graph behavior and safe summaries for checklist item 5.
Expected: step 5 shows only authorized QA068 safe-summary evidence.
6. Review replay graph behavior and safe summaries for checklist item 6.
Expected: step 6 shows only authorized QA068 safe-summary evidence.
7. Review replay graph behavior and safe summaries for checklist item 7.
Expected: step 7 shows only authorized QA068 safe-summary evidence.
8. Review replay graph behavior and safe summaries for checklist item 8.
Expected: step 8 shows only authorized QA068 safe-summary evidence.
9. Review replay graph behavior and safe summaries for checklist item 9.
Expected: step 9 shows only authorized QA068 safe-summary evidence.
10. Review replay graph behavior and safe summaries for checklist item 10.
Expected: step 10 shows only authorized QA068 safe-summary evidence.
11. Review replay graph behavior and safe summaries for checklist item 11.
Expected: step 11 shows only authorized QA068 safe-summary evidence.
12. Review replay graph behavior and safe summaries for checklist item 12.
Expected: step 12 shows only authorized QA068 safe-summary evidence.
13. Review replay graph behavior and safe summaries for checklist item 13.
Expected: step 13 shows only authorized QA068 safe-summary evidence.
14. Review replay graph behavior and safe summaries for checklist item 14.
Expected: step 14 shows only authorized QA068 safe-summary evidence.
15. Review replay graph behavior and safe summaries for checklist item 15.
Expected: step 15 shows only authorized QA068 safe-summary evidence.
16. Review replay graph behavior and safe summaries for checklist item 16.
Expected: step 16 shows only authorized QA068 safe-summary evidence.
17. Review replay graph behavior and safe summaries for checklist item 17.
Expected: step 17 shows only authorized QA068 safe-summary evidence.
18. Review replay graph behavior and safe summaries for checklist item 18.
Expected: step 18 shows only authorized QA068 safe-summary evidence.
19. Review replay graph behavior and safe summaries for checklist item 19.
Expected: step 19 shows only authorized QA068 safe-summary evidence.
20. Review replay graph behavior and safe summaries for checklist item 20.
Expected: step 20 shows only authorized QA068 safe-summary evidence.
21. Review replay graph behavior and safe summaries for checklist item 21.
Expected: step 21 shows only authorized QA068 safe-summary evidence.
22. Review replay graph behavior and safe summaries for checklist item 22.
Expected: step 22 shows only authorized QA068 safe-summary evidence.
23. Review replay graph behavior and safe summaries for checklist item 23.
Expected: step 23 shows only authorized QA068 safe-summary evidence.
24. Review replay graph behavior and safe summaries for checklist item 24.
Expected: step 24 shows only authorized QA068 safe-summary evidence.
25. Review replay graph behavior and safe summaries for checklist item 25.
Expected: step 25 shows only authorized QA068 safe-summary evidence.
26. Review replay graph behavior and safe summaries for checklist item 26.
Expected: step 26 shows only authorized QA068 safe-summary evidence.
27. Review replay graph behavior and safe summaries for checklist item 27.
Expected: step 27 shows only authorized QA068 safe-summary evidence.
28. Review replay graph behavior and safe summaries for checklist item 28.
Expected: step 28 shows only authorized QA068 safe-summary evidence.
29. Review replay graph behavior and safe summaries for checklist item 29.
Expected: step 29 shows only authorized QA068 safe-summary evidence.
30. Review replay graph behavior and safe summaries for checklist item 30.
Expected: step 30 shows only authorized QA068 safe-summary evidence.
31. Review replay graph behavior and safe summaries for checklist item 31.
Expected: step 31 shows only authorized QA068 safe-summary evidence.
32. Review replay graph behavior and safe summaries for checklist item 32.
Expected: step 32 shows only authorized QA068 safe-summary evidence.
33. Review replay graph behavior and safe summaries for checklist item 33.
Expected: step 33 shows only authorized QA068 safe-summary evidence.
34. Review replay graph behavior and safe summaries for checklist item 34.
Expected: step 34 shows only authorized QA068 safe-summary evidence.
35. Review replay graph behavior and safe summaries for checklist item 35.
Expected: step 35 shows only authorized QA068 safe-summary evidence.
36. Review replay graph behavior and safe summaries for checklist item 36.
Expected: step 36 shows only authorized QA068 safe-summary evidence.
37. Review replay graph behavior and safe summaries for checklist item 37.
Expected: step 37 shows only authorized QA068 safe-summary evidence.
38. Review replay graph behavior and safe summaries for checklist item 38.
Expected: step 38 shows only authorized QA068 safe-summary evidence.
39. Review replay graph behavior and safe summaries for checklist item 39.
Expected: step 39 shows only authorized QA068 safe-summary evidence.
40. Review replay graph behavior and safe summaries for checklist item 40.
Expected: step 40 shows only authorized QA068 safe-summary evidence.
## Expected Results
Expected: result 1 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 2 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 3 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 4 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 5 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 6 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 7 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 8 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 9 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 10 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 11 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 12 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 13 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 14 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 15 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 16 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 17 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 18 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 19 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
Expected: result 20 confirms durable replay references, tenant isolation, redaction, or responsive graph layout.
## Evidence To Capture
Capture evidence 1 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 2 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 3 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 4 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 5 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 6 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 7 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 8 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 9 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 10 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 11 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 12 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 13 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 14 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 15 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 16 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 17 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 18 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 19 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
Capture evidence 20 under /tmp/qa068-evidence or output/playwright/qa068_ui with no raw payloads.
## Security And Redaction Checks
Expected: redaction check 1 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 2 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 3 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 4 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 5 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 6 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 7 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 8 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 9 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 10 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 11 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 12 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 13 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 14 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 15 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 16 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 17 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
Expected: redaction check 18 finds no raw prompt, completion, provider response, credential, private payload, memory content, stack trace, or raw tool output.
## Tenant Isolation Checks
Expected: tenant isolation check 1 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 2 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 3 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 4 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 5 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 6 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 7 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 8 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 9 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 10 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 11 confirms Globex cannot see Acme replay evidence.
Expected: tenant isolation check 12 confirms Globex cannot see Acme replay evidence.
## Troubleshooting
Troubleshooting 1: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 2: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 3: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 4: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 5: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 6: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 7: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 8: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 9: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 10: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 11: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 12: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 13: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 14: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 15: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 16: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 17: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 18: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 19: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
Troubleshooting 20: rerun deterministic setup, inspect /tmp/qa068-api.log, keep screenshots, and avoid copying sensitive payloads.
