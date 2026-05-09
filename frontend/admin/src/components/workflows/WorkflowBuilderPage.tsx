import { useEffect, useState } from "react";

import {
  createWorkflowDraft,
  fetchDraftAgentGraph,
  fetchVersionAgentGraph,
  fetchWorkflowBuilder,
  fetchWorkflowLookups,
  publishWorkflowDraft,
  saveWorkflowDraft,
  validateWorkflowDraft,
} from "../../api/client";
import type {
  AgentCommunicationGraph,
  BuilderMutationResult,
  WorkflowBuilderEnvelope,
  WorkflowPublishReadiness,
  WorkflowReferenceCatalog,
  WorkflowValidationSummary,
} from "../../api/generated/reactAdminApi";
import { buildIdempotencyKey } from "../../utils/adminActionMetadata";
import { CommonState } from "../states/CommonState";
import { AgentGraphPanel } from "./AgentGraphPanel";
import { WorkflowContractEditor } from "./WorkflowContractEditor";
import { WorkflowGraphPanel } from "./WorkflowGraphPanel";
import { WorkflowJoinApprovalEditor } from "./WorkflowJoinApprovalEditor";
import { WorkflowJsonInspector } from "./WorkflowJsonInspector";
import { WorkflowPublishPanel } from "./WorkflowPublishPanel";
import { WorkflowPromptProfileBinder } from "./WorkflowPromptProfileBinder";
import { WorkflowReferencePicker } from "./WorkflowReferencePicker";
import { WorkflowRoleEditor } from "./WorkflowRoleEditor";
import { WorkflowCreatePage } from "./WorkflowCreatePage";
import { WorkflowRegistryPage } from "./WorkflowRegistryPage";
import { WorkflowRevisionPanel } from "./WorkflowRevisionPanel";
import {
  WorkflowSectionForm,
  type WorkflowDraftFormValues,
} from "./WorkflowSectionForm";
import { WorkflowSharingPanel } from "./WorkflowSharingPanel";
import { WorkflowSetupWizardPanel } from "./WorkflowSetupWizardPanel";
import { WorkflowTestEvidencePanel } from "./WorkflowTestEvidencePanel";
import { WorkflowTopologyEditor } from "./WorkflowTopologyEditor";
import { WorkflowValidationPanel } from "./WorkflowValidationPanel";
import {
  applyWorkflowMetadata,
  buildGraphPreviewFromDocument,
  cloneWorkflowDocument,
  type WorkflowEditorDocument,
} from "./workflowDocumentEditor";
import { buildThreeAgentStarterDocument } from "./workflowSetupWizard";

interface WorkflowBuilderPageProps {
  builderUrl: string;
  lookupsUrl: string;
}

