import {
  AlertTriangle,
  CheckCircle2,
  Play,
  RefreshCw,
  Send,
  Wrench,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ReactAdminShellState } from "../../api/generated/reactAdminApi";
import { buildIdempotencyKey } from "../../utils/adminActionMetadata";
import { CommonState } from "../states/CommonState";

interface ScopeSummary {
  scope_type: string;
  tenant_id: string | null;
  label: string;
}

interface AdminAction {
  action_id: string;
  label: string;
  method: string;
  href: string;
  enabled: boolean;
  disabled_reason: string | null;
  requires_idempotency_key: boolean;
}

interface WorkspaceCard {
  card_id: string;
  label: string;
  value: string;
  summary: string;
  tone: string;
}

interface Revision {
  design_revision_id: string;
  revision_number: number;
  author_role_key: string;
  safe_summary: string;
  artifact_id: string | null;
  payload_digest: string;
  previous_revision_id: string | null;
}

interface SessionSummary {
  design_review_session_id: string;
  tenant_id: string;
  status: string;
  request_summary: string;
  active_revision_number: number;
  quorum_policy_key: string;
  workflow_version_bundle_id: string | null;
  owner_principal_id: string;
  current_revision: Revision | null;
}

interface Assignment {
  design_reviewer_assignment_id: string;
  reviewer_key: string;
  role_key: string;
  prompt_version_id: string | null;
  profile_version_id: string | null;
  provider_reference: string | null;
  enabled: boolean;
}

interface Verdict {
  design_reviewer_verdict_id: string;
  reviewer_key: string;
  verdict: string;
  score: number;
  blocking_issue_count: number;
  safe_feedback_summary: string;
  artifact_id: string | null;
  output_digest: string;
  usage_summary: Record<string, unknown>;
}

interface QuorumDecision {
  state: { kind: string; summary: string };
  status: string | null;
  approval_count: number | null;
  blocking_issue_count: number | null;
  next_action: string | null;
  policy_version: string | null;
  safe_rationale: string | null;
}

interface RoundSummary {
  design_review_round_id: string;
  design_review_session_id: string;
  design_revision_id: string;
  round_number: number;
  status: string;
  workflow_run_id: string | null;
  reviewer_count: number;
  quorum_count: number;
}

interface RoundDetail {
  round: RoundSummary;
  assignments: Assignment[];
  verdicts: Verdict[];
  quorum_decision: QuorumDecision;
}

interface ManualDecision {
  design_manual_decision_id: string;
  design_review_session_id: string;
  design_review_round_id: string | null;
  decision_type: string;
  actor_principal_id: string;
  safe_rationale: string;
  accepted_risk: boolean;
}

interface Handoff {
  state: { kind: string; summary: string };
  design_development_handoff_id: string | null;
  approved_revision_id: string | null;
  artifact_id: string | null;
  safe_summary: string | null;
  output_digest: string | null;
  status: string | null;
}

interface CoordinatorState {
  manual_resolution_required: boolean;
  next_action: string;
  latest_round: RoundSummary | null;
}

interface SessionDetail {
  session: SessionSummary;
  revisions: Revision[];
  rounds: RoundDetail[];
  manual_decisions: ManualDecision[];
  handoff: Handoff;
  coordinator: CoordinatorState | null;
}

interface WorkflowOption {
  workflow_version_bundle_id: string;
  label: string;
  workflow_key: string;
  display_version: string;
  status: string;
}

interface QuorumPolicyOption {
  policy_key: string;
  label: string;
  summary: string;
}

interface TemplateSetup {
  status: string;
  template_key: string;
  publish_gate_status: string;
  required_evidence_status: string;
  safe_summary: string;
  workflow_draft_id: string | null;
  workflow_lineage_id: string | null;
  workflow_draft_revision_id: string | null;
  workflow_key: string | null;
  display_name: string | null;
  agent_test_suite_id: string | null;
  latest_run_id: string | null;
  deterministic_run_id: string | null;
  model_safe_run_id: string | null;
  evidence_modes: string[];
  ready_to_publish: boolean;
  install_action: AdminAction;
}

