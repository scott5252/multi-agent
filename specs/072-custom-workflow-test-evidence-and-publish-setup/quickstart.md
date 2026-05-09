# Quickstart: Custom Workflow Test Evidence And Publish Setup

## Goal

Validate that an authorized admin can create required Test Bench evidence from the React Workflow Registry setup flow, launch deterministic evidence, refresh diagnostics, and see publish readiness block or pass from backend-owned evidence.

## Deterministic Setup

1. Start PostgreSQL and apply migrations.
2. Seed the Spec 072 QA tenant, workflow draft, roles, graph, prompt/profile references, and Test Bench fixtures with `scripts/qa/seed_workflow_test_evidence_qa072.py`.
3. Run the FastAPI app in `AUTH_MODE=local_principal` with the Spec 072 QA environment file.
4. Build or serve the React Admin frontend.

## Browser Flow

1. Sign in as the local Acme admin principal.
2. Open React Admin through visible navigation.
3. Navigate to Workflow Registry.
4. Open the QA072 workflow draft.
5. Locate the workflow test evidence section.
6. Create or select the required deterministic suite for the current draft.
7. Add the contract smoke case or another safe required case template.
8. Save the workflow draft and reload.
9. Launch a deterministic evidence run.
10. Refresh evidence until the safe run summary appears.
11. Inspect pass/fail diagnostics and artifact references.
12. Open the publish panel and confirm missing, stale, or failed evidence blocks publish.
13. After current passing evidence exists, validate and publish.

## Expected Results

- The evidence section never requires copied workflow, draft, revision, suite, run, or browser URL ids.
- Missing evidence blocks publish and links to the evidence section.
- Stale evidence appears after workflow draft revision changes.
- Failed evidence shows safe diagnostics and blocks publish.
- Current passing deterministic evidence satisfies the publish gate.
- Raw transcripts, prompts, completions, provider/tool payloads, credentials, local paths, private payloads, stack traces, and unauthorized tenant labels do not appear.

## Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/072-custom-workflow-test-evidence-and-publish-setup
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa072-after-spec
```

## Curl Coverage Rule

Review `curl_testing.md` before validation. Add or update commands if Spec 072 adds or behaviorally changes Test Bench, workflow setup, evidence, or publish route families. Record the coverage decision in Spec 072 status artifacts.
