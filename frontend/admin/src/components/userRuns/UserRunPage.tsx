import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import {
  cancelUserRun,
  createUserRunArtifactGrant,
  decideUserRunPrompt,
  fetchUserRunArtifacts,
  fetchUserRunResult,
  fetchUserRunStatus,
  fetchUserRunTimeline,
  registerUserRunCallback,
  startUserRun,
  subscribeUserRun,
} from "../../api/client";
import type {
  ArtifactDownloadUrlResponse,
  ArtifactListResponse,
  CallbackRegistrationResponse,
  NotificationSubscriptionResponse,
  PromptAction,
  PromptDecisionResponse,
  RunInvocationResponse,
  RunResultResponse,
  RunStatusResponse,
  TimelineResponse,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";

type ActionResult =
  | RunInvocationResponse
  | RunStatusResponse
  | PromptDecisionResponse
  | NotificationSubscriptionResponse
  | CallbackRegistrationResponse
  | ArtifactDownloadUrlResponse;

interface UserRunPageProps {
  runId?: string | null;
  search?: string;
}

export function UserRunPage({ runId: initialRunId = null, search = "" }: UserRunPageProps) {
  const [runId, setRunId] = useState<string | null>(initialRunId);
  const [workflowId, setWorkflowId] = useState(
    workflowIdFromSearch(search) ?? "daily-briefing-demo",
  );
  const [safeInput, setSafeInput] = useState("safe browser request");
  const [status, setStatus] = useState<RunStatusResponse | null>(null);
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [result, setResult] = useState<RunResultResponse | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactListResponse | null>(null);
  const [actionResult, setActionResult] = useState<ActionResult | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const effectiveRunId = runId?.trim() || null;

  const refreshRun = useCallback(async () => {
    if (!effectiveRunId) {
      return;
    }
    const [nextStatus, nextTimeline, nextResult, nextArtifacts] = await Promise.all([
      fetchUserRunStatus(`/runs/${effectiveRunId}/status${search}`),
      fetchUserRunTimeline(`/runs/${effectiveRunId}/timeline${search}`),
      fetchUserRunResult(`/runs/${effectiveRunId}/result${search}`),
      fetchUserRunArtifacts(`/runs/${effectiveRunId}/artifacts${search}`),
    ]);
    setStatus(nextStatus);
    setTimeline(nextTimeline);
    setResult(nextResult);
    setArtifacts(nextArtifacts);
    setLoadError(null);
  }, [effectiveRunId, search]);

  useEffect(() => {
    setRunId(initialRunId);
  }, [initialRunId]);

  useEffect(() => {
    const requestedWorkflowId = workflowIdFromSearch(search);
    if (requestedWorkflowId) {
      setWorkflowId(requestedWorkflowId);
    }
  }, [search]);

  useEffect(() => {
    let alive = true;
    if (!effectiveRunId) {
      return;
    }
    refreshRun().catch((caught: unknown) => {
      if (alive) {
        setLoadError(caught instanceof Error ? caught.message : "Run unavailable");
      }
    });
    return () => {
      alive = false;
    };
  }, [effectiveRunId, refreshRun]);

  async function handleStart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAction("start", async () => {
      const response = await startUserRun(
        {
          callback_url: null,
          channel: "web_ui",
          client_session_id: "react-user-run",
          inputs: { text: safeInput },
          workflow_id: workflowId,
        },
        `react-run-start-${workflowId}`,
      );
      const nextRunId = response.run_id;
      setRunId(nextRunId);
      setActionResult(response);
      window.history.replaceState({}, "", `/admin/app/channels/runs/${nextRunId}${search}`);
    });
  }

  async function handleCancel() {
    if (!effectiveRunId) {
      return;
    }
    await runAction("cancel", async () => {
      const response = await cancelUserRun(
        `/runs/${effectiveRunId}/cancel${search}`,
        { reason: "User requested browser cancellation." },
        `react-run-cancel-${effectiveRunId}`,
      );
      setActionResult(response);
      await refreshRun();
    });
  }

  async function handlePrompt(action: PromptAction) {
    if (!effectiveRunId || !status?.waiting_prompt) {
      return;
    }
    const prompt = status.waiting_prompt;
    await runAction(action, async () => {
      const response = await decideUserRunPrompt(
        `/runs/${effectiveRunId}/approvals/${prompt.prompt_id}/decision${search}`,
        {
          action,
          decision_payload: {},
          prompt_version: prompt.prompt_version,
        },
        `react-run-decision-${effectiveRunId}-${action}`,
      );
      setActionResult(response);
      setStatus(response.run_status);
      await refreshRun();
    });
  }

  async function handleSubscribe() {
    if (!effectiveRunId) {
      return;
    }
    await runAction("subscribe", async () => {
      const response = await subscribeUserRun(
        `/runs/${effectiveRunId}/subscriptions${search}`,
        { channel: "web_ui", event_types: ["terminal"] },
        `react-run-subscribe-${effectiveRunId}`,
      );
      setActionResult(response);
      await refreshRun();
    });
  }

  async function handleCallback() {
    if (!effectiveRunId) {
      return;
    }
    await runAction("callback", async () => {
      const response = await registerUserRunCallback(
        `/runs/${effectiveRunId}/callbacks${search}`,
        {
          callback_url: "https://example.test/channel-callback",
          event_types: ["terminal", "waiting_prompt", "artifact_ready"],
        },
        `react-run-callback-${effectiveRunId}`,
      );
      setActionResult(response);
      await refreshRun();
    });
  }

  async function handleArtifactGrant(artifactId: string) {
    if (!effectiveRunId) {
      return;
    }
    await runAction("artifact", async () => {
      const response = await createUserRunArtifactGrant(
        `/runs/${effectiveRunId}/artifacts/${artifactId}/download-url${search}`,
        `react-run-artifact-${effectiveRunId}-${artifactId}`,
      );
      setActionResult(response);
    });
  }

  async function runAction(name: string, action: () => Promise<void>) {
    setBusyAction(name);
    setLoadError(null);
    try {
      await action();
    } catch (caught: unknown) {
      setLoadError(caught instanceof Error ? caught.message : "Run action failed");
    } finally {
      setBusyAction(null);
    }
  }

  const canCancel = status?.permitted_actions.includes("cancel") ?? false;
  const safeStructuredKeys = useMemo(
    () => Object.keys(result?.structured_result ?? {}),
    [result?.structured_result],
  );

  return (
    <section className="channel-page user-run-page">
      <header className="channel-header">
        <div>
          <p className="eyebrow">User-facing runs</p>
          <h1>Run workspace</h1>
          <p>
            Start a workflow, track safe progress, review action state, and keep legacy
            run links on Admin.
          </p>
        </div>
        <div className="channel-header__meta">
          <span className={`status-pill status-pill--${status?.state ?? "ready"}`}>
            {status?.state ?? "ready"}
          </span>
          {effectiveRunId ? <small>{effectiveRunId}</small> : <small>New run</small>}
        </div>
      </header>

      {loadError ? (
        <CommonState
          state={{
            action: null,
            state: "dependency_unavailable",
            summary: loadError,
            title: "Run data unavailable",
            trace_id: status?.trace_id ?? null,
          }}
        />
      ) : null}

      <section className="channel-section" aria-labelledby="start-run-heading">
        <div className="section-heading-row">
          <h2 id="start-run-heading">Start run</h2>
          {actionSummary(actionResult)}
        </div>
        <form className="admin-form" onSubmit={(event) => void handleStart(event)}>
          <label className="form-field">
            <span>Workflow</span>
            <input
              value={workflowId}
              onChange={(event) => setWorkflowId(event.target.value)}
              maxLength={80}
            />
            <small>Safe workflow reference used by the retained run API.</small>
          </label>
          <label className="form-field">
            <span>Request summary</span>
            <textarea
              value={safeInput}
              onChange={(event) => setSafeInput(event.target.value)}
              maxLength={240}
            />
            <small>Only this safe summary is shown in the browser.</small>
          </label>
          <div className="form-actions">
            <button type="submit" disabled={busyAction === "start"}>
              Start Run
            </button>
            {effectiveRunId ? (
              <button type="button" onClick={() => void refreshRun()}>
                Refresh
              </button>
            ) : null}
          </div>
        </form>
      </section>

      {effectiveRunId ? (
        <>
          <section className="channel-section" aria-labelledby="status-heading">
            <div className="section-heading-row">
              <h2 id="status-heading">Status and progress</h2>
              <span>{status?.trace_id ? `Trace ${status.trace_id}` : "Loading"}</span>
            </div>
            {status ? (
              <div className="channel-card">
                <span className={`status-pill status-pill--${status.state}`}>
                  {status.state}
                </span>
                <p>{status.progress_summary}</p>
                <dl className="compact-definition-list">
                  <div>
                    <dt>Cursor</dt>
                    <dd>{status.latest_timeline_cursor}</dd>
                  </div>
                  <div>
                    <dt>Result</dt>
                    <dd>{status.result_availability}</dd>
                  </div>
                  <div>
                    <dt>Artifacts</dt>
                    <dd>{status.artifact_availability}</dd>
                  </div>
                  <div>
                    <dt>Subscribed</dt>
                    <dd>{status.subscribed ? "yes" : "no"}</dd>
                  </div>
                </dl>
              </div>
            ) : (
              <CommonState
                state={{
                  action: null,
                  state: "loading",
                  summary: "Loading safe run status.",
                  title: "Loading run",
                  trace_id: null,
                }}
              />
            )}
          </section>

          <section className="channel-section" aria-labelledby="actions-heading">
            <div className="section-heading-row">
              <h2 id="actions-heading">Actions</h2>
              <span>Backend-permitted controls</span>
            </div>
            <div className="button-row">
              <button
                type="button"
                disabled={!canCancel || busyAction === "cancel"}
                onClick={() => void handleCancel()}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={busyAction === "subscribe"}
                onClick={() => void handleSubscribe()}
              >
                Subscribe
              </button>
              <button
                type="button"
                disabled={busyAction === "callback"}
                onClick={() => void handleCallback()}
              >
                Register Callback
              </button>
            </div>
            {status?.waiting_prompt ? (
              <div className="channel-card">
                <h3>{status.waiting_prompt.summary}</h3>
                <p>Prompt version {status.waiting_prompt.prompt_version}</p>
                <div className="button-row">
                  {status.waiting_prompt.allowed_actions.map((action) => (
                    <button
                      key={action}
                      type="button"
                      disabled={busyAction === action}
                      onClick={() => void handlePrompt(action)}
                    >
                      {labelAction(action)}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}
          </section>

          <section className="channel-section" aria-labelledby="timeline-heading">
            <div className="section-heading-row">
              <h2 id="timeline-heading">Timeline</h2>
              <span>{timeline?.items.length ?? 0} events</span>
            </div>
            <div className="channel-table">
              {(timeline?.items ?? []).map((event) => (
                <div className="channel-row" key={event.event_id}>
                  <div>
                    <strong>{event.event_type.replaceAll("_", " ")}</strong>
                    <span>{event.summary}</span>
                  </div>
                  <span>{event.state}</span>
                  <span>{event.severity}</span>
                  <small>{event.occurred_at}</small>
                </div>
              ))}
            </div>
          </section>

          <section className="channel-section" aria-labelledby="result-heading">
            <div className="section-heading-row">
              <h2 id="result-heading">Result</h2>
              <span>{result?.availability ?? "loading"}</span>
            </div>
            <div className="channel-card">
              <p>{result?.summary ?? "No safe result summary is available yet."}</p>
              <dl className="compact-definition-list">
                <div>
                  <dt>State</dt>
                  <dd>{result?.state ?? "unknown"}</dd>
                </div>
                <div>
                  <dt>Structured keys</dt>
                  <dd>{safeStructuredKeys.length ? safeStructuredKeys.join(", ") : "none"}</dd>
                </div>
              </dl>
            </div>
          </section>

          <section className="channel-section" aria-labelledby="artifacts-heading">
            <div className="section-heading-row">
              <h2 id="artifacts-heading">Artifacts</h2>
              <span>{artifacts?.items.length ?? 0} safe references</span>
            </div>
            <div className="channel-table">
              {(artifacts?.items ?? []).map((artifact) => (
                <div className="channel-row" key={artifact.artifact_id}>
                  <div>
                    <strong>{artifact.name}</strong>
                    <span>{artifact.user_facing_type}</span>
                  </div>
                  <span>{artifact.status}</span>
                  <span>{artifact.size_bytes ?? "unknown"} bytes</span>
                  <button
                    type="button"
                    disabled={!artifact.download_url_available || busyAction === "artifact"}
                    onClick={() => void handleArtifactGrant(artifact.artifact_id)}
                  >
                    Create Grant
                  </button>
                </div>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}

function workflowIdFromSearch(search: string): string | null {
  const params = new URLSearchParams(search || window.location.search);
  return params.get("workflow_id");
}

function labelAction(action: PromptAction): string {
  return action.charAt(0).toUpperCase() + action.slice(1);
}

function actionSummary(result: ActionResult | null) {
  if (!result) {
    return <span>No action yet</span>;
  }
  if ("state" in result && "run_id" in result) {
    return <span>Run {result.run_id} accepted</span>;
  }
  if ("accepted" in result) {
    return <span>{result.accepted ? "Decision accepted" : "Decision not accepted"}</span>;
  }
  if ("expires_at" in result) {
    return <span>Artifact grant created until {result.expires_at}</span>;
  }
  return <span>Status {"status" in result ? result.status : "updated"}</span>;
}