interface WorkspaceEnvelope {
  title: string;
  description: string;
  active_scope: ScopeSummary;
  state: ReactAdminShellState;
  summary_cards: WorkspaceCard[];
  sessions: SessionSummary[];
  selected_session: SessionDetail | null;
  workflow_options: WorkflowOption[];
  quorum_policies: QuorumPolicyOption[];
  template_setup: TemplateSetup;
  actions: {
    create_session: AdminAction;
    refresh: AdminAction;
    launch_round: AdminAction | null;
    manual_decision: AdminAction | null;
  };
}

interface MutationState {
  title: string;
  summary: string;
  tone: "success" | "warning" | "danger";
}

export function DesignReviewWorkspacePage({
  workspaceUrl,
}: {
  workspaceUrl: string;
}) {
  const [envelope, setEnvelope] = useState<WorkspaceEnvelope | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [currentUrl, setCurrentUrl] = useState(workspaceUrl);
  const [requestSummary, setRequestSummary] = useState("");
  const [quorumPolicy, setQuorumPolicy] = useState("four_of_five_no_blockers");
  const [workflowId, setWorkflowId] = useState("");
  const [manualDecision, setManualDecision] = useState("revise");
  const [manualRationale, setManualRationale] = useState("");
  const [nextRevisionSummary, setNextRevisionSummary] = useState("");
  const [acceptedRisk, setAcceptedRisk] = useState(false);
  const [mutationState, setMutationState] = useState<MutationState | null>(null);

  useEffect(() => {
    void loadWorkspace(currentUrl);
  }, [currentUrl]);

  async function loadWorkspace(url: string) {
    try {
      const response = await fetch(url, {
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(await safeErrorDetail(response));
      }
      const payload = (await response.json()) as WorkspaceEnvelope;
      setEnvelope(payload);
      setLoadError(null);
      setWorkflowId(
        payload.selected_session?.session.workflow_version_bundle_id ??
          payload.workflow_options[0]?.workflow_version_bundle_id ??
          "",
      );
      setQuorumPolicy(payload.quorum_policies[0]?.policy_key ?? quorumPolicy);
    } catch (caught) {
      setLoadError(caught instanceof Error ? caught.message : "Workspace unavailable");
    }
  }

  const selected = envelope?.selected_session ?? null;
  const latestRound = useMemo(() => {
    if (!selected) {
      return null;
    }
    return selected.rounds.at(-1) ?? null;
  }, [selected]);

  async function createSession() {
    if (!envelope || !requestSummary.trim()) {
      return;
    }
    const response = await postJson(envelope.actions.create_session.href, {
      tenant_id: envelope.active_scope.tenant_id,
      request_summary: requestSummary.trim(),
      quorum_policy_key: quorumPolicy,
      workflow_version_bundle_id: workflowId || null,
      idempotency_key: buildIdempotencyKey("design-review-create"),
    });
    setMutationState({
      title: "Session created",
      summary: "The session is now available in the workspace.",
      tone: "success",
    });
    setRequestSummary("");
    const sessionId = stringField(response, "design_review_session_id");
    setCurrentUrl(workspaceUrlForSession(envelope, sessionId));
  }

  async function launchRound() {
    if (!envelope?.actions.launch_round || !workflowId) {
      return;
    }
    await postJson(envelope.actions.launch_round.href, {
      tenant_id: envelope.active_scope.tenant_id,
      workflow_version_bundle_id: workflowId,
      reviewers: reviewerSet(),
      max_rounds: 3,
      execution_mode: "deterministic",
      idempotency_key: buildIdempotencyKey("design-review-launch"),
    });
    setMutationState({
      title: "Round launched",
      summary: "The coordinator created a live review round.",
      tone: "success",
    });
    setCurrentUrl(workspaceUrlForSession(envelope, selected?.session.design_review_session_id));
  }

  async function recordManualDecision() {
    if (!envelope?.actions.manual_decision || !latestRound) {
      return;
    }
    await postJson(envelope.actions.manual_decision.href, {
      tenant_id: envelope.active_scope.tenant_id,
      round_id: latestRound.round.design_review_round_id,
      decision_type: manualDecision,
      safe_rationale: manualRationale.trim(),
      accepted_risk: acceptedRisk,
      next_revision_summary: nextRevisionSummary.trim() || null,
      idempotency_key: buildIdempotencyKey("design-review-manual"),
    });
    setMutationState({
      title: "Decision recorded",
      summary: "The manual decision has been persisted.",
      tone: "success",
    });
    setManualRationale("");
    setNextRevisionSummary("");
    setCurrentUrl(workspaceUrlForSession(envelope, selected?.session.design_review_session_id));
  }

  async function installTemplate() {
    if (!envelope?.active_scope.tenant_id) {
      return;
    }
    const setup = envelope.template_setup;
    await postJson(setup.install_action.href, {
      tenant_id: envelope.active_scope.tenant_id,
      template_key: setup.template_key,
      idempotency_key: buildIdempotencyKey("design-review-template"),
      run_required_tests: true,
      safe_mode: "both",
    });
    setMutationState({
      title: "Template ready",
      summary: "Council setup and required evidence are refreshed.",
      tone: "success",
    });
    setCurrentUrl(envelope.actions.refresh.href);
  }

  if (loadError && !envelope) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Design reviews unavailable",
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
          summary: "Loading live sessions, rounds, decisions, and handoffs.",
          title: "Loading design reviews",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="design-review-page">
      <section className="patterns-hero design-review-hero">
        <p className="eyebrow">Design reviews</p>
        <h2>{envelope.title}</h2>
        <p>{envelope.description}</p>
        <small>{envelope.active_scope.label}</small>
      </section>

      {loadError ? <p className="safe-error">{loadError}</p> : null}
      {mutationState ? (
        <article className={`mutation-note ${mutationState.tone}`} role="status">
          <CheckCircle2 aria-hidden="true" size={18} />
          <div>
            <strong>{mutationState.title}</strong>
            <p>{mutationState.summary}</p>
          </div>
        </article>
      ) : null}

      <section className="design-review-summary" aria-label="Workspace summary">
        {envelope.summary_cards.map((card) => (
          <article className={`design-review-card ${card.tone}`} key={card.card_id}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <p>{card.summary}</p>
          </article>
        ))}
      </section>

      <TemplateSetupPanel
        onInstall={() => void installTemplate()}
        setup={envelope.template_setup}
      />

      <section className="design-review-grid">
        <CreateSessionPanel
          envelope={envelope}
          onCreate={() => void createSession()}
          quorumPolicy={quorumPolicy}
          requestSummary={requestSummary}
          setQuorumPolicy={setQuorumPolicy}
          setRequestSummary={setRequestSummary}
          setWorkflowId={setWorkflowId}
          workflowId={workflowId}
        />
        <SessionListPanel
          envelope={envelope}
          onRefresh={() => setCurrentUrl(envelope.actions.refresh.href)}
          onSelect={(sessionId) => setCurrentUrl(workspaceUrlForSession(envelope, sessionId))}
        />
      </section>

      {selected ? (
        <section className="design-review-detail" aria-label="Selected design review">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Selected session</p>
              <h2>{selected.session.request_summary}</h2>
            </div>
            <span className="status-pill">{selected.session.status}</span>
          </div>
          <ActionPanel
            acceptedRisk={acceptedRisk}
            envelope={envelope}
            latestRound={latestRound}
            manualDecision={manualDecision}
            manualRationale={manualRationale}
            nextRevisionSummary={nextRevisionSummary}
            onLaunch={() => void launchRound()}
            onManualDecision={() => void recordManualDecision()}
            selected={selected}
            setAcceptedRisk={setAcceptedRisk}
            setManualDecision={setManualDecision}
            setManualRationale={setManualRationale}
            setNextRevisionSummary={setNextRevisionSummary}
            setWorkflowId={setWorkflowId}
            workflowId={workflowId}
          />
          <RevisionPanel revisions={selected.revisions} />
          <RoundPanel rounds={selected.rounds} />
          <ManualDecisionPanel decisions={selected.manual_decisions} />
          <HandoffPanel handoff={selected.handoff} />
        </section>
      ) : (
        <CommonState state={envelope.state} />
      )}
    </div>
  );
}

