import { useEffect, useState } from "react";

import {
  fetchRunAgentGraph,
  fetchOperationsWorkbench,
  requestWorkbenchExport,
} from "../../api/client";
import type {
  AgentCommunicationGraph,
  OperationsWorkbenchEnvelope,
  WorkbenchExportSnapshot,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { AgentGraphPanel } from "../workflows/AgentGraphPanel";
import { WorkbenchExportPanel } from "./WorkbenchExportPanel";
import { WorkbenchReliabilityPanel } from "./WorkbenchReliabilityPanel";
import { WorkbenchSummaryGrid } from "./WorkbenchSummaryGrid";
import { WorkbenchTimeline } from "./WorkbenchTimeline";

export function WorkbenchPage({ workbenchUrl }: { workbenchUrl: string }) {
  const [envelope, setEnvelope] = useState<OperationsWorkbenchEnvelope | null>(null);
  const [exportSnapshot, setExportSnapshot] =
    useState<WorkbenchExportSnapshot | null>(null);
  const [runGraph, setRunGraph] = useState<AgentCommunicationGraph | null>(null);
  const [runGraphError, setRunGraphError] = useState<string | null>(null);
  const [runGraphLoading, setRunGraphLoading] = useState(false);
  const [graphReloadToken, setGraphReloadToken] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchOperationsWorkbench(workbenchUrl)
      .then((payload) => {
        if (alive) {
          setEnvelope(payload);
          setExportSnapshot(payload.exports);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(caught instanceof Error ? caught.message : "Workbench unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [workbenchUrl]);

  useEffect(() => {
    if (!envelope?.run_debug) {
      setRunGraph(null);
      setRunGraphError(null);
      setRunGraphLoading(false);
      return;
    }
    let alive = true;
    const tenantId =
      envelope.run_debug.tenant_scope?.tenant_id ?? envelope.scope.tenant_id;
    setRunGraphLoading(true);
    fetchRunAgentGraph(envelope.run_debug.workflow_run_id, tenantId)
      .then((payload) => {
        if (alive) {
          setRunGraph(payload);
          setRunGraphError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setRunGraph(null);
          setRunGraphError(
            caught instanceof Error ? caught.message : "Runtime graph unavailable",
          );
        }
      })
      .finally(() => {
        if (alive) {
          setRunGraphLoading(false);
        }
      });
    return () => {
      alive = false;
    };
  }, [envelope, graphReloadToken]);

  async function exportEvidence() {
    if (!envelope) {
      return;
    }
    const action = envelope.actions.find((candidate) => candidate.action_id === "workbench-export");
    if (!action) {
      return;
    }
    setExportSnapshot(await requestWorkbenchExport(action.href));
  }

  if (loadError) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Workbench unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!envelope) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading safe operational summaries.",
          title: "Loading workbench",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="workbench-page">
      <section className="patterns-hero workbench-hero">
        <p className="eyebrow">Operations</p>
        <h2>{envelope.title}</h2>
        <p>{envelope.description}</p>
        <small>
          {envelope.time_range.label} · {envelope.generated_at_label}
        </small>
      </section>
      <WorkbenchSummaryGrid
        cards={envelope.summary_cards}
        causes={envelope.likely_causes}
        panels={envelope.health_panels}
      />
      {envelope.run_debug ? <WorkbenchTimeline runDebug={envelope.run_debug} /> : null}
      {envelope.run_debug ? (
        <AgentGraphPanel
          error={runGraphError}
          graph={runGraph}
          loading={runGraphLoading}
          onRetry={() => setGraphReloadToken((value) => value + 1)}
          sourceLabel="Runtime run"
        />
      ) : null}
      <WorkbenchReliabilityPanel reliability={envelope.reliability} />
      <WorkbenchExportPanel
        exportSnapshot={exportSnapshot ?? envelope.exports}
        onExport={exportEvidence}
      />
      <section className="workbench-panel log-panel" aria-label="Redacted logs">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Logs</p>
            <h2>Redacted signals</h2>
          </div>
        </div>
        <table className="admin-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Subsystem</th>
              <th>Status</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {envelope.logs.map((log) => (
              <tr key={log.log_id}>
                <td>{log.occurred_at_label}</td>
                <td>{log.subsystem}</td>
                <td>{log.status}</td>
                <td>{log.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