export function WorkflowBuilderPage({
  builderUrl,
  lookupsUrl,
}: WorkflowBuilderPageProps) {
  const [dirty, setDirty] = useState(false);
  const [envelope, setEnvelope] = useState<WorkflowBuilderEnvelope | null>(null);
  const [catalog, setCatalog] = useState<WorkflowReferenceCatalog | null>(null);
  const [formValues, setFormValues] = useState<WorkflowDraftFormValues | null>(
    null,
  );
  const [editorDocument, setEditorDocument] =
    useState<WorkflowEditorDocument | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [draftAgentGraph, setDraftAgentGraph] =
    useState<AgentCommunicationGraph | null>(null);
  const [draftAgentGraphError, setDraftAgentGraphError] = useState<string | null>(
    null,
  );
  const [draftAgentGraphLoading, setDraftAgentGraphLoading] = useState(false);
  const [versionAgentGraph, setVersionAgentGraph] =
    useState<AgentCommunicationGraph | null>(null);
  const [versionAgentGraphError, setVersionAgentGraphError] = useState<
    string | null
  >(null);
  const [versionAgentGraphLoading, setVersionAgentGraphLoading] = useState(false);
  const [publishReadiness, setPublishReadiness] =
    useState<WorkflowPublishReadiness | null>(null);
  const [validation, setValidation] = useState<WorkflowValidationSummary | null>(
    null,
  );
  const [saveResult, setSaveResult] = useState<BuilderMutationResult | null>(null);
  const [createResult, setCreateResult] =
    useState<BuilderMutationResult | null>(null);
  const [validationResult, setValidationResult] =
    useState<BuilderMutationResult | null>(null);
  const [publishResult, setPublishResult] =
    useState<BuilderMutationResult | null>(null);
  const [creating, setCreating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    let alive = true;
    Promise.all([fetchWorkflowBuilder(builderUrl), fetchWorkflowLookups(lookupsUrl)])
      .then(([builderPayload, lookupPayload]) => {
        if (!alive) {
          return;
        }
        const selectedCatalog = catalogWithFallbacks(
          lookupPayload,
          builderPayload.reference_catalog,
        );
        setEnvelope(builderPayload);
        setCatalog(selectedCatalog);
        setValidation(builderPayload.validation ?? null);
        setPublishReadiness(builderPayload.publish_readiness ?? null);
        setFormValues(
          builderPayload.draft
            ? {
                description: builderPayload.draft.description,
                join_policy:
                  builderPayload.draft.graph.join_policies[0]?.policy_id ??
                  "wait_for_required_branches",
                name: builderPayload.draft.name,
                selected_profile_ref:
                  selectedCatalog.profile_options[0]?.reference_id ?? null,
                selected_prompt_ref:
                  selectedCatalog.prompt_options[0]?.reference_id ?? null,
              }
            : null,
        );
        setEditorDocument(
          builderPayload.draft
            ? cloneWorkflowDocument(builderPayload.draft.document)
            : null,
        );
        setDirty(false);
        setLoadError(null);
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Workflow builder unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [builderUrl, lookupsUrl]);

  useEffect(() => {
    const workflowDraftId = envelope?.draft?.workflow_draft_id;
    if (!workflowDraftId) {
      setDraftAgentGraph(null);
      setDraftAgentGraphError(null);
      setDraftAgentGraphLoading(false);
      return;
    }
    let alive = true;
    setDraftAgentGraphLoading(true);
    fetchDraftAgentGraph(workflowDraftId)
      .then((payload) => {
        if (!alive) {
          return;
        }
        setDraftAgentGraph(payload);
        setDraftAgentGraphError(null);
      })
      .catch((caught: unknown) => {
        if (alive) {
          setDraftAgentGraph(null);
          setDraftAgentGraphError(
            caught instanceof Error ? caught.message : "Draft graph unavailable",
          );
        }
      })
      .finally(() => {
        if (alive) {
          setDraftAgentGraphLoading(false);
        }
      });
    return () => {
      alive = false;
    };
  }, [envelope?.draft?.workflow_draft_id]);

  const versionGraphId =
    envelope?.version_detail?.workflow_version_bundle_id ??
    workflowVersionIdFromPath();

  useEffect(() => {
    if (!versionGraphId) {
      setVersionAgentGraph(null);
      setVersionAgentGraphError(null);
      setVersionAgentGraphLoading(false);
      return;
    }
    let alive = true;
    setVersionAgentGraphLoading(true);
    fetchVersionAgentGraph(versionGraphId)
      .then((payload) => {
        if (!alive) {
          return;
        }
        setVersionAgentGraph(payload);
        setVersionAgentGraphError(null);
      })
      .catch((caught: unknown) => {
        if (alive) {
          setVersionAgentGraph(null);
          setVersionAgentGraphError(
            caught instanceof Error
              ? caught.message
              : "Published version graph unavailable",
          );
        }
      })
      .finally(() => {
        if (alive) {
          setVersionAgentGraphLoading(false);
        }
      });
    return () => {
      alive = false;
    };
  }, [versionGraphId]);

  function updateValues(values: WorkflowDraftFormValues) {
    setFormValues(values);
    setEditorDocument((current) =>
      current ? applyWorkflowMetadata(current, values) : current,
    );
    setDirty(true);
  }

  function updateEditorDocument(document: WorkflowEditorDocument) {
    setEditorDocument(
      formValues ? applyWorkflowMetadata(document, formValues) : document,
    );
    setDirty(true);
  }

  function revertEditorDocument() {
    if (!envelope?.draft) {
      return;
    }
    setFormValues({
      description: envelope.draft.description,
      join_policy:
        envelope.draft.graph.join_policies[0]?.policy_id ??
        "wait_for_required_branches",
      name: envelope.draft.name,
      selected_profile_ref: catalog?.profile_options[0]?.reference_id ?? null,
      selected_prompt_ref: catalog?.prompt_options[0]?.reference_id ?? null,
    });
    setEditorDocument(cloneWorkflowDocument(envelope.draft.document));
    setSaveResult(null);
    setDirty(false);
  }

  function applyStarterWorkflow() {
    if (!editorDocument) {
      return;
    }
    setEditorDocument(buildThreeAgentStarterDocument(editorDocument));
    setDirty(true);
  }

  function saveActionHref() {
    return envelope?.actions.find((action) => action.action_id === "workflow-save")
      ?.href;
  }

  function validateActionHref() {
    return envelope?.actions.find(
      (action) => action.action_id === "workflow-validate",
    )?.href;
  }

  function publishActionHref() {
    return envelope?.actions.find(
      (action) => action.action_id === "workflow-publish",
    )?.href;
  }

  async function createDraft() {
    if (!envelope?.create_state.create_action.href) {
      return;
    }
    setCreating(true);
    const slug = `admin-live-workflow-${Date.now().toString(36)}`;
    const displayName = "Admin live workflow";
    try {
      const result = await createWorkflowDraft(
        envelope.create_state.create_action.href,
        {
          created_from_version_id: null,
          description: "Created from the admin workflow live-data page.",
          display_name: displayName,
          document: buildCreateDocument(slug, displayName),
          idempotency_key: buildIdempotencyKey("workflow-create"),
          scope_type:
            envelope.scope.scope_type === "platform" ? "platform" : "tenant",
          slug,
          tenant_id: envelope.scope.tenant_id,
          workflow_kind: "main_workflow",
        },
      );
      setCreateResult(result);
      setLoadError(null);
    } catch (caught: unknown) {
      setCreateResult(null);
      setLoadError(caught instanceof Error ? caught.message : "Create failed");
    } finally {
      setCreating(false);
    }
  }

  async function saveDraft(forceStale = false) {
    if (!envelope?.draft || !formValues || !editorDocument || !saveActionHref()) {
      return;
    }
    const documentToSave = buildSaveDocument(editorDocument, formValues);
    setSaving(true);
    try {
      const result = await saveWorkflowDraft(saveActionHref() ?? "", {
        change_summary: forceStale
          ? "Simulated stale workflow document save"
          : "Workflow document save",
        client_context: {
          active_section: "workflow-graph-role-builder",
          form_version: "workflow-graph-role-builder.v1",
        },
        description: formValues.description,
        document: documentToSave,
        force_stale: forceStale,
        idempotency_key: buildIdempotencyKey(
          forceStale ? "workflow-save-stale" : "workflow-save",
        ),
        join_policy: formValues.join_policy,
        name: formValues.name,
        revision: envelope.draft.revision,
        selected_profile_ref: formValues.selected_profile_ref,
        selected_prompt_ref: formValues.selected_prompt_ref,
      });
      setSaveResult(result);
      if (result.validation) {
        setValidation(result.validation);
      }
      if (result.publish_readiness) {
        setPublishReadiness(result.publish_readiness);
      }
      if (result.status === "accepted" || result.status === "idempotent_replay") {
        setDirty(false);
        setEnvelope((current) =>
          current?.draft && result.editor_state
            ? {
                ...current,
                draft: result.editor_state,
                sections:
                  result.editor_state.section_summaries.length > 0
                    ? result.editor_state.section_summaries
                    : current.sections,
              }
            : current?.draft
            ? {
                ...current,
                draft: {
                  ...current.draft,
                  description: formValues.description,
                  document: documentToSave,
                  name: formValues.name,
                  revision: result.revision ?? current.draft.revision,
                },
              }
            : current,
        );
        setEditorDocument(
          result.editor_state
            ? cloneWorkflowDocument(result.editor_state.document)
            : cloneWorkflowDocument(documentToSave),
        );
      }
    } catch (caught: unknown) {
      setSaveResult(null);
      setLoadError(caught instanceof Error ? caught.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function runValidation(ready: boolean) {
    if (!validateActionHref()) {
      return;
    }
    setValidating(true);
    try {
      const result = await validateWorkflowDraft(validateActionHref() ?? "", ready);
      setValidationResult(result);
      if (result.validation) {
        setValidation(result.validation);
      }
      if (result.publish_readiness) {
        setPublishReadiness(result.publish_readiness);
      }
    } catch (caught: unknown) {
      setValidationResult(null);
      setLoadError(caught instanceof Error ? caught.message : "Validation failed");
    } finally {
      setValidating(false);
    }
  }

  async function publishDraft(readyFixture: boolean, confirmed: boolean) {
    if (!envelope?.draft || !publishActionHref()) {
      return;
    }
    setPublishing(true);
    try {
      const result = await publishWorkflowDraft(publishActionHref() ?? "", {
        confirmed,
        idempotency_key: buildIdempotencyKey(
          confirmed ? "workflow-publish-confirm" : "workflow-publish",
        ),
        ready_fixture: readyFixture,
        revision: envelope.draft.revision,
      });
      setPublishResult(result);
      if (result.publish_readiness) {
        setPublishReadiness(result.publish_readiness);
      }
      if (result.status === "accepted") {
        const refreshed = await fetchWorkflowBuilder(builderUrl);
        setEnvelope(refreshed);
        setValidation(refreshed.validation ?? validation);
        setPublishReadiness(refreshed.publish_readiness ?? publishReadiness);
        if (refreshed.draft) {
          setFormValues({
            description: refreshed.draft.description,
            join_policy:
              refreshed.draft.graph.join_policies[0]?.policy_id ??
              "wait_for_required_branches",
            name: refreshed.draft.name,
            selected_profile_ref: catalog?.profile_options[0]?.reference_id ?? null,
            selected_prompt_ref: catalog?.prompt_options[0]?.reference_id ?? null,
          });
          setEditorDocument(cloneWorkflowDocument(refreshed.draft.document));
        }
      }
    } catch (caught: unknown) {
      setPublishResult(null);
      setLoadError(caught instanceof Error ? caught.message : "Publish failed");
    } finally {
      setPublishing(false);
    }
  }

  if (loadError && !envelope) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Workflow builder unavailable",
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
          summary: "Loading draft, references, graph, and publish gates.",
          title: "Loading workflow builder",
          trace_id: null,
        }}
      />
    );
  }

  if (!envelope.draft) {
    return (
      <div className="workflow-builder-page">
        <section className="patterns-hero workflow-hero">
          <p className="eyebrow">Workflows</p>
          <h2>{envelope.title}</h2>
          <p>{envelope.description}</p>
        </section>
        {loadError ? <p className="safe-error">{loadError}</p> : null}
        <WorkflowRegistryPage registry={envelope.registry} />
        <WorkflowCreatePage
          createState={envelope.create_state}
          creating={creating}
          mutationResult={createResult}
          onCreate={() => void createDraft()}
        />
        <CommonState
          state={
            envelope.state ?? {
              action: null,
              empty_state: envelope.empty_state ?? null,
              provenance: envelope.provenance ?? null,
              state: "empty",
              summary: "No workflow draft is available for this scope.",
              title: "No active workflow draft",
              trace_id: null,
            }
          }
        />
      </div>
    );
  }

  if (!formValues || !editorDocument || !validation || !publishReadiness) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading draft, references, graph, and publish gates.",
          title: "Loading workflow builder",
          trace_id: null,
        }}
      />
    );
  }

  const editableGraph = buildGraphPreviewFromDocument(
    editorDocument,
    envelope.draft.graph,
  );

  return (
    <div className="workflow-builder-page">
      <section className="patterns-hero workflow-hero">
        <p className="eyebrow">Workflows</p>
        <h2>{envelope.title}</h2>
        <p>{envelope.description}</p>
      </section>
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <WorkflowRegistryPage registry={envelope.registry} />
      <WorkflowCreatePage
        createState={envelope.create_state}
        creating={creating}
        mutationResult={createResult}
        onCreate={() => void createDraft()}
      />
      <WorkflowSetupWizardPanel
        document={editorDocument}
        onApplyStarter={applyStarterWorkflow}
        publishedVersionId={versionGraphId}
        publishReadiness={publishReadiness}
        tenantId={envelope.scope.tenant_id}
        validation={validation}
      />
      <WorkflowSectionForm
        dirty={dirty}
        draft={envelope.draft}
        error={null}
        joinPolicies={envelope.draft.graph.join_policies}
        mutationResult={saveResult}
        onChange={updateValues}
        onForceStale={() => void saveDraft(true)}
        onRevert={revertEditorDocument}
        onSave={() => void saveDraft(false)}
        saving={saving}
        sections={envelope.sections}
        values={formValues}
      />
      <WorkflowReferencePicker
        catalog={catalog}
        onProfileChange={(referenceId) =>
          updateValues({ ...formValues, selected_profile_ref: referenceId })
        }
        onPromptChange={(referenceId) =>
          updateValues({ ...formValues, selected_prompt_ref: referenceId })
        }
        selectedProfileRef={formValues.selected_profile_ref}
        selectedPromptRef={formValues.selected_prompt_ref}
      />
      <WorkflowRoleEditor
        catalog={catalog}
        document={editorDocument}
        onChange={updateEditorDocument}
      />
      <WorkflowPromptProfileBinder
        catalog={catalog}
        document={editorDocument}
        onChange={updateEditorDocument}
      />
      <WorkflowTestEvidencePanel
        catalog={catalog}
        document={editorDocument}
        draftRevision={envelope.draft.workflow_draft_revision_id}
        onChange={updateEditorDocument}
        publishReadiness={publishReadiness}
        tenantId={envelope.scope.tenant_id}
        workflowDraftId={envelope.draft.workflow_draft_id}
      />
      <WorkflowContractEditor
        document={editorDocument}
        onChange={updateEditorDocument}
      />
      <WorkflowTopologyEditor
        document={editorDocument}
        onChange={updateEditorDocument}
      />
      <WorkflowJoinApprovalEditor
        catalog={catalog}
        document={editorDocument}
        onChange={updateEditorDocument}
      />
      <WorkflowGraphPanel graph={editableGraph} />
      <AgentGraphPanel
        error={draftAgentGraphError}
        graph={draftAgentGraph}
        loading={draftAgentGraphLoading}
        sourceLabel="Draft"
      />
      <WorkflowValidationPanel
        lastResult={validationResult}
        onValidate={(ready) => void runValidation(ready)}
        validating={validating}
        validation={validation}
      />
      <WorkflowPublishPanel
        lastResult={publishResult}
        onPublish={(readyFixture, confirmed) =>
          void publishDraft(readyFixture, confirmed)
        }
        publishing={publishing}
        readiness={publishReadiness}
      />
      <WorkflowSharingPanel sharing={envelope.sharing} />
      <div className="workflow-review-grid">
        <WorkflowRevisionPanel revisions={envelope.revisions} />
        {envelope.json_inspector ? (
          <WorkflowJsonInspector inspector={envelope.json_inspector} />
        ) : null}
      </div>
      {envelope.version_detail ? (
        <section className="workflow-version-panel" aria-labelledby="version-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Published version</p>
              <h2 id="version-title">{envelope.version_detail.display_name}</h2>
            </div>
          </div>
          <p>{envelope.version_detail.summary}</p>
          <small>
            {envelope.version_detail.display_version} /{" "}
            {envelope.version_detail.digest_label}
          </small>
        </section>
      ) : null}
      {versionGraphId ? (
        <AgentGraphPanel
          error={versionAgentGraphError}
          graph={versionAgentGraph}
          loading={versionAgentGraphLoading}
          sourceLabel="Published version"
        />
      ) : null}
    </div>
  );
}

