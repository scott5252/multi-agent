import { describe, expect, it } from "vitest";

import {
  workflowBuilderEnvelope,
  workflowReferenceCatalog,
} from "../../test/workflowBuilderTestData";
import { cloneWorkflowDocument } from "./workflowDocumentEditor";
import {
  buildThreeAgentStarterDocument,
  buildWorkflowSetupProgress,
} from "./workflowSetupWizard";

describe("workflowSetupWizard", () => {
  it("marks the guided setup active until publish and runtime launch are ready", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const progress = buildWorkflowSetupProgress({
      document,
      publishedVersionId: null,
      publishReadiness: workflowBuilderEnvelope.publish_readiness!,
      validation: workflowBuilderEnvelope.validation!,
    });

    expect(progress.totalCount).toBe(9);
    expect(progress.steps.find((step) => step.key === "agents")?.status).toBe(
      "active",
    );
    expect(progress.steps.find((step) => step.key === "evidence")?.href).toBe(
      "#workflow-test-evidence",
    );
    expect(progress.steps.find((step) => step.key === "runtime")?.status).toBe(
      "blocked",
    );
  });

  it("builds a three-agent starter with ready prompt profile refs and a join node", () => {
    const baseDocument = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const document = buildThreeAgentStarterDocument(baseDocument);
    const readyReadiness = {
      ...workflowBuilderEnvelope.publish_readiness!,
      blockers: [],
      decision: "accepted" as const,
      published_bundle_summary: "Published workflow bundle is available.",
      required_evidence: [
        {
          artifact_reference_id: null,
          evidence_id: "required",
          href: "#workflow-test-evidence",
          label: "Required evidence",
          status: "ready" as const,
          summary: "Required evidence passed.",
        },
      ],
      summary: "Ready to publish.",
    };
    const readyValidation = {
      ...workflowBuilderEnvelope.validation!,
      findings: [],
      status: "ready" as const,
      summary: "Validation passed.",
    };
    const progress = buildWorkflowSetupProgress({
      document: {
        ...document,
        test_requirements: [
          {
            freshness_policy: "latest_revision",
            latest_result_id: "run-current",
            latest_result_status: "passed",
            requirement_key: "required-evidence",
            suite_id: workflowReferenceCatalog.test_suite_options[0].reference_id,
            target_type: "workflow_draft",
          },
        ],
      },
      publishedVersionId: "version-current",
      publishReadiness: readyReadiness,
      validation: readyValidation,
    });

    expect(document.roles).toHaveLength(3);
    expect(document.nodes.some((node) => node.node_type === "join")).toBe(true);
    expect(document.edges).toHaveLength(5);
    expect(
      document.roles.every(
        (role) => role.profile_reference_key && role.prompt_reference_keys?.length,
      ),
    ).toBe(true);
    expect(progress.completeCount).toBe(progress.totalCount);
  });
});
