import { describe, expect, it } from "vitest";

import type { WorkflowReferenceOption } from "../../api/generated/reactAdminApi";
import {
  bindReferenceToRole,
  buildGeneratedReference,
  buildReferenceFromCatalog,
  safeCatalogLabel,
  summarizeBindingReadiness,
} from "./workflowPromptProfileBinding";
import { cloneWorkflowDocument } from "./workflowDocumentEditor";

const catalogOption: WorkflowReferenceOption = {
  href: "/admin/app/governance/prompts",
  kind: "prompt",
  label: "Safe triage prompt",
  readiness_status: "ready",
  reference_id: "Prompt Version: Triage 1",
  safe_summary: "Published prompt version is available.",
  tenant_eligible: true,
  version_label: "v1",
};

const document = cloneWorkflowDocument({
  approval_gates: [],
  contracts: [],
  display_name: "Prompt binding",
  edges: [],
  editor_annotations: {
    collapsed_sections: [],
    graph_layout: {},
    section_notes: {},
  },
  entry_node_key: "start",
  join_policies: [],
  nodes: [],
  prompt_profile_references: [],
  roles: [
    {
      display_name: "Triage agent",
      purpose: "Classify inbound work.",
      responsibilities: ["Route safe requests."],
      role_key: "triage",
      role_kind: "agent",
    },
  ],
  subworkflow_refs: [],
  workflow_key: "prompt-binding",
  workflow_kind: "main_workflow",
});

describe("workflowPromptProfileBinding", () => {
  it("summarizes incomplete and ready role bindings", () => {
    expect(summarizeBindingReadiness(document)).toEqual({
      missingProfiles: 1,
      missingPrompts: 1,
      readyRoles: 0,
      totalRoles: 1,
    });
  });

  it("builds safe catalog labels without raw prompt content", () => {
    expect(safeCatalogLabel(catalogOption)).toBe("Safe triage prompt v1");
    expect(safeCatalogLabel(null)).toBe("No authorized record selected");
  });

  it("binds prompt references to roles and preserves safe ids", () => {
    const role = document.roles[0];
    const reference = buildReferenceFromCatalog({
      kind: "prompt",
      option: catalogOption,
      role,
    });
    const nextDocument = bindReferenceToRole({
      document,
      kind: "prompt",
      reference,
      roleKey: role.role_key,
    });

    expect(nextDocument.roles[0].prompt_reference_keys).toEqual([
      "prompt-version-triage-1",
    ]);
    expect(nextDocument.prompt_profile_references[0]).toMatchObject({
      readiness_status: "ready",
      reference_key: "prompt-version-triage-1",
      role_key: "triage",
    });
    expect(JSON.stringify(nextDocument)).not.toContain("raw prompt");
  });

  it("builds generated profile references without leaking editor content", () => {
    const generated = buildGeneratedReference({
      kind: "profile",
      label: "Authorized template text stays private",
      role: document.roles[0],
      usedKeys: [],
    });

    expect(generated.reference_key).toBe("triage-profile");
    expect(generated.readiness_status).toBe("ready");
    expect(JSON.stringify(generated)).not.toContain("template text");
  });
});
