# UI And QA Contract: Model-Backed Graph Role Executor

Spec 061 does not add an Admin workspace. Browser validation uses existing
health/runtime surfaces plus QA scripts to prove the backend behavior.

## Operator-Visible States

- Deterministic role execution remains the default and existing run inspection
  surfaces continue to show deterministic safe summaries.
- Mocked model-backed role execution records safe runtime step output,
  timeline, gateway attempt, and usage evidence.
- Denied or invalid model-backed execution records safe failure categories
  without exposing raw prompts, completions, credentials, provider payloads,
  memory contents, or raw artifacts.

## QA Evidence Expectations

- `qa061.md` includes setup, seed, automated validation, negative paths,
  redaction checks, troubleshooting, and related files.
- `qa061_ui.md` documents the browser smoke route and expected visible ready
  state.
- `.env.qa061` uses `multi_agent_platform_qa061`, local-principal auth, fake
  provider credentials, and `.data/qa061-artifacts`.
- `qa061_user_guide.md` explains how to validate deterministic default behavior
  and mocked model-backed behavior without live providers.
- `pr_notes.md` documents review focus for redaction, tenant isolation,
  deterministic QA, and gateway-only provider access.

## Curl Coverage Rule

No `curl_testing.md` update is required unless implementation adds or changes a
public/admin/runtime JSON route. The full curl suite still runs after Spec 061
to prove existing APIs remain compatible.