function TemplateSetupPanel({
  onInstall,
  setup,
}: {
  onInstall: () => void;
  setup: TemplateSetup;
}) {
  const canInstall = setup.install_action.enabled;
  return (
    <section className="design-review-panel template-setup-panel" aria-label="Template setup">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Council template</p>
          <h2>{setup.display_name ?? "Design Reviewer Council"}</h2>
        </div>
        <span className={`status-pill ${setup.ready_to_publish ? "success" : ""}`}>
          {setup.status.replaceAll("_", " ")}
        </span>
      </div>
      <p>{setup.safe_summary}</p>
      <dl className="decision-grid template-state-grid">
        <div>
          <dt>Publish gate</dt>
          <dd>{setup.publish_gate_status.replaceAll("_", " ")}</dd>
        </div>
        <div>
          <dt>Evidence</dt>
          <dd>{setup.required_evidence_status.replaceAll("_", " ")}</dd>
        </div>
        <div>
          <dt>Modes</dt>
          <dd>{setup.evidence_modes.length ? setup.evidence_modes.join(", ") : "pending"}</dd>
        </div>
        <div>
          <dt>Revision</dt>
          <dd>{setup.workflow_draft_revision_id ?? "not installed"}</dd>
        </div>
      </dl>
      <div className="template-actions">
        <button
          className="primary-button"
          disabled={!canInstall}
          onClick={onInstall}
          type="button"
        >
          <Wrench aria-hidden="true" size={16} />
          {setup.status === "not_installed" ? "Install template" : "Refresh evidence"}
        </button>
        {!canInstall ? <small>{setup.install_action.disabled_reason}</small> : null}
      </div>
    </section>
  );
}

