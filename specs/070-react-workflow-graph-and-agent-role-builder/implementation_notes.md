# Implementation Notes: Spec 070

## Existing Surface Audit

- `WorkflowBuilderPage.tsx` loaded the Spec 069 full document but only exposed
  metadata and reference selectors as editable controls.
- `WorkflowSectionForm.tsx` owned draft name, description, save, stale-save,
  and mutation result rendering.
- `WorkflowGraphPanel.tsx` already used `@xyflow/react` for a read-only graph
  canvas with node and edge lists.
- `WorkflowReferencePicker.tsx`, `WorkflowValidationPanel.tsx`, and
  `WorkflowPublishPanel.tsx` already consumed backend-owned contracts and safe
  summaries.
- Generated React types model the canonical workflow document as a backend
  record, so Spec 070 keeps browser editing helpers local and persists through
  the existing full-document save route.

## Implementation Direction

- Add typed frontend helper utilities for normalizing workflow document
  collections while preserving unknown safe fields.
- Add collection editors for roles, contracts, nodes, edges, joins, approvals,
  subworkflows, and layout positions.
- Keep graph editing form/list-first and use the existing graph panel as a
  projection of the dirty local document.
- Keep validation and publish readiness backend-owned; client dependency
  warnings are only advisory.
- Do not introduce new public JSON route families for Spec 070.

## Evidence Notes

- Frontend workflow tests cover helper normalization, dependency warnings,
  graph projection, role add, and save payload assembly.
- Backend route smoke covers saving a document with three roles, seven nodes,
  eight edges, a quorum join, approval gate, subworkflow reference, contracts,
  and layout annotations.
- `curl_testing.md` remains covered by the Spec 069 React workflow save section
  because Spec 070 does not add or change route families.
