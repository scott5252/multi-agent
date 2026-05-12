import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ClipboardCheck,
  ExternalLink,
  FileText,
  GitBranch,
  KeyRound,
  ListChecks,
  Rocket,
  Save,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";

import {
  createWorkflowDraft,
  fetchWorkflowBuilder,
  fetchWorkflowLookups,
  publishWorkflowDraft,
  saveWorkflowDraft,
  validateWorkflowDraft,
} from "../../api/client";
import type {
  BuilderMutationResult,
  WorkflowBuilderEnvelope,
  WorkflowReferenceCatalog,
} from "../../api/generated/reactAdminApi";
import { buildIdempotencyKey } from "../../utils/adminActionMetadata";
import { Badge, Button } from "../primitives";
import { CommonState } from "../states/CommonState";
import {
  applyWorkflowMetadata,
  cloneWorkflowDocument,
  type WorkflowEditorDocument,
} from "./workflowDocumentEditor";
import type { WorkflowDraftFormValues } from "./WorkflowSectionForm";
import {
  attachWorkflowEvidenceRequirement,
  buildBlankWorkflowDocument,
  buildGenericBlueprintDocument,
  buildWorkflowSetupProgress,
  DEFAULT_WORKFLOW_SCENARIO_INTAKE,
  intakeWithDerivedKey,
  normalizeWorkflowKey,
  WORKFLOW_ONBOARDING_STEPS,
  type WorkflowScenarioIntake,
  type WorkflowSetupStep,
  type WorkflowSetupStepKey,
} from "./workflowSetupWizard";

interface WorkflowOnboardingWizardPageProps {
  builderUrl: string;
  lookupsUrl: string;
}

const STEP_ORDER = WORKFLOW_ONBOARDING_STEPS.map((step) => step.key);