function CreateSessionPanel({
  envelope,
  onCreate,
  quorumPolicy,
  requestSummary,
  setQuorumPolicy,
  setRequestSummary,
  setWorkflowId,
  workflowId,
}: {
  envelope: WorkspaceEnvelope;
  onCreate: () => void;
  quorumPolicy: string;
  requestSummary: string;
  setQuorumPolicy: (value: string) => void;
  setRequestSummary: (value: string) => void;
  setWorkflowId: (value: string) => void;
  workflowId: string;
}) {
  return (
    <section className="design-review-panel" aria-label="Create design review">
      <div className="section-heading">
        <div>
          <p className="eyebrow">New session</p>
          <h2>Create request</h2>
        </div>
      </div>
      <label>
        Request summary
        <textarea
          onChange={(event) => setRequestSummary(event.target.value)}
          rows={5}
          value={requestSummary}
        />
      </label>
      <label>
        Quorum policy
        <select
          onChange={(event) => setQuorumPolicy(event.target.value)}
          value={quorumPolicy}
        >
          {envelope.quorum_policies.map((policy) => (
            <option key={policy.policy_key} value={policy.policy_key}>
              {policy.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Workflow
        <select
          onChange={(event) => setWorkflowId(event.target.value)}
          value={workflowId}
        >
          <option value="">No workflow selected</option>
          {envelope.workflow_options.map((option) => (
            <option
              key={option.workflow_version_bundle_id}
              value={option.workflow_version_bundle_id}
            >
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <button
        className="primary-button"
        disabled={!requestSummary.trim()}
        onClick={onCreate}
        type="button"
      >
        <Send aria-hidden="true" size={16} />
        Create session
      </button>
    </section>
  );
}

function SessionListPanel({
  envelope,
  onRefresh,
  onSelect,
}: {
  envelope: WorkspaceEnvelope;
  onRefresh: () => void;
  onSelect: (sessionId: string) => void;
}) {
  return (
    <section className="design-review-panel" aria-label="Session history">
      <div className="section-heading">
        <div>
          <p className="eyebrow">History</p>
          <h2>Sessions</h2>
        </div>
        <button className="icon-button" onClick={onRefresh} title="Refresh" type="button">
          <RefreshCw aria-hidden="true" size={16} />
          <span className="sr-only">Refresh</span>
        </button>
      </div>
      {envelope.sessions.length === 0 ? (
        <p className="muted-copy">No live sessions exist for this tenant.</p>
      ) : (
        <table className="admin-table compact-table">
          <thead>
            <tr>
              <th>Summary</th>
              <th>Status</th>
              <th>Revision</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {envelope.sessions.map((session) => (
              <tr key={session.design_review_session_id}>
                <td>{session.request_summary}</td>
                <td>{session.status}</td>
                <td>{session.active_revision_number}</td>
                <td>
                  <button
                    className="text-button"
                    onClick={() => onSelect(session.design_review_session_id)}
                    type="button"
                  >
                    Select
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

function ActionPanel({
  acceptedRisk,
  envelope,
  latestRound,
  manualDecision,
  manualRationale,
  nextRevisionSummary,
  onLaunch,
  onManualDecision,
  selected,
  setAcceptedRisk,
  setManualDecision,
  setManualRationale,
  setNextRevisionSummary,
  setWorkflowId,
  workflowId,
}: {
  acceptedRisk: boolean;
  envelope: WorkspaceEnvelope;
  latestRound: RoundDetail | null;
  manualDecision: string;
  manualRationale: string;
  nextRevisionSummary: string;
  onLaunch: () => void;
  onManualDecision: () => void;
  selected: SessionDetail;
  setAcceptedRisk: (value: boolean) => void;
  setManualDecision: (value: string) => void;
  setManualRationale: (value: string) => void;
  setNextRevisionSummary: (value: string) => void;
  setWorkflowId: (value: string) => void;
  workflowId: string;
}) {
  const canLaunch = Boolean(envelope.actions.launch_round?.enabled && workflowId);
  const manualRequired = Boolean(selected.coordinator?.manual_resolution_required);
  return (
    <section className="design-review-actions" aria-label="Session actions">
      <div className="action-cluster">
        <label>
          Launch workflow
          <select
            onChange={(event) => setWorkflowId(event.target.value)}
            value={workflowId}
          >
            <option value="">No workflow selected</option>
            {envelope.workflow_options.map((option) => (
              <option
                key={option.workflow_version_bundle_id}
                value={option.workflow_version_bundle_id}
              >
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <button
          className="primary-button"
          disabled={!canLaunch}
          onClick={onLaunch}
          type="button"
        >
          <Play aria-hidden="true" size={16} />
          Launch round
        </button>
        {!canLaunch ? (
          <small>{envelope.actions.launch_round?.disabled_reason}</small>
        ) : null}
      </div>
      {manualRequired ? (
        <div className="manual-action-form">
          <AlertTriangle aria-hidden="true" size={18} />
          <label>
            Decision
            <select
              onChange={(event) => setManualDecision(event.target.value)}
              value={manualDecision}
            >
              <option value="revise">Revise</option>
              <option value="approve_exception">Approve exception</option>
              <option value="retry">Retry</option>
              <option value="cancel">Cancel</option>
            </select>
          </label>
          <label>
            Safe rationale
            <textarea
              onChange={(event) => setManualRationale(event.target.value)}
              rows={3}
              value={manualRationale}
            />
          </label>
          <label>
            Next revision summary
            <input
              onChange={(event) => setNextRevisionSummary(event.target.value)}
              value={nextRevisionSummary}
            />
          </label>
          <label className="checkbox-row">
            <input
              checked={acceptedRisk}
              onChange={(event) => setAcceptedRisk(event.target.checked)}
              type="checkbox"
            />
            Accepted risk
          </label>
          <button
            className="primary-button"
            disabled={!latestRound || !manualRationale.trim()}
            onClick={onManualDecision}
            type="button"
          >
            <Send aria-hidden="true" size={16} />
            Record decision
          </button>
        </div>
      ) : null}
    </section>
  );
}

function RevisionPanel({ revisions }: { revisions: Revision[] }) {
  return (
    <section className="design-review-panel" aria-label="Revision summaries">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Revisions</p>
          <h2>Safe summaries</h2>
        </div>
      </div>
      <div className="revision-list">
        {revisions.map((revision) => (
          <article key={revision.design_revision_id}>
            <strong>Revision {revision.revision_number}</strong>
            <p>{revision.safe_summary}</p>
            <small>Digest {revision.payload_digest}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function RoundPanel({ rounds }: { rounds: RoundDetail[] }) {
  return (
    <section className="design-review-panel" aria-label="Review rounds">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Rounds</p>
          <h2>Reviewer evidence</h2>
        </div>
      </div>
      {rounds.length === 0 ? (
        <p className="muted-copy">No review rounds have been launched.</p>
      ) : (
        rounds.map((round) => (
          <article className="round-card" key={round.round.design_review_round_id}>
            <div className="round-heading">
              <strong>Round {round.round.round_number}</strong>
              <span className="status-pill">{round.round.status}</span>
            </div>
            <p>
              {round.round.reviewer_count} reviewers, quorum {round.round.quorum_count}
            </p>
            {round.round.workflow_run_id ? (
              <small>Run {round.round.workflow_run_id}</small>
            ) : null}
            <dl className="decision-grid">
              <div>
                <dt>Decision</dt>
                <dd>{round.quorum_decision.status ?? round.quorum_decision.state.kind}</dd>
              </div>
              <div>
                <dt>Approvals</dt>
                <dd>{round.quorum_decision.approval_count ?? 0}</dd>
              </div>
              <div>
                <dt>Blockers</dt>
                <dd>{round.quorum_decision.blocking_issue_count ?? 0}</dd>
              </div>
            </dl>
            <div className="verdict-grid">
              {round.verdicts.map((verdict) => (
                <article key={verdict.design_reviewer_verdict_id}>
                  <strong>{verdict.reviewer_key}</strong>
                  <span>{verdict.verdict}</span>
                  <p>{verdict.safe_feedback_summary}</p>
                  <small>
                    Score {verdict.score} · Blockers {verdict.blocking_issue_count}
                  </small>
                </article>
              ))}
            </div>
          </article>
        ))
      )}
    </section>
  );
}

function ManualDecisionPanel({ decisions }: { decisions: ManualDecision[] }) {
  return (
    <section className="design-review-panel" aria-label="Manual decisions">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Manual decisions</p>
          <h2>Human actions</h2>
        </div>
      </div>
      {decisions.length === 0 ? (
        <p className="muted-copy">No manual decisions have been recorded.</p>
      ) : (
        <ul className="decision-list">
          {decisions.map((decision) => (
            <li key={decision.design_manual_decision_id}>
              <strong>{decision.decision_type}</strong>
              <p>{decision.safe_rationale}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function HandoffPanel({ handoff }: { handoff: Handoff }) {
  return (
    <section className="design-review-panel" aria-label="Development handoff">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Handoff</p>
          <h2>Development reference</h2>
        </div>
      </div>
      {handoff.design_development_handoff_id ? (
        <dl className="decision-grid">
          <div>
            <dt>Status</dt>
            <dd>{handoff.status}</dd>
          </div>
          <div>
            <dt>Approved revision</dt>
            <dd>{handoff.approved_revision_id}</dd>
          </div>
          <div>
            <dt>Digest</dt>
            <dd>{handoff.output_digest}</dd>
          </div>
          <div>
            <dt>Summary</dt>
            <dd>{handoff.safe_summary}</dd>
          </div>
        </dl>
      ) : (
        <p className="muted-copy">{handoff.state.summary}</p>
      )}
    </section>
  );
}

async function postJson(url: string, payload: Record<string, unknown>) {
  const response = await fetch(url, {
    body: JSON.stringify(payload),
    credentials: "same-origin",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(await safeErrorDetail(response));
  }
  return (await response.json()) as Record<string, unknown>;
}

async function safeErrorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    return `Request failed with status ${response.status}`;
  }
  return `Request failed with status ${response.status}`;
}

function stringField(record: Record<string, unknown>, key: string): string | null {
  const value = record[key];
  return typeof value === "string" ? value : null;
}

function workspaceUrlForSession(
  envelope: WorkspaceEnvelope,
  sessionId: string | null | undefined,
): string {
  const params = new URLSearchParams();
  if (envelope.active_scope.tenant_id) {
    params.set("tenant_id", envelope.active_scope.tenant_id);
  }
  if (sessionId) {
    params.set("session_id", sessionId);
  }
  const query = params.toString();
  return `/admin/app/design-reviews/bootstrap.json${query ? `?${query}` : ""}`;
}

function reviewerSet() {
  return [0, 1, 2, 3, 4].map((index) => ({
    enabled: true,
    reviewer_key: `reviewer-${index}`,
    role_key: `reviewer-role-${index}`,
  }));
}
