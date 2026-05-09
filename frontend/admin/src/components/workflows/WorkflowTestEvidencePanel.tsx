import { FlaskConical, Play, RefreshCw, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import {
  launchTestRun,
  saveTestCase,
  saveTestSuite,
} from "../../api/client";
import type {
  TestBenchMutationResult,
  WorkflowPublishReadiness,
  WorkflowReferenceCatalog,
} from "../../api/generated/reactAdminApi";
import { buildIdempotencyKey } from "../../utils/adminActionMetadata";
import { Badge, Button } from "../primitives";
import type { WorkflowEditorDocument } from "./workflowDocumentEditor";
import {
  createGeneratedRequirement,
  createRequirementFromCatalog,
  safeArtifactReference,
  summarizeWorkflowEvidence,
  updateRequirementFromRun,
} from "./workflowTestEvidence";

interface WorkflowTestEvidencePanelProps {
  catalog: WorkflowReferenceCatalog;
  document: WorkflowEditorDocument;
  draftRevision: string;
  onChange: (document: WorkflowEditorDocument) => void;
  publishReadiness: WorkflowPublishReadiness;
  tenantId: string | null;
  workflowDraftId: string;
}

export function WorkflowTestEvidencePanel({
  catalog,
  document,
  draftRevision,
  onChange,
  publishReadiness,
  tenantId,
  workflowDraftId,
}: WorkflowTestEvidencePanelProps) {
  const [selectedSuiteId, setSelectedSuiteId] = useState(
    catalog.test_suite_options[0]?.reference_id ??
      document.test_requirements[0]?.suite_id ??
      "",
  );
  const [suiteResult, setSuiteResult] = useState<TestBenchMutationResult | null>(
    null,
  );
  const [caseResult, setCaseResult] = useState<TestBenchMutationResult | null>(
    null,
  );
  const [runResult, setRunResult] = useState<TestBenchMutationResult | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const readiness = summarizeWorkflowEvidence(document, publishReadiness);
  const tenantQuery = tenantId ? `?tenant_id=${encodeURIComponent(tenantId)}` : "";
  const selectedOption = useMemo(
    () =>
      catalog.test_suite_options.find(
        (option) => option.reference_id === selectedSuiteId,
      ) ?? catalog.test_suite_options[0],
    [catalog.test_suite_options, selectedSuiteId],
  );
  const activeRequirement = document.test_requirements[0] ?? null;
  const activeSuiteId =
    activeRequirement?.suite_id ||
    suiteResult?.suite?.summary.suite_id ||
    selectedOption?.reference_id ||
    "";
  const agentTestsHref =
    selectedOption?.href ??
    `/admin/app/test-bench${tenantQuery}${tenantQuery ? "&" : "?"}target_id=${encodeURIComponent(workflowDraftId)}`;

  function attachSelectedSuite() {
    if (!selectedOption) {
      return;
    }
    const exists = document.test_requirements.some(
      (requirement) => requirement.suite_id === selectedOption.reference_id,
    );
    if (exists) {
      return;
    }
    onChange({
      ...document,
      test_requirements: [
        ...document.test_requirements,
        createRequirementFromCatalog(document, selectedOption),
      ],
    });
  }

  async function createRequiredSuite() {
    if (!tenantId) {
      setError("Select a tenant before creating required evidence.");
      return;
    }
    setBusyAction("suite");
    setError(null);
    try {
      const result = await saveTestSuite(`/admin/app/test-bench/suites${tenantQuery}`, {
        default_safe_mode: "mock_model",
        description: "Required deterministic evidence for workflow publish.",
        idempotency_key: buildIdempotencyKey("workflow-evidence-suite"),
        name: `${document.display_name} required evidence`,
        pass_threshold: 1,
        required_for_publish: true,
        revision: null,
        target_id: workflowDraftId,
        target_revision: draftRevision,
        target_type: "workflow_draft",
      });
      setSuiteResult(result);
      const suiteId = result.suite?.summary.suite_id;
      if (suiteId) {
        setSelectedSuiteId(suiteId);
        onChange({
          ...document,
          test_requirements: [
            ...document.test_requirements,
            createGeneratedRequirement(
              document,
              suiteId,
              "Required deterministic evidence suite created.",
            ),
          ],
        });
      }
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Suite creation failed");
    } finally {
      setBusyAction(null);
    }
  }

  async function addSafeCase() {
    if (!activeSuiteId) {
      setError("Attach a required suite before adding a case.");
      return;
    }
    setBusyAction("case");
    setError(null);
    try {
      const result = await saveTestCase(
        `/admin/app/test-bench/suites/${encodeURIComponent(activeSuiteId)}/cases${tenantQuery}`,
        {
          assertions: [
            {
              assertion_id: "workflow-status-passed",
              comparator: "equals",
              expected_summary: "passed",
              field_errors: [],
              kind: "deterministic",
              label: "Workflow output status passes",
              path_summary: "status",
              severity: "blocking",
              threshold_weight: 1,
              validation_status: "ready",
            },
          ],
          evaluator_reference_id: null,
          expected_contract_summary: "Workflow output includes a passed status.",
          fixture_summary: "Minimal deterministic workflow input fixture.",
          idempotency_key: buildIdempotencyKey("workflow-evidence-case"),
          name: "Workflow contract smoke case",
          revision: null,
        },
      );
      setCaseResult(result);
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Case save failed");
    } finally {
      setBusyAction(null);
    }
  }

  async function launchEvidenceRun() {
    if (!activeSuiteId || !activeRequirement) {
      setError("Attach a required suite before launching evidence.");
      return;
    }
    setBusyAction("run");
    setError(null);
    try {
      const result = await launchTestRun(
        `/admin/app/test-bench/suites/${encodeURIComponent(activeSuiteId)}/runs${tenantQuery}`,
        {
          idempotency_key: buildIdempotencyKey("workflow-evidence-run"),
          run_reason: "Workflow publish evidence",
          safe_mode: "mock_model",
          target_revision: draftRevision,
        },
      );
      setRunResult(result);
      onChange({
        ...document,
        test_requirements: document.test_requirements.map((requirement) =>
          requirement.requirement_key === activeRequirement.requirement_key
            ? updateRequirementFromRun(requirement, result)
            : requirement,
        ),
      });
    } catch (caught: unknown) {
      setError(caught instanceof Error ? caught.message : "Run launch failed");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <section
      className="workflow-evidence-panel"
      id="workflow-test-evidence"
      aria-labelledby="workflow-test-evidence-title"
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">Test evidence</p>
          <h2 id="workflow-test-evidence-title">Required publish evidence</h2>
        </div>
        <Badge tone={toneFor(readiness.status)}>{readiness.status}</Badge>
      </div>
      <p>{readiness.summary}</p>
      {error ? <p className="safe-error">{error}</p> : null}
      <div className="workflow-evidence-controls">
        <label>
          Authorized suite
          <select
            value={selectedSuiteId}
            onChange={(event) => setSelectedSuiteId(event.target.value)}
          >
            {catalog.test_suite_options.length === 0 ? (
              <option value="">No authorized suite</option>
            ) : null}
            {catalog.test_suite_options.map((option) => (
              <option key={option.reference_id} value={option.reference_id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <Button
          disabled={!selectedOption}
          onClick={attachSelectedSuite}
          type="button"
          variant="secondary"
        >
          <ShieldCheck aria-hidden="true" size={16} />
          Attach suite
        </Button>
        <Button
          disabled={busyAction === "suite" || !tenantId}
          onClick={() => void createRequiredSuite()}
          type="button"
          variant="secondary"
        >
          <FlaskConical aria-hidden="true" size={16} />
          Create suite
        </Button>
        <a className="action-link" href={agentTestsHref}>
          Open Agent Tests
        </a>
      </div>
      <div className="workflow-evidence-grid">
        {document.test_requirements.length === 0 ? (
          <article className="workflow-evidence-card">
            <strong>No required suite attached</strong>
            <p>Publish remains blocked until required evidence is attached.</p>
          </article>
        ) : null}
        {document.test_requirements.map((requirement) => (
          <article
            className="workflow-evidence-card"
            key={requirement.requirement_key}
          >
            <div className="card-heading">
              <strong>{requirement.requirement_key}</strong>
              <Badge tone={toneFor(requirement.latest_result_status ?? "missing")}>
                {requirement.latest_result_status ?? "missing"}
              </Badge>
            </div>
            <p>{requirement.safe_summary ?? "Evidence has not run yet."}</p>
            <dl className="compact-dl">
              <div>
                <dt>Suite</dt>
                <dd>{requirement.suite_id}</dd>
              </div>
              <div>
                <dt>Policy</dt>
                <dd>{requirement.freshness_policy ?? "latest_revision"}</dd>
              </div>
              <div>
                <dt>Result</dt>
                <dd>{requirement.latest_result_id ?? "Not recorded"}</dd>
              </div>
            </dl>
          </article>
        ))}
        {publishReadiness.required_evidence.map((item) => (
          <article className="workflow-evidence-card" key={item.evidence_id}>
            <div className="card-heading">
              <strong>{item.label}</strong>
              <Badge tone={toneFor(item.status)}>{item.status}</Badge>
            </div>
            <p>{item.summary}</p>
            {safeArtifactReference(item) ? (
              <small>{safeArtifactReference(item)}</small>
            ) : null}
          </article>
        ))}
      </div>
      <div className="action-row">
        <Button
          disabled={busyAction === "case" || !activeSuiteId}
          onClick={() => void addSafeCase()}
          type="button"
          variant="secondary"
        >
          <FlaskConical aria-hidden="true" size={16} />
          Add safe case
        </Button>
        <Button
          disabled={busyAction === "run" || !activeRequirement}
          onClick={() => void launchEvidenceRun()}
          type="button"
          variant="primary"
        >
          <Play aria-hidden="true" size={16} />
          Launch deterministic run
        </Button>
        <Button
          disabled={busyAction !== null}
          onClick={() => setRunResult(null)}
          type="button"
          variant="secondary"
        >
          <RefreshCw aria-hidden="true" size={16} />
          Clear run result
        </Button>
      </div>
      {suiteResult ? <ResultCard label="Suite result" result={suiteResult} /> : null}
      {caseResult ? <ResultCard label="Case result" result={caseResult} /> : null}
      {runResult ? <ResultCard label="Run result" result={runResult} /> : null}
    </section>
  );
}

function ResultCard({
  label,
  result,
}: {
  label: string;
  result: TestBenchMutationResult;
}) {
  return (
    <article className={`mutation-result ${result.status}`}>
      <p className="eyebrow">{label}</p>
      <h3>{result.status.replace("_", " ")}</h3>
      <p>{result.summary}</p>
      {result.diagnostics.length > 0 ? (
        <ul className="validation-list">
          {result.diagnostics.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed", "passing"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "critical", "validation_error"].includes(status)) {
    return "critical";
  }
  if (["warning", "stale", "missing", "running", "queued"].includes(status)) {
    return "warning";
  }
  return "info";
}