export function WorkflowOnboardingWizardPage({
  builderUrl,
  lookupsUrl,
}: WorkflowOnboardingWizardPageProps) {
  const [activeStep, setActiveStep] =
    useState<WorkflowSetupStepKey>("scenario");
  const [catalog, setCatalog] = useState<WorkflowReferenceCatalog | null>(null);
  const [dirty, setDirty] = useState(false);
  const [editorDocument, setEditorDocument] =
    useState<WorkflowEditorDocument | null>(null);
  const [envelope, setEnvelope] = useState<WorkflowBuilderEnvelope | null>(null);
  const [formValues, setFormValues] = useState<WorkflowDraftFormValues | null>(
    null,
  );
  const [intake, setIntake] = useState<WorkflowScenarioIntake>(
    DEFAULT_WORKFLOW_SCENARIO_INTAKE,
  );
  const [loadError, setLoadError] = useState<string | null>(null);
  const [mutationResult, setMutationResult] =
    useState<BuilderMutationResult | null>(null);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);

  async function load() {
    const [builderPayload, lookupPayload] = await Promise.all([
      fetchWorkflowBuilder(builderUrl),
      fetchWorkflowLookups(lookupsUrl),
    ]);
    const selectedCatalog = catalogWithFallbacks(
      lookupPayload,
      builderPayload.reference_catalog,
    );
    setEnvelope(builderPayload);
    setCatalog(selectedCatalog);
    if (builderPayload.draft) {
      const document = cloneWorkflowDocument(builderPayload.draft.document);
      setEditorDocument(document);
      setFormValues({
        description: builderPayload.draft.description,
        join_policy:
          builderPayload.draft.graph.join_policies[0]?.policy_id ??
          "wait_for_required_branches",
        name: builderPayload.draft.name,
        selected_profile_ref:
          selectedCatalog.profile_options[0]?.reference_id ?? null,
        selected_prompt_ref:
          selectedCatalog.prompt_options[0]?.reference_id ?? null,
      });
      setIntake((current) => ({
        ...current,
        purpose: document.description ?? current.purpose,
        workflowKey: document.workflow_key,
        workflowName: document.display_name,
      }));
      setActiveStep((current) => (current === "scenario" ? "metadata" : current));
    }
    setDirty(false);
    setLoadError(null);
  }

  useEffect(() => {
    let alive = true;
    load().catch((caught: unknown) => {
      if (alive) {
        setLoadError(
          caught instanceof Error ? caught.message : "Workflow onboarding unavailable",
        );
      }
    });
    return () => {
      alive = false;
    };
  }, [builderUrl, lookupsUrl]);

  const validation = envelope?.validation ?? null;
  const publishReadiness = envelope?.publish_readiness ?? null;
  const publishedVersionId =
    envelope?.version_detail?.workflow_version_bundle_id ?? null;
  const setupProgress = useMemo(() => {
    if (!editorDocument || !validation || !publishReadiness) {
      return null;
    }
    return buildWorkflowSetupProgress({
      document: editorDocument,
      publishedVersionId,
      publishReadiness,
      validation,
    });
  }, [editorDocument, publishedVersionId, publishReadiness, validation]);
  const steps = useMemo(
    () => buildOnboardingSteps(activeStep, Boolean(editorDocument), setupProgress?.steps),
    [activeStep, editorDocument, setupProgress?.steps],
  );

  if (loadError && !envelope) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Workflow onboarding unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!envelope || !catalog) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading workflow registry, draft state, and reference readiness.",
          title: "Loading workflow onboarding",
          trace_id: null,
        }}
      />
    );
  }

  async function createDraftFromIntake() {
    const normalized = intakeWithDerivedKey(intake);
    const base = buildBlankWorkflowDocument(normalized);
    const document = buildGenericBlueprintDocument(base, normalized);
    setPendingAction("create");
    try {
      const result = await createWorkflowDraft(
        envelope?.create_state.create_action.href ?? "",
        {
          created_from_version_id: null,
          description: normalized.purpose,
          display_name: normalized.workflowName,
          document,
          idempotency_key: buildIdempotencyKey(
            `workflow-onboarding-create-${normalized.workflowKey}`,
          ),
          scope_type:
            envelope?.scope.scope_type === "platform" ? "platform" : "tenant",
          slug: normalized.workflowKey,
          tenant_id: envelope?.scope.tenant_id ?? null,
          workflow_kind: "main_workflow",
        },
      );
      setMutationResult(result);
      await load();
      setActiveStep("metadata");
    } catch (caught: unknown) {
      setMutationResult({
        audit_reference_id: null,
        confirmation: null,
        editor_state: null,
        field_errors: [],
        idempotency: null,
        next_action: null,
        publish_readiness: null,
        revision: null,
        stale_conflict: null,
        status: "validation_error",
        summary: caught instanceof Error ? caught.message : "Create failed",
        toast: null,
        validation: null,
      });
    } finally {
      setPendingAction(null);
    }
  }

  async function saveDraft(changeSummary = "Workflow onboarding save") {
    if (!envelope?.draft || !formValues || !editorDocument) {
      return;
    }
    const saveHref = draftActionHref(envelope, "workflow-save");
    if (!saveHref) {
      return;
    }
    const documentToSave = applyWorkflowMetadata(editorDocument, formValues);
    setPendingAction("save");
    try {
      const result = await saveWorkflowDraft(saveHref, {
        change_summary: changeSummary,
        client_context: {
          active_section: `onboarding-${activeStep}`,
          form_version: "workflow-onboarding-wizard.v1",
        },
        description: formValues.description,
        document: documentToSave,
        force_stale: false,
        idempotency_key: buildIdempotencyKey(`workflow-onboarding-save-${activeStep}`),
        join_policy: formValues.join_policy,
        name: formValues.name,
        revision: envelope.draft.revision,
        selected_profile_ref: formValues.selected_profile_ref,
        selected_prompt_ref: formValues.selected_prompt_ref,
      });
      setMutationResult(result);
      await load();
    } catch (caught: unknown) {
      setMutationResult(errorResult(caught, "Save failed"));
    } finally {
      setPendingAction(null);
    }
  }

  async function runValidation(readyFixture: boolean) {
    const href = envelope ? draftActionHref(envelope, "workflow-validate") : null;
    if (!href) {
      return;
    }
    setPendingAction("validate");
    try {
      const result = await validateWorkflowDraft(href, readyFixture);
      setMutationResult(result);
      await load();
    } catch (caught: unknown) {
      setMutationResult(errorResult(caught, "Validation failed"));
    } finally {
      setPendingAction(null);
    }
  }

  async function publishDraft(readyFixture: boolean, confirmed: boolean) {
    const href = envelope ? draftActionHref(envelope, "workflow-publish") : null;
    if (!href || !envelope?.draft) {
      return;
    }
    setPendingAction("publish");
    try {
      const result = await publishWorkflowDraft(href, {
        confirmed,
        idempotency_key: buildIdempotencyKey(
          confirmed ? "workflow-onboarding-publish-confirm" : "workflow-onboarding-publish",
        ),
        ready_fixture: readyFixture,
        revision: envelope.draft.revision,
      });
      setMutationResult(result);
      await load();
    } catch (caught: unknown) {
      setMutationResult(errorResult(caught, "Publish failed"));
    } finally {
      setPendingAction(null);
    }
  }

  function updateIntake(next: Partial<WorkflowScenarioIntake>) {
    setIntake((current) => {
      const merged = { ...current, ...next };
      if (next.workflowName && !next.workflowKey) {
        merged.workflowKey = normalizeWorkflowKey(next.workflowName);
      }
      return merged;
    });
  }

  function applyBlueprint() {
    const base = editorDocument ?? buildBlankWorkflowDocument(intake);
    const document = buildGenericBlueprintDocument(base, intake);
    setEditorDocument(document);
    setFormValues((current) =>
      current
        ? {
            ...current,
            description: document.description ?? current.description,
            name: document.display_name,
          }
        : current,
    );
    setDirty(true);
    setActiveStep("agents");
  }

  function attachEvidence() {
    const suiteId = catalog?.test_suite_options[0]?.reference_id;
    if (!editorDocument || !suiteId) {
      return;
    }
    setEditorDocument(attachWorkflowEvidenceRequirement(editorDocument, suiteId));
    setDirty(true);
  }

  function go(offset: -1 | 1) {
    const currentIndex = STEP_ORDER.indexOf(activeStep);
    const nextIndex = Math.min(Math.max(currentIndex + offset, 0), STEP_ORDER.length - 1);
    setActiveStep(STEP_ORDER[nextIndex]);
    setSelectedIndex(0);
  }

  const loadedEnvelope = envelope;
  const loadedCatalog = catalog;
  const tenantQuery = loadedEnvelope.scope.tenant_id
    ? `tenant_id=${encodeURIComponent(loadedEnvelope.scope.tenant_id)}`
    : "";
  const draftHref = loadedEnvelope.draft
    ? queryHref(`/admin/app/workflows/drafts/${loadedEnvelope.draft.workflow_draft_id}`, [
        tenantQuery,
      ])
    : queryHref("/admin/app/workflows", [tenantQuery]);
  const launchWorkflowId = publishedVersionId ?? editorDocument?.workflow_key ?? "";
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
    <div className="workflow-onboarding-page">
      <section className="workflow-onboarding-shell" aria-labelledby="onboarding-title">
        <header className="workflow-onboarding-header">
          <div>
            <p className="eyebrow">{loadedEnvelope.scope.label}</p>
            <h1 id="onboarding-title">Set up workflow</h1>
            <p>
              Guide a generic workflow from scenario intake to validation, publish,
              launch, and evidence without raw JSON editing.
            </p>
          </div>
          <div className="workflow-onboarding-header-actions">
            <Badge tone={dirty ? "warning" : "success"}>
              {dirty ? "Unsaved" : "Saved"}
            </Badge>
            <a className="ui-button secondary" href={draftHref}>
              <ExternalLink aria-hidden="true" size={16} />
              Advanced editor
            </a>
          </div>
        </header>

        <div className="workflow-onboarding-frame">
          <nav aria-label="Workflow onboarding steps" className="workflow-onboarding-rail">
            {steps.map((step) => (
              <button
                className={`workflow-onboarding-step ${step.key === activeStep ? "active" : ""}`}
                key={step.key}
                onClick={() => setActiveStep(step.key)}
                type="button"
              >
                <span>{step.title}</span>
                <Badge tone={toneFor(step.status)}>{step.status}</Badge>
              </button>
            ))}
          </nav>
          <main className="workflow-onboarding-body" id={`wizard-${activeStep}`}>
            {renderStep()}
          </main>
        </div>

        <footer className="workflow-onboarding-footer">
          <Button
            disabled={activeStep === STEP_ORDER[0]}
            onClick={() => go(-1)}
            type="button"
            variant="secondary"
          >
            <ArrowLeft aria-hidden="true" size={16} />
            Back
          </Button>
          <MutationNotice result={mutationResult} />
          <Button
            disabled={activeStep === STEP_ORDER.at(-1)}
            onClick={() => go(1)}
            type="button"
          >
            Next
            <ArrowRight aria-hidden="true" size={16} />
          </Button>
        </footer>
      </section>
    </div>
  );

  function renderStep() {
    if (activeStep === "scenario" || !editorDocument || !loadedEnvelope.draft) {
      return (
        <ScenarioStep
          canCreate={Boolean(loadedEnvelope.create_state.create_action.enabled)}
          creating={pendingAction === "create"}
          intake={intake}
          onCreate={() => void createDraftFromIntake()}
          onIntakeChange={updateIntake}
        />
      );
    }
    if (activeStep === "metadata") {
      return (
        <MetadataStep
          dirty={dirty}
          document={editorDocument}
          formValues={formValues}
          onApplyBlueprint={applyBlueprint}
          onFormChange={(values) => {
            setFormValues(values);
            setEditorDocument(applyWorkflowMetadata(editorDocument, values));
            setDirty(true);
          }}
          onSave={() => void saveDraft()}
          saving={pendingAction === "save"}
        />
      );
    }
    if (activeStep === "agents") {
      return (
        <PagedCollectionStep
          emptyLabel="No roles are configured yet."
          icon={<ListChecks aria-hidden="true" size={18} />}
          items={editorDocument.roles.map((role) => ({
            detail: role.purpose,
            key: role.role_key,
            meta: `${role.responsibilities?.length ?? 0} responsibilities`,
            title: role.display_name,
          }))}
          onPage={setSelectedIndex}
          selectedIndex={selectedIndex}
          title="Agent roles"
        />
      );
    }
    if (activeStep === "contracts") {
      return (
        <PagedCollectionStep
          emptyLabel="No contracts are configured yet."
          icon={<FileText aria-hidden="true" size={18} />}
          items={editorDocument.contracts.map((contract) => ({
            detail: contract.contract_kind ?? "contract",
            key: contract.contract_key,
            meta: contract.semantic_version ?? "1.0.0",
            title: contract.display_name ?? contract.contract_key,
          }))}
          onPage={setSelectedIndex}
          selectedIndex={selectedIndex}
          title="Contracts"
        />
      );
    }
    if (activeStep === "graph") {
      return (
        <GraphStep
          document={editorDocument}
          onSave={() => void saveDraft("Workflow onboarding graph save")}
          saving={pendingAction === "save"}
        />
      );
    }
    if (activeStep === "bindings") {
      return <ResourceStep catalog={loadedCatalog} document={editorDocument} />;
    }
    if (activeStep === "evidence") {
      return (
        <EvidenceStep
          catalog={loadedCatalog}
          document={editorDocument}
          dirty={dirty}
          onAttach={attachEvidence}
          onSave={() => void saveDraft("Workflow onboarding evidence save")}
          saving={pendingAction === "save"}
        />
      );
    }
    if (activeStep === "publish") {
      return (
        <PublishStep
          onPublish={(readyFixture, confirmed) =>
            void publishDraft(readyFixture, confirmed)
          }
          onValidate={(readyFixture) => void runValidation(readyFixture)}
          pendingAction={pendingAction}
          publishReadiness={publishReadiness}
          validation={validation}
        />
      );
    }
    return (
      <LaunchStep
        designReviewHref={designReviewHref}
        publishedVersionId={publishedVersionId}
        runHref={runHref}
      />
    );
  }
}

