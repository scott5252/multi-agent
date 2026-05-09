import type {
  WorkflowReferenceCatalog,
  WorkflowReferenceOption,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface WorkflowReferencePickerProps {
  catalog: WorkflowReferenceCatalog;
  selectedProfileRef: string | null;
  selectedPromptRef: string | null;
  onProfileChange: (referenceId: string) => void;
  onPromptChange: (referenceId: string) => void;
}

export function WorkflowReferencePicker({
  catalog,
  selectedProfileRef,
  selectedPromptRef,
  onProfileChange,
  onPromptChange,
}: WorkflowReferencePickerProps) {
  return (
    <section
      className="workflow-reference-picker"
      id="workflow-references"
      aria-labelledby="references-title"
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">References</p>
          <h2 id="references-title">Pinned runtime inputs</h2>
        </div>
      </div>
      <div className="reference-controls">
        <label className="form-field">
          <span className="label">Prompt</span>
          <select
            className="ui-input"
            onChange={(event) => onPromptChange(event.target.value)}
            value={selectedPromptRef ?? ""}
          >
            {catalog.prompt_options.map((option) => (
              <option key={option.reference_id} value={option.reference_id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span className="label">Runtime profile</span>
          <select
            className="ui-input"
            onChange={(event) => onProfileChange(event.target.value)}
            value={selectedProfileRef ?? ""}
          >
            {catalog.profile_options.map((option) => (
              <option key={option.reference_id} value={option.reference_id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="reference-grid">
        {[
          ...catalog.provider_options,
          ...catalog.skill_options,
          ...catalog.test_suite_options,
          ...catalog.subworkflow_options,
        ].map((option) => (
          <ReferenceCard key={option.reference_id} option={option} />
        ))}
      </div>
    </section>
  );
}

function ReferenceCard({ option }: { option: WorkflowReferenceOption }) {
  return (
    <article className="reference-card">
      <div className="card-heading">
        <strong>{option.label}</strong>
        <Badge tone={toneFor(option.readiness_status)}>
          {option.readiness_status}
        </Badge>
      </div>
      <p>{option.safe_summary}</p>
      <small>
        {option.kind}
        {option.version_label ? ` / ${option.version_label}` : ""}
      </small>
      {option.href ? <a href={option.href}>Open source</a> : null}
    </article>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready" || status === "published") {
    return "success";
  }
  if (status === "blocked" || status === "critical") {
    return "critical";
  }
  if (status === "warning" || status === "stale") {
    return "warning";
  }
  return "info";
}
