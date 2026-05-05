import { Save, RotateCcw } from "lucide-react";
import type { FormEvent } from "react";

import type {
  BuilderMutationResult,
  BuilderSection,
  WorkflowDraftDocument,
  WorkflowJoinPolicySummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

export interface WorkflowDraftFormValues {
  description: string;
  join_policy: string;
  name: string;
  selected_profile_ref: string | null;
  selected_prompt_ref: string | null;
}

interface WorkflowSectionFormProps {
  dirty: boolean;
  draft: WorkflowDraftDocument;
  error: string | null;
  joinPolicies: WorkflowJoinPolicySummary[];
  mutationResult: BuilderMutationResult | null;
  onChange: (values: WorkflowDraftFormValues) => void;
  onForceStale: () => void;
  onSave: () => void;
  saving: boolean;
  sections: BuilderSection[];
  values: WorkflowDraftFormValues;
}

export function WorkflowSectionForm({
  dirty,
  draft,
  error,
  joinPolicies,
  mutationResult,
  onChange,
  onForceStale,
  onSave,
  saving,
  sections,
  values,
}: WorkflowSectionFormProps) {
  function update(field: keyof WorkflowDraftFormValues, value: string) {
    onChange({ ...values, [field]: value });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSave();
  }

  return (
    <section className="workflow-authoring" aria-labelledby="authoring-title">
      <aside className="workflow-section-rail" aria-label="Workflow sections">
        {sections.map((section) => (
          <a href={`#workflow-${section.section_id}`} key={section.section_id}>
            <span>{section.label}</span>
            <Badge tone={toneFor(section.status)}>{section.status}</Badge>
            <small>{section.summary}</small>
          </a>
        ))}
      </aside>
      <form className="workflow-form" onSubmit={submit}>
        <div className="form-header">
          <div>
            <p className="eyebrow">Draft</p>
            <h2 id="authoring-title">{draft.name}</h2>
          </div>
          <Badge tone={toneFor(draft.status)}>{draft.status}</Badge>
        </div>
        <dl className="workflow-draft-facts">
          <div>
            <dt>Revision</dt>
            <dd>{draft.revision}</dd>
          </div>
          <div>
            <dt>Lineage</dt>
            <dd>{draft.workflow_lineage_id}</dd>
          </div>
          <div>
            <dt>Scope</dt>
            <dd>{draft.tenant_label ?? "Platform"}</dd>
          </div>
        </dl>
        <label className="form-field" id="workflow-metadata">
          <span className="label">Name</span>
          <input
            className="ui-input"
            onChange={(event) => update("name", event.target.value)}
            value={values.name}
          />
        </label>
        <label className="form-field">
          <span className="label">Description</span>
          <textarea
            className="ui-input workflow-textarea"
            onChange={(event) => update("description", event.target.value)}
            rows={4}
            value={values.description}
          />
        </label>
        <label className="form-field" id="workflow-graph">
          <span className="label">Join policy</span>
          <select
            className="ui-input"
            onChange={(event) => update("join_policy", event.target.value)}
            value={values.join_policy}
          >
            {joinPolicies.map((policy) => (
              <option key={policy.policy_id} value={policy.policy_id}>
                {policy.label}
              </option>
            ))}
          </select>
        </label>
        <div className="form-actions">
          <span className={dirty ? "dirty-state" : "table-footer"}>
            {dirty ? "Unsaved changes" : "Draft matches last loaded revision"}
          </span>
          <div className="action-row">
            <Button
              disabled={saving}
              onClick={onForceStale}
              type="button"
              variant="secondary"
            >
              <RotateCcw aria-hidden="true" size={16} />
              Simulate stale save
            </Button>
            <Button disabled={saving} type="submit" variant="primary">
              <Save aria-hidden="true" size={16} />
              Save draft
            </Button>
          </div>
        </div>
        {error ? <p className="safe-error">{error}</p> : null}
        {mutationResult ? <MutationSummary result={mutationResult} /> : null}
      </form>
    </section>
  );
}

function MutationSummary({ result }: { result: BuilderMutationResult }) {
  return (
    <section className={`mutation-result ${result.status}`}>
      <p className="eyebrow">Save result</p>
      <h2>{result.status.replace("_", " ")}</h2>
      <p>{result.summary}</p>
      {result.stale_conflict ? <p>{result.stale_conflict.message}</p> : null}
      {result.audit_reference_id ? <small>{result.audit_reference_id}</small> : null}
    </section>
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