function ScenarioStep({
  canCreate,
  creating,
  intake,
  onCreate,
  onIntakeChange,
}: {
  canCreate: boolean;
  creating: boolean;
  intake: WorkflowScenarioIntake;
  onCreate: () => void;
  onIntakeChange: (next: Partial<WorkflowScenarioIntake>) => void;
}) {
  return (
    <section aria-labelledby="wizard-scenario-title" className="wizard-step-panel">
      <StepHeading
        icon={<Sparkles aria-hidden="true" size={18} />}
        summary="Capture neutral scenario intent and create a durable editable draft blueprint."
        title="Scenario intake"
      />
      <div className="wizard-form-grid">
        <label>
          Workflow name
          <input
            onChange={(event) => onIntakeChange({ workflowName: event.target.value })}
            value={intake.workflowName}
          />
        </label>
        <label>
          Workflow key
          <input
            onBlur={() =>
              onIntakeChange({ workflowKey: normalizeWorkflowKey(intake.workflowKey) })
            }
            onChange={(event) => onIntakeChange({ workflowKey: event.target.value })}
            value={intake.workflowKey}
          />
        </label>
        <label className="wide">
          Purpose
          <textarea
            onChange={(event) => onIntakeChange({ purpose: event.target.value })}
            rows={2}
            value={intake.purpose}
          />
        </label>
        <label>
          Trigger
          <select
            onChange={(event) =>
              onIntakeChange({
                triggerMode: event.target.value as WorkflowScenarioIntake["triggerMode"],
              })
            }
            value={intake.triggerMode}
          >
            <option value="manual_launch">Manual launch</option>
            <option value="channel_or_api">Channel or API</option>
          </select>
        </label>
        <label>
          Agent count
          <input
            max={5}
            min={1}
            onChange={(event) =>
              onIntakeChange({ agentCount: Number(event.target.value) })
            }
            type="number"
            value={intake.agentCount}
          />
        </label>
        <label>
          Coordination
          <select
            onChange={(event) =>
              onIntakeChange({
                coordinationPattern: event.target
                  .value as WorkflowScenarioIntake["coordinationPattern"],
              })
            }
            value={intake.coordinationPattern}
          >
            <option value="parallel_review">Parallel review</option>
            <option value="sequential_handoff">Sequential handoff</option>
          </select>
        </label>
        <label>
          Evidence
          <select
            onChange={(event) =>
              onIntakeChange({
                evidencePreference: event.target
                  .value as WorkflowScenarioIntake["evidencePreference"],
              })
            }
            value={intake.evidencePreference}
          >
            <option value="deterministic_safe_run">Deterministic safe run</option>
            <option value="manual_before_publish">Manual before publish</option>
          </select>
        </label>
        <label className="wide">
          Expected inputs
          <textarea
            onChange={(event) => onIntakeChange({ expectedInputs: event.target.value })}
            rows={2}
            value={intake.expectedInputs}
          />
        </label>
        <label className="wide">
          Desired outputs
          <textarea
            onChange={(event) => onIntakeChange({ desiredOutputs: event.target.value })}
            rows={2}
            value={intake.desiredOutputs}
          />
        </label>
      </div>
      <div className="wizard-inline-actions">
        <Button disabled={!canCreate || creating} onClick={onCreate} type="button">
          <Sparkles aria-hidden="true" size={16} />
          {creating ? "Creating draft" : "Create durable draft"}
        </Button>
      </div>
    </section>
  );
}