function workflowVersionIdFromPath(): string | null {
  const match = window.location.pathname.match(
    /^\/admin\/app\/workflows\/versions\/([^/]+)/,
  );
  return match?.[1] ?? null;
}

function buildCreateDocument(slug: string, displayName: string) {
  return {
    approval_gates: [],
    contracts: [
      {
        contract_key: "request",
        json_schema: { type: "object" },
      },
      {
        contract_key: "result",
        json_schema: { type: "object" },
      },
    ],
    description: "Durable workflow draft created from the admin live-data UI.",
    display_name: displayName,
    edges: [],
    entry_node_key: "start",
    join_policies: [],
    nodes: [
      {
        display_name: "Start",
        node_key: "start",
        node_type: "role",
        role_key: "coordinator",
      },
    ],
    roles: [
      {
        display_name: "Coordinator",
        input_contract_key: "request",
        output_contract_key: "result",
        purpose: "Coordinate the workflow created from the admin UI.",
        role_key: "coordinator",
        skill_bindings: [
          {
            binding_key: "coordinator-review",
            purpose: "Review workflow input.",
            skill_slug: "coordinator-review",
            skill_version: "2026.05.0",
          },
        ],
      },
    ],
    subworkflow_refs: [],
    test_requirements: [],
    workflow_key: slug,
    workflow_kind: "main_workflow",
  };
}

function buildSaveDocument(
  document: WorkflowEditorDocument,
  values: WorkflowDraftFormValues,
): Record<string, unknown> {
  return applyWorkflowMetadata(document, values);
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
