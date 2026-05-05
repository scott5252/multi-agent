import { useEffect, useState } from "react";

import {
  fetchTestBenchDashboard,
  fetchTestRunDetail,
  launchTestRun,
  refreshPublishGateEvidence,
  saveTestCase,
  saveTestSuite,
} from "../../api/client";
import type {
  TestBenchDashboard,
  TestBenchMutationResult,
  TestCaseSummary,
  TestRunDetail,
  TestSuiteDetail,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { AssertionAndTargetPanel } from "./AssertionAndTargetPanel";
import { PublishGateEvidencePanel } from "./PublishGateEvidencePanel";
import { RunDetailPanel } from "./RunDetailPanel";
import { RunLauncherPanel } from "./RunLauncherPanel";
import { RunListPanel } from "./RunListPanel";
import { RunProgressPanel } from "./RunProgressPanel";
import { SuiteAuthoringPanel } from "./SuiteAuthoringPanel";
import { SuiteListPanel } from "./SuiteListPanel";
import { TestBenchAuditPanel } from "./TestBenchAuditPanel";
import { TestBenchDashboardPanel } from "./TestBenchDashboardPanel";
import { TestBenchSectionNav } from "./TestBenchSectionNav";
import { TraceAndArtifactPanel } from "./TraceAndArtifactPanel";

export function TestBenchPage({ testBenchUrl }: { testBenchUrl: string }) {
  const [dashboard, setDashboard] = useState<TestBenchDashboard | null>(null);
  const [suite, setSuite] = useState<TestSuiteDetail | null>(null);
  const [activeRun, setActiveRun] = useState<TestRunDetail | null>(null);
  const [activeSection, setActiveSection] = useState("suites");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [suiteResult, setSuiteResult] = useState<TestBenchMutationResult | null>(null);
  const [caseResult, setCaseResult] = useState<TestBenchMutationResult | null>(null);
  const [launchResult, setLaunchResult] =
    useState<TestBenchMutationResult | null>(null);
  const [gateResult, setGateResult] = useState<TestBenchMutationResult | null>(null);

  useEffect(() => {
    let alive = true;
    fetchTestBenchDashboard(testBenchUrl)
      .then(async (payload) => {
        const selectedSuite = payload.selected_suite;
        const detail = await fetchTestRunDetail(
          `/admin/app/test-bench/runs/run-qa033-failing.json${window.location.search}`,
        );
        if (alive) {
          setDashboard(payload);
          setSuite(selectedSuite);
          setActiveRun(detail);
          setActiveSection(payload.sections[0]?.section_id ?? "suites");
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Test bench unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [testBenchUrl]);

  async function submitSuite(url: string) {
    if (!suite) {
      return;
    }
    const result = await saveTestSuite(url, {
      default_safe_mode: suite.summary.default_safe_mode,
      description: "Safe suite summary for release governance.",
      idempotency_key: "suite-save-ui-qa033",
      name: suite.summary.suite_name,
      pass_threshold: suite.summary.pass_threshold,
      required_for_publish: suite.summary.required_for_publish,
      revision: suite.summary.suite_revision,
      target_id: suite.target_binding.target_id,
      target_revision: suite.target_binding.selected_revision,
      target_type: suite.target_binding.target_type,
    });
    setSuiteResult(result);
    if (result.suite) {
      setSuite(result.suite);
    }
  }

  async function submitCase(url: string, testCase: TestCaseSummary) {
    const result = await saveTestCase(url, {
      assertions: testCase.assertions,
      evaluator_reference_id: "evaluator-qa033-safe-summary",
      expected_contract_summary: testCase.expected_contract_summary,
      fixture_summary: testCase.fixture_summary,
      idempotency_key: "case-save-ui-qa033",
      name: testCase.case_name,
      revision: testCase.case_revision,
    });
    setCaseResult(result);
  }

  async function submitRun(url: string, safeMode: string) {
    if (!suite) {
      return;
    }
    const result = await launchTestRun(url, {
      idempotency_key: "run-launch-ui-qa033",
      run_reason: "Release confidence",
      safe_mode: safeMode,
      target_revision: suite.target_binding.selected_revision,
    });
    setLaunchResult(result);
    if (result.run) {
      setActiveRun(result.run);
    }
  }

  async function openRun(url: string) {
    setActiveRun(await fetchTestRunDetail(url));
  }

  async function refreshGate(url: string) {
    const result = await refreshPublishGateEvidence(url, {
      idempotency_key: "gate-refresh-ui-qa033",
      target_revision: suite?.target_binding.selected_revision ?? "workflow-draft-rev-qa033-current",
    });
    setGateResult(result);
  }

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Test bench unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!dashboard || !suite) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading suites, safe modes, runs, diagnostics, gates, and audit evidence.",
          title: "Loading test bench",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="governance-page testbench-page">
      <section className="patterns-hero governance-hero testbench-hero">
        <p className="eyebrow">Agent tests</p>
        <h2>{dashboard.title}</h2>
        <p>{dashboard.description}</p>
      </section>
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <TestBenchSectionNav
        activeSection={activeSection}
        onChange={setActiveSection}
        sections={dashboard.sections}
      />
      <TestBenchDashboardPanel
        gateAlerts={dashboard.gate_alerts}
        metrics={dashboard.summary_cards}
      />
      <SuiteListPanel onOpenSuite={() => setSuite(dashboard.selected_suite)} suites={dashboard.suites} />
      <SuiteAuthoringPanel
        caseResult={caseResult}
        onSaveCase={(url, testCase) => void submitCase(url, testCase)}
        onSaveSuite={(url) => void submitSuite(url)}
        suite={suite}
        suiteResult={suiteResult}
      />
      <AssertionAndTargetPanel
        metadata={suite.run_launcher}
        targetBinding={suite.target_binding}
      />
      <RunLauncherPanel
        launchResult={launchResult}
        onLaunch={(url, safeMode) => void submitRun(url, safeMode)}
        suite={suite}
      />
      <RunProgressPanel run={activeRun} />
      <RunListPanel
        onOpenRun={(url) => void openRun(url)}
        runs={dashboard.recent_runs}
      />
      <RunDetailPanel run={activeRun} />
      <TraceAndArtifactPanel run={activeRun} />
      <PublishGateEvidencePanel
        gates={dashboard.gate_alerts}
        onRefreshGate={(url) => void refreshGate(url)}
        refreshResult={gateResult}
      />
      <TestBenchAuditPanel auditTimeline={dashboard.audit_timeline} />
    </div>
  );
}