function MetadataStep({
  dirty,
  document,
  formValues,
  onApplyBlueprint,
  onFormChange,
  onSave,
  saving,
}: {
  dirty: boolean;
  document: WorkflowEditorDocument;
  formValues: WorkflowDraftFormValues | null;
  onApplyBlueprint: () => void;
  onFormChange: (values: WorkflowDraftFormValues) => void;
  onSave: () => void;
  saving: boolean;
}) {
  if (!formValues) {
    return null;
  }
  return (
    <section aria-labelledby="wizard-metadata-title" className="wizard-step-panel">
      <StepHeading
        icon={<ShieldCheck aria-hidden="true" size={18} />}
        summary="Keep the backend draft as the durable source of truth."
        title="Draft blueprint"
      />
      <div className="wizard-form-grid">
        <label>
          Name
          <input
            onChange={(event) =>
              onFormChange({ ...formValues, name: event.target.value })
            }
            value={formValues.name}
          />
        </label>
        <label>
          Workflow key
          <input readOnly value={document.workflow_key} />
        </label>
        <label className="wide">
          Description
          <textarea
            onChange={(event) =>
              onFormChange({ ...formValues, description: event.target.value })
            }
            rows={2}
            value={formValues.description}
          />
        </label>
      </div>
      <div className="wizard-inline-actions">
        <Button onClick={onApplyBlueprint} type="button" variant="secondary">
          <Workflow aria-hidden="true" size={16} />
          Refresh blueprint
        </Button>
        <Button disabled={!dirty || saving} onClick={onSave} type="button">
          <Save aria-hidden="true" size={16} />
          {saving ? "Saving" : "Save draft"}
        </Button>
      </div>
    </section>
  );
}

