# PR Notes: Spec 065 - Agent Communication Graph Contracts And Projections

## Summary

Spec 065 adds backend-owned Agent Communication Graph JSON contracts for
workflow drafts and published workflow bundles. The implementation is additive:
existing workflow graph previews still behave as before, while the new graph
routes expose richer agent/sub-agent/tool/join/approval/handoff/terminal
metadata for the React viewer planned in Spec 066.

## Reviewer Focus

- Verify the new graph routes reuse existing workflow registry authorization and
  cross-tenant denial behavior.
- Verify graph labels, summaries, references, badges, and accessibility strings
  are schema-validated as safe text.
- Verify published graph projection loads the compiled bundle document when it
  is available and returns an honest partial state when it is not.
- Verify `curl_testing.md` includes draft and published graph route coverage.
- Verify no migration was added for Spec 065.

## Validation Evidence

- Focused backend tests: `tests/unit/api/test_admin_agent_graph_schemas.py`,
  `tests/unit/admin/test_agent_graph.py`,
  `tests/integration/api/test_admin_agent_graph_api.py`, and workflow registry
  contract assertions.
- Generated TypeScript: `frontend/admin/src/api/generated/reactAdminApi.ts`.
- QA docs: `qa065.md`, `qa065_ui.md`, `.env.qa065`, and
  `qa065_user_guide.md`.
