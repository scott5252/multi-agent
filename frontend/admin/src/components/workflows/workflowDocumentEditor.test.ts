import { describe, expect, it } from "vitest";

import { workflowBuilderEnvelope } from "../../test/workflowBuilderTestData";
import {
  buildGraphPreviewFromDocument,
  cloneWorkflowDocument,
  contractDependencyWarnings,
  duplicateRole,
  makeUniqueKey,
  nodeDependencyWarnings,
  roleDependencyWarnings,
} from "./workflowDocumentEditor";

describe("workflowDocumentEditor", () => {
  it("normalizes workflow documents and preserves unknown fields", () => {
    const document = cloneWorkflowDocument({
      ...workflowBuilderEnvelope.draft!.document,
      extra_safe_field: "preserved",
    });

    expect(document.extra_safe_field).toBe("preserved");
    expect(document.roles[0].role_key).toBe("coordinator");
    expect(document.contracts[0].contract_key).toBe("request");
    expect(document.editor_annotations.graph_layout).toEqual({});
  });

  it("generates stable unique keys and duplicate role keys", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);

    expect(makeUniqueKey("agent", ["agent", "agent-2"])).toBe("agent-3");
    expect(duplicateRole(document, document.roles[0]).role_key).toBe(
      "coordinator-copy",
    );
  });

  it("summarizes dependency warnings for referenced items", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);

    expect(roleDependencyWarnings(document, "coordinator")).toContain(
      "Referenced by node start",
    );
    expect(contractDependencyWarnings(document, "request")).toContain(
      "Referenced by role coordinator",
    );
    expect(nodeDependencyWarnings(document, "calendar")).toContain(
      "Referenced by edge edge-start-calendar",
    );
  });

  it("projects editable documents into graph previews", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const graph = buildGraphPreviewFromDocument(
      document,
      workflowBuilderEnvelope.draft!.graph,
    );

    expect(graph.nodes.map((node) => node.node_id)).toEqual([
      "start",
      "calendar",
      "join",
    ]);
    expect(graph.edges).toHaveLength(2);
    expect(graph.join_policies[0].policy_id).toBe("wait_for_required_branches");
    expect(graph.accessibility_summary).toContain("3 nodes");
  });
});
