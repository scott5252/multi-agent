import { describe, expect, it } from "vitest";

import { workflowBuilderEnvelope } from "../../test/workflowBuilderTestData";
import { cloneWorkflowDocument } from "./workflowDocumentEditor";
import {
  createGeneratedRequirement,
  createRequirementFromCatalog,
  safeArtifactReference,
  safeEvidenceText,
  summarizeWorkflowEvidence,
  updateRequirementFromRun,
} from "./workflowTestEvidence";

describe("workflowTestEvidence helpers", () => {
  it("summarizes missing, stale, and current evidence from workflow state", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const summary = summarizeWorkflowEvidence(
      {
        ...document,
        test_requirements: [
          {
            freshness_policy: "latest_revision",
            latest_result_status: "passed",
            requirement_key: "current",
            suite_id: "suite-current",
            target_type: "workflow_draft",
          },
          {
            freshness_policy: "latest_revision",
            latest_result_status: "stale",
            requirement_key: "stale",
            suite_id: "suite-stale",
            target_type: "workflow_draft",
          },
        ],
      },
      workflowBuilderEnvelope.publish_readiness!,
    );

    expect(summary.current).toBe(1);
    expect(summary.stale).toBe(1);
    expect(summary.status).toBe("blocked");
    expect(summary.summary).toContain("1 current");
  });

  it("creates catalog and generated requirements with safe summaries", () => {
    const document = cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document);
    const catalogRequirement = createRequirementFromCatalog(document, {
      href: "/admin/app/test-bench",
      kind: "test_suite",
      label: "Daily briefing required suite",
      readiness_status: "blocked",
      reference_id: "suite-briefing-required",
      safe_summary: "Repository-backed evidence is required.",
      tenant_eligible: true,
      version_label: null,
    });
    const generated = createGeneratedRequirement(
      { ...document, test_requirements: [catalogRequirement] },
      "suite-generated",
      "raw transcript should be redacted",
    );

    expect(catalogRequirement.requirement_key).toContain("suite-briefing-required");
    expect(generated.requirement_key).not.toBe(catalogRequirement.requirement_key);
    expect(generated.safe_summary).toBe("Evidence summary was redacted.");
  });

  it("updates requirement status from safe run results", () => {
    const requirement = createGeneratedRequirement(
      cloneWorkflowDocument(workflowBuilderEnvelope.draft!.document),
      "suite-generated",
      "Required suite generated.",
    );
    const updated = updateRequirementFromRun(requirement, {
      artifact: null,
      audit_reference_id: "audit-run",
      case: null,
      confirmation: null,
      diagnostics: [],
      field_errors: [],
      gate: null,
      idempotency: null,
      next_action: null,
      revision: "run-rev",
      run: {
        artifacts: [],
        assertion_diagnostics: [],
        audit_reference_id: "audit-run",
        blocked_side_effects: [],
        case_results: [],
        progress: {
          audit_reference_id: "audit-progress",
          completed_cases: 1,
          next_poll_seconds: 0,
          sse_href: null,
          status: "passed",
          summary: "Complete",
          total_cases: 1,
        },
        publish_gate: {
          artifact_references: [],
          audit_reference_id: "audit-gate",
          authorized_actions: [],
          evidence_status: "passed",
          gate_id: "gate",
          latest_run_id: "run-1",
          latest_run_revision: "draft-rev-qa030-current",
          latest_run_status: "passed",
          reason: "Current target revision has passing evidence.",
          remediation: "Publication can use this current evidence.",
          required_suite_id: "suite-generated",
          required_suite_label: "Required suite",
          target_label: "Workflow draft",
          target_revision: "draft-rev-qa030-current",
          target_type: "workflow_draft",
        },
        redaction_summary: "Transcript is redacted.",
        summary: {
          actor_label: "Tenant Admin",
          audit_reference_id: "audit-run",
          authorized_actions: [],
          case_failed: 0,
          case_passed: 1,
          case_total: 1,
          failure_category: null,
          finished_label: "Now",
          latency_summary: "1 ms",
          pass_rate: 1,
          run_id: "run-1",
          safe_mode: "mock_model",
          started_label: "Now",
          status: "passed",
          suite_id: "suite-generated",
          suite_name: "Required suite",
          target_revision: "draft-rev-qa030-current",
          usage_summary: "No provider usage.",
        },
        trace_steps: [],
      },
      stale_conflict: null,
      status: "accepted",
      suite: null,
      summary: "Evidence run completed.",
      toast: null,
    });

    expect(updated.latest_result_id).toBe("run-1");
    expect(updated.latest_result_status).toBe("passed");
  });

  it("redacts unsafe evidence text and local artifact paths", () => {
    expect(safeEvidenceText("/Users/example/raw transcript")).toBe(
      "Evidence reference was redacted.",
    );
    expect(
      safeArtifactReference({
        artifact_reference_id: "/Users/example/artifact.json",
        evidence_id: "artifact",
        href: null,
        label: "Artifact",
        status: "blocked",
        summary: "Bad local path",
      }),
    ).toBe("Evidence reference was redacted.");
  });
});
