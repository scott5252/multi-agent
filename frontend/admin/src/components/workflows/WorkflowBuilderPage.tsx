import { useEffect, useState } from "react";

import {
  fetchWorkflowBuilder,
  fetchWorkflowLookups,
  publishWorkflowDraft,
  saveWorkflowDraft,
  validateWorkflowDraft,
} from "../../api/client";
import type {
  BuilderMutationResult,
  WorkflowBuilderEnvelope,
  WorkflowPublishReadiness,
  WorkflowReferenceCatalog,
  WorkflowValidationSummary,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { WorkflowGraphPanel } from "./WorkflowGraphPanel";
import { WorkflowJsonInspector } from "./WorkflowJsonInspector";
import { WorkflowPublishPanel } from "./WorkflowPublishPanel";
import { WorkflowReferencePicker } from "./WorkflowReferencePicker";
import { WorkflowRevisionPanel } from "./WorkflowRevisionPanel";
import {
  WorkflowSectionForm,
  type WorkflowDraftFormValues,
} from "./WorkflowSectionForm";
import { WorkflowValidationPanel } from "./WorkflowValidationPanel";

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
  const [loadError, setLoadError] = useState<string | null>(null);
  const [publishReadiness, setPublishReadiness] =
    useState<WorkflowPublishReadiness | null>(null);
  const [validation, setValidation] = useState<WorkflowValidationSummary | null>(
    null,
  );
  const [saveResult, setSaveResult] = useState<BuilderMutationResult | null>(null);
  const [validationResult, setValidationResult] =
    useState<BuilderMutationResult | null>(null);
  const [publishResult, setPublishResult] =
    useState<BuilderMutationResult | null>(null);
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
        setEnvelope(builderPayload);
        setCatalog(lookupPayload);
        setValidation(builderPayload.validation);
        setPublishReadiness(builderPayload.publish_readiness);
        setFormValues({
          description: builderPayload.draft.description,
          join_policy:
            builderPayload.draft.graph.join_policies[0]?.policy_id ??
            "wait_for_required_branches",
          name: builderPayload.draft.name,
          selected_profile_ref:
            lookupPayload.profile_options[0]?.reference_id ?? null,
          selected_prompt_ref: lookupPayload.prompt_options[0]?.reference_id ?? null,
        });
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

  function updateValues(values: WorkflowDraftFormValues) {
    setFormValues(values);
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

  async function saveDraft(forceStale = false) {
    if (!envelope || !formValues || !saveActionHref()) {
      return;
    }
    setSaving(true);
    try {
      const result = await saveWorkflowDraft(saveActionHref() ?? "", {
        description: formValues.description,
        force_stale: forceStale,
        idempotency_key: forceStale
          ? "workflow-save-stale-ui-qa030"
          : "workflow-save-ui-qa030",
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
      if (result.status === "accepted") {
        setDirty(false);
        setEnvelope((current) =>
          current
            ? {
                ...current,
                draft: {
                  ...current.draft,
                  description: formValues.description,
                  name: formValues.name,
                  revision: result.revision ?? current.draft.revision,
                },
              }
            : current,
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
    if (!envelope || !publishActionHref()) {
      return;
    }
    setPublishing(true);
    try {
      const result = await publishWorkflowDraft(publishActionHref() ?? "", {
        confirmed,
        idempotency_key: confirmed
          ? "workflow-publish-confirm-ui-qa030"
          : "workflow-publish-ui-qa030",
        ready_fixture: readyFixture,
        revision: envelope.draft.revision,
      });
      setPublishResult(result);
      if (result.publish_readiness) {
        setPublishReadiness(result.publish_readiness);
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

  if (!envelope || !catalog || !formValues || !validation || !publishReadiness) {
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

  return (
    <div className="workflow-builder-page">
      <section className="patterns-hero workflow-hero">
        <p className="eyebrow">Workflows</p>
        <h2>{envelope.title}</h2>
        <p>{envelope.description}</p>
      </section>
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <WorkflowSectionForm
        dirty={dirty}
        draft={envelope.draft}
        error={null}
        joinPolicies={envelope.draft.graph.join_policies}
        mutationResult={saveResult}
        onChange={updateValues}
        onForceStale={() => void saveDraft(true)}
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
      <WorkflowGraphPanel graph={envelope.draft.graph} />
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
      <div className="workflow-review-grid">
        <WorkflowRevisionPanel revisions={envelope.revisions} />
        <WorkflowJsonInspector inspector={envelope.json_inspector} />
      </div>
    </div>
  );
}