function GraphStep({
  document,
  onSave,
  saving,
}: {
  document: WorkflowEditorDocument;
  onSave: () => void;
  saving: boolean;
}) {
  return (
    <section aria-labelledby="wizard-graph-title" className="wizard-step-panel">
      <StepHeading
        icon={<GitBranch aria-hidden="true" size={18} />}
        summary="Review graph shape without opening raw document JSON."
        title="Graph configuration"
      />
      <div className="wizard-stat-grid">
        <Stat label="Nodes" value={String(document.nodes.length)} />
        <Stat label="Edges" value={String(document.edges.length)} />
        <Stat label="Joins" value={String(document.join_policies.length)} />
        <Stat label="Approvals" value={String(document.approval_gates.length)} />
      </div>
      <div className="wizard-graph-list" aria-label="Configured graph edges">
        {document.edges.slice(0, 6).map((edge) => (
          <span key={edge.edge_key}>
            {edge.source_node_key}
            {" -> "}
            {edge.target_node_key}
          </span>
        ))}
      </div>
      <Button disabled={saving} onClick={onSave} type="button">
        <Save aria-hidden="true" size={16} />
        {saving ? "Saving" : "Save graph"}
      </Button>
    </section>
  );
}

function ResourceStep({
  catalog,
  document,
}: {
  catalog: WorkflowReferenceCatalog;
  document: WorkflowEditorDocument;
}) {
  const readyRefs = document.prompt_profile_references.filter((reference) =>
    ["ready", "active"].includes(reference.readiness_status ?? ""),
  ).length;
  return (
    <section aria-labelledby="wizard-bindings-title" className="wizard-step-panel">
      <StepHeading
        icon={<KeyRound aria-hidden="true" size={18} />}
        summary="Summaries stay safe; detailed prompt/profile editing remains in authorized workspaces."
        title="Resources and readiness"
      />
      <div className="wizard-stat-grid">
        <Stat label="Role bindings" value={`${readyRefs}/${document.prompt_profile_references.length}`} />
        <Stat label="Providers" value={String(catalog.provider_options.length)} />
        <Stat label="Skills" value={String(catalog.skill_options.length)} />
        <Stat label="Suites" value={String(catalog.test_suite_options.length)} />
      </div>
      <div className="wizard-resource-links">
        <a className="action-link" href="/admin/app/governance">
          Prompt and profile workspace
        </a>
        <a className="action-link" href="/admin/app/skills">
          Skill readiness workspace
        </a>
        <a className="action-link" href="/admin/app/channels">
          Channel readiness workspace
        </a>
      </div>
    </section>
  );
}

