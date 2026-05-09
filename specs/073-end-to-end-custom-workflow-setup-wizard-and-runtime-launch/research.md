# Research: End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Existing Surfaces Reviewed

- Workflow Builder already owns create, save, validation, publish, role editing, graph topology, joins, contracts, prompt/profile binding, and test evidence setup.
- User Run workspace starts retained `/runs` invocations with a workflow id string.
- Design Reviews workspace loads authorized published workflow options and launches coordinator rounds with selected workflow bundle ids.
- Agent graph panels already provide visual and keyboard-readable graph summaries for drafts and published versions.

## Decisions

- **Decision**: Implement a checklist inside Workflow Builder instead of a separate wizard route.
  - **Rationale**: Advanced editors remain visible and durable behavior stays in the existing builder.
  - **Alternatives Considered**: A separate route would duplicate save and readiness state.

- **Decision**: Provide a visible three-agent starter action.
  - **Rationale**: Clean tenants need a fast path to a realistic multi-agent workflow while retaining full editability.
  - **Alternatives Considered**: Requiring manual role/node creation for every Playwright run is slower and more brittle.

- **Decision**: Derive checklist progress in the browser but keep publish/evidence/validation truth backend-owned.
  - **Rationale**: The browser can guide; it cannot certify readiness.
  - **Alternatives Considered**: A new backend progress endpoint is unnecessary because required backend readiness objects already exist.

- **Decision**: Use safe query parameters for runtime and Design Review handoff.
  - **Rationale**: Existing Admin surfaces can accept a preselected workflow id without new route families.
  - **Alternatives Considered**: Copying ids manually violates the roadmap requirement.

## Open Questions Resolved

- No new Alembic migration is needed.
- No generated TypeScript contract change is needed.
- No updates to `curl_testing.md` are required because no public JSON route family changed.
- Playwright must still prove the browser path, including clean login and visible UI controls.
