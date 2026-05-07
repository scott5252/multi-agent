import { Save } from "lucide-react";

import type {
  TestBenchMutationResult,
  TestCaseSummary,
  TestSuiteDetail,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface SuiteAuthoringPanelProps {
  caseResult: TestBenchMutationResult | null;
  onSaveCase: (href: string, testCase: TestCaseSummary) => void;
  onSaveSuite: (href: string) => void;
  suite: TestSuiteDetail;
  suiteResult: TestBenchMutationResult | null;
}

export function SuiteAuthoringPanel({
  caseResult,
  onSaveCase,
  onSaveSuite,
  suite,
  suiteResult,
}: SuiteAuthoringPanelProps) {
  const saveSuiteAction = suite.summary.authorized_actions.find(
    (action) => action.action_id === "open-suite",
  );
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="authoring-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Author</p>
          <h2 id="authoring-title">Suite and case forms</h2>
        </div>
        <Button
          onClick={() => onSaveSuite("/admin/app/test-bench/suites")}
          type="button"
          variant="primary"
        >
          <Save aria-hidden="true" size={16} />
          Save suite
        </Button>
      </div>
      <article className="governance-card">
        <div className="card-heading">
          <strong>{suite.summary.suite_name}</strong>
          <Badge tone={toneFor(suite.summary.archive_status)}>
            {suite.summary.archive_status}
          </Badge>
        </div>
        <p>{suite.summary.target_label}</p>
        <dl className="compact-dl">
          <div>
            <dt>Default mode</dt>
            <dd>{suite.summary.default_safe_mode}</dd>
          </div>
          <div>
            <dt>Pass threshold</dt>
            <dd>{Math.round(suite.summary.pass_threshold * 100)}%</dd>
          </div>
          <div>
            <dt>Suite revision</dt>
            <dd>{suite.summary.suite_revision}</dd>
          </div>
        </dl>
        {saveSuiteAction ? <small>{saveSuiteAction.href}</small> : null}
      </article>
      <div className="governance-card-grid">
        {suite.cases.map((testCase) => {
          const saveAction = testCase.authorized_actions.find(
            (action) => action.action_id === "edit-case",
          );
          return (
            <article className="governance-card" key={testCase.case_id}>
              <div className="card-heading">
                <strong>{testCase.case_name}</strong>
                <Badge tone={toneFor(testCase.case_status)}>
                  {testCase.case_status}
                </Badge>
              </div>
              <p>{testCase.fixture_summary}</p>
              <p>{testCase.expected_contract_summary}</p>
              <small>{testCase.evaluator_summary}</small>
              {saveAction ? (
                <Button
                  onClick={() => onSaveCase(saveAction.href, testCase)}
                  type="button"
                  variant="secondary"
                >
                  Save case
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
      {suiteResult ? <ResultCard label="Suite result" result={suiteResult} /> : null}
      {caseResult ? <ResultCard label="Case result" result={caseResult} /> : null}
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
      <h3>{result.status}</h3>
      <p>{result.summary}</p>
      {result.audit_reference_id ? <small>{result.audit_reference_id}</small> : null}
    </article>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "failed_assertion", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
