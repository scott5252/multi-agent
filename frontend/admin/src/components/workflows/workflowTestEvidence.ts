import type {
  TestBenchMutationResult,
  WorkflowEvidenceSummary,
  WorkflowPublishReadiness,
  WorkflowReferenceOption,
} from "../../api/generated/reactAdminApi";
import {
  makeUniqueKey,
  testRequirementKeys,
  type WorkflowEditorDocument,
  type WorkflowTestRequirementItem,
} from "./workflowDocumentEditor";

const UNSAFE_EVIDENCE_MARKERS = [
  "raw transcript",
  "raw prompt",
  "raw completion",
  "provider payload",
  "tool payload",
  "credential",
  "authorization header",
  "stack trace",
  "/users/",
];

export interface WorkflowEvidenceReadinessSummary {
  blocked: number;
  current: number;
  missing: number;
  stale: number;
  status: "ready" | "warning" | "blocked" | "missing";
  summary: string;
  total: number;
}

export function summarizeWorkflowEvidence(
  document: WorkflowEditorDocument,
  readiness: WorkflowPublishReadiness,
): WorkflowEvidenceReadinessSummary {
  const total = document.test_requirements.length;
  const current = document.test_requirements.filter((requirement) =>
    ["passed", "passing", "ready"].includes(
      requirement.latest_result_status ?? "missing",
    ),
  ).length;
  const stale = document.test_requirements.filter(
    (requirement) => requirement.latest_result_status === "stale",
  ).length;
  const missing = document.test_requirements.filter((requirement) =>
    ["missing", "unknown", ""].includes(requirement.latest_result_status ?? "missing"),
  ).length;
  const blockedEvidence = readiness.required_evidence.filter((item) =>
    ["blocked", "validation_error", "critical"].includes(item.status),
  ).length;
  const blocked = blockedEvidence + Math.max(0, total - current - stale - missing);
  const status =
    total === 0
      ? "missing"
      : blocked > 0
        ? "blocked"
        : stale > 0 || missing > 0
          ? "warning"
          : "ready";
  const summary =
    total === 0
      ? "No required workflow test evidence is attached."
      : `${current} current, ${stale} stale, ${missing} missing across ${total} required evidence item${total === 1 ? "" : "s"}.`;
  return { blocked, current, missing, stale, status, summary, total };
}

export function createRequirementFromCatalog(
  document: WorkflowEditorDocument,
  option: WorkflowReferenceOption,
): WorkflowTestRequirementItem {
  return {
    freshness_policy: "latest_revision",
    latest_result_id: null,
    latest_result_status:
      option.readiness_status === "ready" ? "passed" : option.readiness_status,
    requirement_key: makeUniqueKey(
      `${option.reference_id || option.label}-evidence`,
      testRequirementKeys(document),
    ),
    safe_summary: safeEvidenceText(option.safe_summary),
    suite_id: option.reference_id,
    target_type: "workflow_draft",
  };
}

export function createGeneratedRequirement(
  document: WorkflowEditorDocument,
  suiteId: string,
  summary: string,
): WorkflowTestRequirementItem {
  return {
    freshness_policy: "latest_revision",
    latest_result_id: null,
    latest_result_status: "missing",
    requirement_key: makeUniqueKey("required-workflow-evidence", testRequirementKeys(document)),
    safe_summary: safeEvidenceText(summary),
    suite_id: suiteId,
    target_type: "workflow_draft",
  };
}

export function updateRequirementFromRun(
  requirement: WorkflowTestRequirementItem,
  result: TestBenchMutationResult,
): WorkflowTestRequirementItem {
  const runStatus = result.run?.summary.status;
  return {
    ...requirement,
    executed_at: result.run?.summary.finished_label ?? requirement.executed_at,
    latest_result_id: result.run?.summary.run_id ?? requirement.latest_result_id,
    latest_result_status:
      runStatus === "passed"
        ? "passed"
        : runStatus === "failed"
          ? "failed"
          : runStatus ?? requirement.latest_result_status ?? "missing",
    safe_summary: safeEvidenceText(
      result.gate?.reason ??
        result.run?.assertion_diagnostics[0]?.remediation ??
        result.summary ??
        "Evidence run summary is available.",
    ),
  };
}

export function safeEvidenceText(value: string | null | undefined): string {
  const normalized = String(value ?? "Evidence summary unavailable.")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 220);
  const lowered = normalized.toLowerCase();
  if (normalized.startsWith("/") || lowered.includes("file://")) {
    return "Evidence reference was redacted.";
  }
  if (UNSAFE_EVIDENCE_MARKERS.some((marker) => lowered.includes(marker))) {
    return "Evidence summary was redacted.";
  }
  return normalized || "Evidence summary unavailable.";
}

export function safeArtifactReference(item: WorkflowEvidenceSummary): string | null {
  if (!item.artifact_reference_id) {
    return null;
  }
  return safeEvidenceText(item.artifact_reference_id);
}