function EvidenceStep({
  catalog,
  dirty,
  document,
  onAttach,
  onSave,
  saving,
}: {
  catalog: WorkflowReferenceCatalog;
  dirty: boolean;
  document: WorkflowEditorDocument;
  onAttach: () => void;
  onSave: () => void;
  saving: boolean;
}) {
  const suite = catalog.test_suite_options[0];
  return (
    <section aria-labelledby="wizard-evidence-title" className="wizard-step-panel">
      <StepHeading
        icon={<ClipboardCheck aria-hidden="true" size={18} />}
        summary="Required evidence is stored on the workflow draft and refreshed by backend publish gates."
        title="Evidence configuration"
      />
      <div className="wizard-stat-grid">
        <Stat label="Requirements" value={String(document.test_requirements.length)} />
        <Stat label="Available suites" value={String(catalog.test_suite_options.length)} />
        <Stat
          label="Latest status"
          value={document.test_requirements[0]?.latest_result_status ?? "not attached"}
        />
      </div>
      <p className="table-footer">
        {suite
          ? `Attach ${suite.label} as required deterministic evidence.`
          : "No authorized Test Bench suite is available for this scope."}
      </p>
      <div className="wizard-inline-actions">
        <Button disabled={!suite} onClick={onAttach} type="button" variant="secondary">
          <ClipboardCheck aria-hidden="true" size={16} />
          Attach evidence
        </Button>
        <Button disabled={!dirty || saving} onClick={onSave} type="button">
          <Save aria-hidden="true" size={16} />
          {saving ? "Saving" : "Save evidence"}
        </Button>
      </div>
    </section>
  );
}

