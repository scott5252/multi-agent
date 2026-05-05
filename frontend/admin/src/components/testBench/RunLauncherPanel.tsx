import { PlayCircle } from "lucide-react";
import { useState } from "react";

import type {
  SafeExecutionModeOption,
  TestBenchMutationResult,
  TestSuiteDetail,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface RunLauncherPanelProps {
  launchResult: TestBenchMutationResult | null;
  onLaunch: (href: string, safeMode: string) => void;
  suite: TestSuiteDetail;
}

export function RunLauncherPanel({
  launchResult,
  onLaunch,
  suite,
}: RunLauncherPanelProps) {
  const [safeMode, setSafeMode] = useState(suite.run_launcher.default_safe_mode);
  const launchAction = suite.summary.authorized_actions.find(
    (action) => action.action_id === "launch-run",
  );
  const activeMode = suite.run_launcher.safe_modes.find(
    (mode) => mode.mode_id === safeMode,
  );
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="run-launch-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Execute</p>
          <h2 id="run-launch-title">Safe run launch</h2>
        </div>
        {launchAction ? (
          <Button
            onClick={() => onLaunch(launchAction.href, safeMode)}
            type="button"
            variant="primary"
          >
            <PlayCircle aria-hidden="true" size={16} />
            Launch run
          </Button>
        ) : null}
      </div>
      <label className="field-label" htmlFor="safe-mode">
        Safe execution mode
      </label>
      <select
        className="select-control"
        id="safe-mode"
        onChange={(event) => setSafeMode(event.target.value)}
        value={safeMode}
      >
        {suite.run_launcher.safe_modes.map((mode) => (
          <option key={mode.mode_id} value={mode.mode_id}>
            {mode.label}
          </option>
        ))}
      </select>
      {activeMode ? <ModeCard mode={activeMode} /> : null}
      {launchResult ? (
        <article className={`mutation-result ${launchResult.status}`}>
          <p className="eyebrow">Launch result</p>
          <h3>{launchResult.status}</h3>
          <p>{launchResult.summary}</p>
          {launchResult.run ? <p>{launchResult.run.progress.summary}</p> : null}
        </article>
      ) : null}
    </section>
  );
}

function ModeCard({ mode }: { mode: SafeExecutionModeOption }) {
  return (
    <article className="governance-card mode-card">
      <div className="card-heading">
        <strong>{mode.label}</strong>
        <Badge tone={toneFor(mode.allowed_status)}>{mode.allowed_status}</Badge>
      </div>
      <p>{mode.policy_reason}</p>
      <dl className="compact-dl">
        <div>
          <dt>Model</dt>
          <dd>{mode.model_behavior}</dd>
        </div>
        <div>
          <dt>Tools</dt>
          <dd>{mode.tool_behavior}</dd>
        </div>
        <div>
          <dt>Posture</dt>
          <dd>{mode.side_effect_posture}</dd>
        </div>
      </dl>
    </article>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
