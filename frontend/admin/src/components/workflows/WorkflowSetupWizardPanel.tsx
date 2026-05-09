import { ListChecks, Rocket, Workflow } from "lucide-react";

import type {
  WorkflowPublishReadiness,
  WorkflowValidationSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import type { WorkflowEditorDocument } from "./workflowDocumentEditor";
import {
  buildWorkflowSetupProgress,
  type WorkflowSetupStepStatus,
} from "./workflowSetupWizard";

interface WorkflowSetupWizardPanelProps {
  document: WorkflowEditorDocument;
  onApplyStarter: () => void;
  publishedVersionId: string | null;
  publishReadiness: WorkflowPublishReadiness;
  tenantId: string | null;
  validation: WorkflowValidationSummary;
}

export function WorkflowSetupWizardPanel({
  document,
  onApplyStarter,
  publishedVersionId,
  publishReadiness,
  tenantId,
  validation,
}: WorkflowSetupWizardPanelProps) {
  const progress = buildWorkflowSetupProgress({
    document,
    publishedVersionId,
    publishReadiness,
    validation,
  });
  const tenantQuery = tenantId ? `tenant_id=${encodeURIComponent(tenantId)}` : "";
  const launchWorkflowId = publishedVersionId ?? document.workflow_key;
  const runHref = queryHref("/admin/app/channels/runs", [
    tenantQuery,
    launchWorkflowId ? `workflow_id=${encodeURIComponent(launchWorkflowId)}` : "",
  ]);
  const designReviewHref = queryHref("/admin/app/design-reviews", [
    tenantQuery,
    publishedVersionId
      ? `workflow_version_bundle_id=${encodeURIComponent(publishedVersionId)}`
      : "",
  ]);

  return (
    <section
      aria-labelledby="workflow-setup-wizard-title"
      className="workflow-setup-wizard"
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">Guided setup</p>
          <h2 id="workflow-setup-wizard-title">Custom workflow launch checklist</h2>
          <p className="table-footer">
            {progress.completeCount}/{progress.totalCount} steps ready
          </p>
        </div>
        <Badge tone={progress.completeCount === progress.totalCount ? "success" : "info"}>
          {progress.percent}%
        </Badge>
      </div>
      <div
        aria-label="Workflow setup progress"
        aria-valuemax={100}
        aria-valuemin={0}
        aria-valuenow={progress.percent}
        className="workflow-progress"
        role="progressbar"
      >
        <span style={{ width: `${progress.percent}%` }} />
      </div>
      <div className="workflow-setup-actions">
        <Button onClick={onApplyStarter} type="button" variant="secondary">
          <ListChecks aria-hidden="true" size={16} />
          Apply three-agent starter
        </Button>
        <a className="action-link" href="#workflow-test-evidence">
          Evidence setup
        </a>
        <a className="action-link" href="#workflow-publish">
          Publish gate
        </a>
      </div>
      <div className="workflow-setup-step-grid">
        {progress.steps.map((step) => (
          <a className="workflow-setup-step" href={step.href} key={step.key}>
            <div className="card-heading">
              <strong>{step.title}</strong>
              <Badge tone={toneFor(step.status)}>{step.status}</Badge>
            </div>
            <p>{step.summary}</p>
          </a>
        ))}
      </div>
      <section
        aria-labelledby="workflow-runtime-launch-title"
        className="workflow-runtime-launch"
        id="workflow-runtime-launch"
      >
        <div>
          <p className="eyebrow">Launch</p>
          <h3 id="workflow-runtime-launch-title">Runtime and review handoff</h3>
        </div>
        <div className="workflow-runtime-actions">
          <a className="ui-button primary" href={runHref}>
            <Rocket aria-hidden="true" size={16} />
            Open runtime launch
          </a>
          <a className="ui-button secondary" href={designReviewHref}>
            <Workflow aria-hidden="true" size={16} />
            Select in Design Reviews
          </a>
          {publishedVersionId ? (
            <a
              className="ui-button secondary"
              href={`/admin/app/workflows/versions/${encodeURIComponent(publishedVersionId)}${tenantId ? `?tenant_id=${encodeURIComponent(tenantId)}` : ""}`}
            >
              <Workflow aria-hidden="true" size={16} />
              Inspect published graph
            </a>
          ) : null}
        </div>
        <p className="table-footer">
          {publishedVersionId
            ? "Published bundle is ready for runtime selection."
            : "Publish the draft to activate runtime selection links."}
        </p>
      </section>
    </section>
  );
}

function queryHref(path: string, parts: string[]): string {
  const query = parts.filter(Boolean).join("&");
  return query ? `${path}?${query}` : path;
}

function toneFor(status: WorkflowSetupStepStatus): "success" | "warning" | "info" {
  if (status === "complete") {
    return "success";
  }
  if (status === "active") {
    return "warning";
  }
  return "info";
}