function PublishStep({
  onPublish,
  onValidate,
  pendingAction,
  publishReadiness,
  validation,
}: {
  onPublish: (readyFixture: boolean, confirmed: boolean) => void;
  onValidate: (readyFixture: boolean) => void;
  pendingAction: string | null;
  publishReadiness: WorkflowBuilderEnvelope["publish_readiness"] | null;
  validation: WorkflowBuilderEnvelope["validation"] | null;
}) {
  return (
    <section aria-labelledby="wizard-publish-title" className="wizard-step-panel">
      <StepHeading
        icon={<CheckCircle2 aria-hidden="true" size={18} />}
        summary="Validation and publish readiness are computed by backend services."
        title="Validate and publish"
      />
      <div className="wizard-stat-grid">
        <Stat label="Validation" value={validation?.status ?? "unavailable"} />
        <Stat label="Publish gate" value={publishReadiness?.decision ?? "unavailable"} />
        <Stat label="Blockers" value={String(publishReadiness?.blockers.length ?? 0)} />
      </div>
      <p className="table-footer">
        {publishReadiness?.summary ?? validation?.summary ?? "Run validation first."}
      </p>
      <div className="wizard-inline-actions">
        <Button
          disabled={pendingAction === "validate"}
          onClick={() => onValidate(true)}
          type="button"
          variant="secondary"
        >
          <CheckCircle2 aria-hidden="true" size={16} />
          {pendingAction === "validate" ? "Validating" : "Run ready validation"}
        </Button>
        <Button
          disabled={pendingAction === "publish"}
          onClick={() => onPublish(true, true)}
          type="button"
        >
          <Rocket aria-hidden="true" size={16} />
          {pendingAction === "publish" ? "Publishing" : "Publish"}
        </Button>
      </div>
    </section>
  );
}

function LaunchStep({
  designReviewHref,
  publishedVersionId,
  runHref,
}: {
  designReviewHref: string;
  publishedVersionId: string | null;
  runHref: string;
}) {
  return (
    <section aria-labelledby="wizard-runtime-title" className="wizard-step-panel">
      <StepHeading
        icon={<Rocket aria-hidden="true" size={18} />}
        summary="Open authorized runtime and evidence surfaces without copying identifiers."
        title="Launch and verify"
      />
      <div className="wizard-launch-grid">
        <a className="ui-button primary" href={runHref}>
          <Rocket aria-hidden="true" size={16} />
          Runtime launch
        </a>
        <a className="ui-button secondary" href={designReviewHref}>
          <Workflow aria-hidden="true" size={16} />
          Review workspace
        </a>
        {publishedVersionId ? (
          <a
            className="ui-button secondary"
            href={`/admin/app/workflows/versions/${encodeURIComponent(publishedVersionId)}`}
          >
            <GitBranch aria-hidden="true" size={16} />
            Published graph
          </a>
        ) : null}
      </div>
      <p className="table-footer">
        {publishedVersionId
          ? "Published workflow bundle is available for runtime selection."
          : "Publish the draft before runtime bundle selection is available."}
      </p>
    </section>
  );
}

