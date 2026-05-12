import { describe, expect, it } from "vitest";

import {
  workflowBuilderEnvelope,
  workflowReferenceCatalog,
} from "../../test/workflowBuilderTestData";
import { cloneWorkflowDocument } from "./workflowDocumentEditor";
import {
  attachWorkflowEvidenceRequirement,
  buildGenericBlueprintDocument,
  buildThreeAgentStarterDocument,
  buildWorkflowSetupProgress,
  DEFAULT_WORKFLOW_SCENARIO_INTAKE,
  normalizeWorkflowKey,
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

  it("builds a neutral arbitrary-scenario blueprint without tutorial defaults", () => {
    const baseDocument = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const document = buildGenericBlueprintDocument(baseDocument, {
      ...DEFAULT_WORKFLOW_SCENARIO_INTAKE,
      desiredOutputs: "A triaged supplier risk summary.",
      expectedInputs: "A supplier record and a question from an operator.",
      purpose: "Coordinate supplier risk intake for regional operators.",
      workflowKey: "Supplier Risk Intake!!",
      workflowName: "Supplier Risk Intake",
    });

    expect(document.workflow_key).toBe("supplier-risk-intake");
    expect(document.display_name).toBe("Supplier Risk Intake");
    expect(document.roles).toHaveLength(3);
    expect(document.contracts.map((contract) => contract.contract_key)).toEqual([
      "scenario-request",
      "scenario-handoff",
      "scenario-result",
    ]);
    expect(document.nodes.some((node) => node.node_type === "join")).toBe(true);
    expect(JSON.stringify(document)).not.toContain("Daily Intelligence Briefing");
    expect(JSON.stringify(document)).not.toContain("Design Reviewer Council");
  });

  it("normalizes workflow keys and attaches required evidence idempotently", () => {
    const document = buildGenericBlueprintDocument(
      cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document),
      DEFAULT_WORKFLOW_SCENARIO_INTAKE,
    );
    const withEvidence = attachWorkflowEvidenceRequirement(
      attachWorkflowEvidenceRequirement(document, "suite-risk-required"),
      "suite-risk-required",
    );

    expect(normalizeWorkflowKey("  Quarterly Review / Ops  ")).toBe(
      "quarterly-review-ops",
    );
    const onboardingRequirements = withEvidence.test_requirements.filter(
      (requirement) =>
        requirement.requirement_key === "onboarding-required-evidence",
    );
    expect(onboardingRequirements).toHaveLength(1);
    expect(onboardingRequirements[0].suite_id).toBe("suite-risk-required");
    expect(onboardingRequirements[0].latest_result_status).toBe("pending");
  });
});
