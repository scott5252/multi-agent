# PR Notes: Spec 066 - React Agent Graph Viewer For Workflow Drafts And Versions

## Summary

Spec 066 adds a read-only React Admin Agent Graph Viewer for workflow drafts and published workflow versions. The viewer consumes the Spec 065 backend Agent Communication Graph JSON, renders a React Flow canvas, preserves keyboard-readable node and edge list alternatives, and exposes safe selected-item details without replacing existing workflow builder, JSON inspector, validation, publish, revision, or sharing panels.

## Reviewer Focus

- Verify generated React Admin API types now include `AgentCommunicationGraph`.
- Verify draft and published graph fetch helpers use same-origin credentials and safe error handling.
- Verify `AgentGraphPanel` uses only backend graph payloads and creates no synthetic production graph records.
- Verify node and edge lists provide keyboard selection parity with canvas selection.
- Verify visible copy does not expose raw prompts, completions, credentials, provider payloads, private payloads, memory contents, or raw tool output.
- Verify desktop and mobile Playwright screenshots show non-overlapping graph, list, and detail content.

## Validation Evidence

- Focused frontend tests: `AgentGraphPanel` and `WorkflowBuilderPage`.
- Generated contracts: `scripts/frontend/generate_admin_react_types.py --check`.
- Browser QA: `output/playwright/qa066_ui/qa066-agent-graph-desktop.png` and `output/playwright/qa066_ui/qa066-agent-graph-mobile.png`.
- QA docs: `qa066.md`, `qa066_ui.md`, `.env.qa066`, and `qa066_user_guide.md`.