function PagedCollectionStep({
  emptyLabel,
  icon,
  items,
  onPage,
  selectedIndex,
  title,
}: {
  emptyLabel: string;
  icon: ReactNode;
  items: Array<{ detail: string; key: string; meta: string; title: string }>;
  onPage: (index: number) => void;
  selectedIndex: number;
  title: string;
}) {
  const item = items[selectedIndex] ?? null;
  return (
    <section className="wizard-step-panel">
      <StepHeading
        icon={icon}
        summary="Use one-item paging so the wizard remains fixed-frame."
        title={title}
      />
      {item ? (
        <article className="wizard-paged-card">
          <div>
            <p className="eyebrow">{item.key}</p>
            <h3>{item.title}</h3>
            <p>{item.detail}</p>
          </div>
          <Badge tone="info">{item.meta}</Badge>
        </article>
      ) : (
        <p className="table-footer">{emptyLabel}</p>
      )}
      <div className="wizard-inline-actions">
        <Button
          disabled={selectedIndex <= 0}
          onClick={() => onPage(selectedIndex - 1)}
          type="button"
          variant="secondary"
        >
          <ArrowLeft aria-hidden="true" size={16} />
          Previous
        </Button>
        <span className="table-footer">
          {items.length ? selectedIndex + 1 : 0}/{items.length}
        </span>
        <Button
          disabled={selectedIndex >= items.length - 1}
          onClick={() => onPage(selectedIndex + 1)}
          type="button"
          variant="secondary"
        >
          Next item
          <ArrowRight aria-hidden="true" size={16} />
        </Button>
      </div>
    </section>
  );
}

function StepHeading({
  icon,
  summary,
  title,
}: {
  icon: ReactNode;
  summary: string;
  title: string;
}) {
  return (
    <div className="section-heading">
      <div>
        <p className="eyebrow">Onboarding wizard</p>
        <h2>{title}</h2>
        <p>{summary}</p>
      </div>
      <span className="home-action-icon">{icon}</span>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MutationNotice({ result }: { result: BuilderMutationResult | null }) {
  if (!result) {
    return <span className="table-footer">No mutation submitted in this step.</span>;
  }
  return (
    <span className={`wizard-mutation ${result.status}`}>
      {result.summary}
    </span>
  );
}

function buildOnboardingSteps(
  activeStep: WorkflowSetupStepKey,
  hasDraft: boolean,
  setupSteps: WorkflowSetupStep[] | undefined,
): WorkflowSetupStep[] {
  const byKey = new Map(setupSteps?.map((step) => [step.key, step]));
  return WORKFLOW_ONBOARDING_STEPS.map((step) => {
    if (step.key === "scenario") {
      return {
        ...step,
        status: hasDraft ? "complete" : activeStep === "scenario" ? "active" : "blocked",
      };
    }
    const derived = byKey.get(step.key);
    return {
      ...step,
      status:
        step.key === activeStep
          ? "active"
          : hasDraft
            ? derived?.status ?? "blocked"
            : "blocked",
      summary: derived?.summary ?? step.summary,
    };
  });
}

function toneFor(status: WorkflowSetupStep["status"]): "success" | "warning" | "info" {
  if (status === "complete") {
    return "success";
  }
  if (status === "active") {
    return "warning";
  }
  return "info";
}

function catalogWithFallbacks(
  lookupCatalog: WorkflowReferenceCatalog,
  selectedDraftCatalog: WorkflowReferenceCatalog,
): WorkflowReferenceCatalog {
  return {
    ...lookupCatalog,
    profile_options:
      lookupCatalog.profile_options.length > 0
        ? lookupCatalog.profile_options
        : selectedDraftCatalog.profile_options,
    prompt_options:
      lookupCatalog.prompt_options.length > 0
        ? lookupCatalog.prompt_options
        : selectedDraftCatalog.prompt_options,
  };
}

function draftActionHref(
  envelope: WorkflowBuilderEnvelope,
  actionId: string,
): string | null {
  return envelope.actions.find((action) => action.action_id === actionId)?.href ?? null;
}

function queryHref(path: string, parts: string[]): string {
  const query = parts.filter(Boolean).join("&");
  return query ? `${path}?${query}` : path;
}

function errorResult(caught: unknown, fallback: string): BuilderMutationResult {
  return {
    audit_reference_id: null,
    confirmation: null,
    editor_state: null,
    field_errors: [],
    idempotency: null,
    next_action: null,
    publish_readiness: null,
    revision: null,
    stale_conflict: null,
    status: "validation_error",
    summary: caught instanceof Error ? caught.message : fallback,
    toast: null,
    validation: null,
  };
}
