# PR Review Notes: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Reviewer Focus

- Verify that `GraphExecutionService` executes published workflow bundle graphs
  without adding a Spec 020 migration.
- Verify that ready role nodes are executed concurrently while database writes
  remain sequential and durable.
- Verify that join policies cover `all_success`, `quorum`, `first_success`,
  and `manual_resolution`.
- Verify that restart/resume reconstructs succeeded nodes from persisted run
  steps before scheduling new work.
- Verify that tenant mismatch between a run and a published bundle fails
  closed.
- Verify that timeline events, checkpoints, handoffs, side-effect intents, and
  final outputs store safe summaries or references only.

## Implementation Notes

- New graph runtime code lives in
  `src/multi_agent_platform/runtime/orchestration/graph_execution.py`.
- Deterministic role execution lives in
  `src/multi_agent_platform/runtime/orchestration/graph_roles.py`.
- Graph redaction helpers live in
  `src/multi_agent_platform/runtime/orchestration/graph_redaction.py`.
- Runtime repository helpers were added to
  `src/multi_agent_platform/db/repositories/runtime_orchestration.py`.
- The orchestration worker now delegates claimed runs to
  `GraphExecutionService`.
- QA020 uses mock role execution only and does not call real providers or
  external tools.

## Compatibility Notes

- Spec 020 intentionally reuses existing runtime tables for runs, steps,
  checkpoints, handoffs, side-effect intents, approvals, timeline events, and
  execution bundles.
- No Alembic revision is expected for this feature.
- Published workflow graph documents are loaded from existing workflow version
  bundle metadata.
- Browser review uses existing admin shell, workflow studio, run inspection,
  and operations pages; no new UI route is introduced.

## Required Evidence

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/020-workflow-graph-execution-parallel-sub-agent-runtime
uv run pytest --no-cov tests/unit/runtime/orchestration/test_graph_execution.py tests/unit/runtime/orchestration/test_graph_roles.py tests/unit/runtime/orchestration/test_graph_redaction.py tests/contract/test_workflow_graph_execution_contract.py tests/docs/test_workflow_graph_execution_docs.py tests/integration/runtime/test_workflow_graph_execution.py tests/integration/workers/test_orchestration_worker.py tests/performance/runtime/test_workflow_graph_execution_performance.py
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml --start-processes
```

## Manual QA References

- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_ui.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_user_guide.md`
- `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/testing-instructions.md`
