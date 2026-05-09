import { CheckCircle2, FileText, Link2, ShieldCheck, UserCog } from "lucide-react";
import { useMemo, useState } from "react";

import type { WorkflowReferenceCatalog } from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import {
  createGeneratedRoleReference,
  bindReferenceToRole,
  buildReferenceFromCatalog,
  bindingStatusForRole,
  safeCatalogLabel,
  summarizeBindingReadiness,
} from "./workflowPromptProfileBinding";
import type {
  WorkflowEditorDocument,
  WorkflowRoleItem,
} from "./workflowDocumentEditor";

interface WorkflowPromptProfileBinderProps {
  catalog: WorkflowReferenceCatalog;
  document: WorkflowEditorDocument;
  onChange: (document: WorkflowEditorDocument) => void;
}

export function WorkflowPromptProfileBinder({
  catalog,
  document,
  onChange,
}: WorkflowPromptProfileBinderProps) {
  const [selectedRoleKey, setSelectedRoleKey] = useState(
    document.roles[0]?.role_key ?? "",
  );
  const [selectedPromptRef, setSelectedPromptRef] = useState(
    catalog.prompt_options[0]?.reference_id ?? "",
  );
  const [selectedProfileRef, setSelectedProfileRef] = useState(
    catalog.profile_options[0]?.reference_id ?? "",
  );
  const [promptDraftTitle, setPromptDraftTitle] = useState("Workflow role prompt");
  const [promptTemplate, setPromptTemplate] = useState(
    "Classify the request using only authorized workflow context.",
  );
  const [profileDraftTitle, setProfileDraftTitle] = useState(
    "Workflow role runtime profile",
  );
  const [routingHint, setRoutingHint] = useState("local-safe-model");
  const readiness = summarizeBindingReadiness(document);
  const selectedRole = useMemo(
    () =>
      document.roles.find((role) => role.role_key === selectedRoleKey) ??
      document.roles[0] ??
      null,
    [document.roles, selectedRoleKey],
  );
  const selectedPrompt = catalog.prompt_options.find(
    (option) => option.reference_id === selectedPromptRef,
  );
  const selectedProfile = catalog.profile_options.find(
    (option) => option.reference_id === selectedProfileRef,
  );

  function bindCatalogPrompt(role: WorkflowRoleItem) {
    if (!selectedPrompt) {
      return;
    }
    onChange(
      bindReferenceToRole({
        document,
        kind: "prompt",
        reference: buildReferenceFromCatalog({
          kind: "prompt",
          option: selectedPrompt,
          role,
        }),
        roleKey: role.role_key,
      }),
    );
  }

  function bindCatalogProfile(role: WorkflowRoleItem) {
    if (!selectedProfile) {
      return;
    }
    onChange(
      bindReferenceToRole({
        document,
        kind: "profile",
        reference: buildReferenceFromCatalog({
          kind: "profile",
          option: selectedProfile,
          role,
        }),
        roleKey: role.role_key,
      }),
    );
  }

  function createPromptReference(role: WorkflowRoleItem) {
    onChange(
      createGeneratedRoleReference({
        document,
        kind: "prompt",
        label: promptDraftTitle,
        role,
      }),
    );
  }

  function createProfileReference(role: WorkflowRoleItem) {
    onChange(
      createGeneratedRoleReference({
        document,
        kind: "profile",
        label: profileDraftTitle,
        role,
      }),
    );
  }

  return (
    <section
      aria-labelledby="workflow-prompt-profile-title"
      className="workflow-editor-panel workflow-binding-panel"
      id="workflow-prompt-profiles"
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">Prompt/Profile Setup</p>
          <h2 id="workflow-prompt-profile-title">Per-Agent Bindings</h2>
          <p className="table-footer">
            Prompt and profile references are saved to workflow roles without
            exposing raw prompt content in summaries.
          </p>
        </div>
        <Badge tone={readiness.readyRoles === readiness.totalRoles ? "success" : "warning"}>
          {readiness.readyRoles}/{readiness.totalRoles} ready
        </Badge>
      </div>

      {document.roles.length === 0 ? (
        <p className="workflow-editor-empty">Add a role before binding prompts.</p>
      ) : (
        <div className="workflow-binding-grid">
          <section aria-labelledby="binding-matrix-title">
            <h3 id="binding-matrix-title" className="workflow-editor-subtitle">
              Binding Matrix
            </h3>
            <div className="workflow-binding-list">
              {document.roles.map((role) => (
                <article className="workflow-binding-row" key={role.role_key}>
                  <div className="card-heading">
                    <strong>{role.display_name}</strong>
                    <Badge tone={badgeTone(bindingStatusForRole(role))}>
                      {bindingStatusForRole(role)}
                    </Badge>
                  </div>
                  <dl className="workflow-binding-facts">
                    <div>
                      <dt>Prompt</dt>
                      <dd>{(role.prompt_reference_keys ?? []).join(", ") || "Missing"}</dd>
                    </div>
                    <div>
                      <dt>Profile</dt>
                      <dd>{role.profile_reference_key || "Missing"}</dd>
                    </div>
                  </dl>
                  <Button
                    onClick={() => setSelectedRoleKey(role.role_key)}
                    type="button"
                    variant={selectedRole?.role_key === role.role_key ? "primary" : "secondary"}
                  >
                    <Link2 aria-hidden="true" size={16} />
                    Configure
                  </Button>
                </article>
              ))}
            </div>
          </section>

          <section aria-labelledby="binding-controls-title">
            <h3 id="binding-controls-title" className="workflow-editor-subtitle">
              Role Binding Controls
            </h3>
            {selectedRole ? (
              <div className="workflow-binding-controls">
                <label className="form-field">
                  <span className="label">Role</span>
                  <select
                    className="ui-input"
                    onChange={(event) => setSelectedRoleKey(event.target.value)}
                    value={selectedRole.role_key}
                  >
                    {document.roles.map((role) => (
                      <option key={role.role_key} value={role.role_key}>
                        {role.display_name}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="workflow-binding-editor">
                  <div className="card-heading">
                    <strong>Prompt</strong>
                    <Badge tone={selectedPrompt ? "success" : "warning"}>
                      {selectedPrompt ? "authorized" : "empty"}
                    </Badge>
                  </div>
                  <label className="form-field">
                    <span className="label">Authorized prompt</span>
                    <select
                      className="ui-input"
                      onChange={(event) => setSelectedPromptRef(event.target.value)}
                      value={selectedPromptRef}
                    >
                      <option value="">No prompt selected</option>
                      {catalog.prompt_options.map((option) => (
                        <option key={option.reference_id} value={option.reference_id}>
                          {safeCatalogLabel(option)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="form-field">
                    <span className="label">Prompt title</span>
                    <input
                      className="ui-input"
                      onChange={(event) => setPromptDraftTitle(event.target.value)}
                      value={promptDraftTitle}
                    />
                  </label>
                  <details className="workflow-authorized-editor">
                    <summary>
                      <FileText aria-hidden="true" size={16} />
                      Authorized prompt editor
                    </summary>
                    <label className="form-field">
                      <span className="label">Template content</span>
                      <textarea
                        className="ui-input workflow-textarea"
                        onChange={(event) => setPromptTemplate(event.target.value)}
                        rows={5}
                        value={promptTemplate}
                      />
                    </label>
                    <p className="table-footer">
                      This content is never copied into role summaries or graph panels.
                    </p>
                  </details>
                  <div className="workflow-item-actions">
                    <Button
                      disabled={!selectedPrompt}
                      onClick={() => bindCatalogPrompt(selectedRole)}
                      type="button"
                      variant="secondary"
                    >
                      <CheckCircle2 aria-hidden="true" size={16} />
                      Bind selected prompt
                    </Button>
                    <Button
                      onClick={() => createPromptReference(selectedRole)}
                      type="button"
                      variant="primary"
                    >
                      <ShieldCheck aria-hidden="true" size={16} />
                      Publish prompt reference
                    </Button>
                  </div>
                </div>

                <div className="workflow-binding-editor">
                  <div className="card-heading">
                    <strong>Runtime Profile</strong>
                    <Badge tone={selectedProfile ? "success" : "warning"}>
                      {selectedProfile ? "authorized" : "empty"}
                    </Badge>
                  </div>
                  <label className="form-field">
                    <span className="label">Authorized profile</span>
                    <select
                      className="ui-input"
                      onChange={(event) => setSelectedProfileRef(event.target.value)}
                      value={selectedProfileRef}
                    >
                      <option value="">No profile selected</option>
                      {catalog.profile_options.map((option) => (
                        <option key={option.reference_id} value={option.reference_id}>
                          {safeCatalogLabel(option)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="form-field">
                    <span className="label">Profile name</span>
                    <input
                      className="ui-input"
                      onChange={(event) => setProfileDraftTitle(event.target.value)}
                      value={profileDraftTitle}
                    />
                  </label>
                  <label className="form-field">
                    <span className="label">Model routing hint</span>
                    <input
                      className="ui-input"
                      onChange={(event) => setRoutingHint(event.target.value)}
                      value={routingHint}
                    />
                  </label>
                  <p className="table-footer">
                    Provider readiness uses safe summaries only; credential values are
                    never rendered.
                  </p>
                  <div className="workflow-item-actions">
                    <Button
                      disabled={!selectedProfile}
                      onClick={() => bindCatalogProfile(selectedRole)}
                      type="button"
                      variant="secondary"
                    >
                      <CheckCircle2 aria-hidden="true" size={16} />
                      Bind selected profile
                    </Button>
                    <Button
                      onClick={() => createProfileReference(selectedRole)}
                      type="button"
                      variant="primary"
                    >
                      <UserCog aria-hidden="true" size={16} />
                      Activate profile reference
                    </Button>
                  </div>
                </div>
              </div>
            ) : null}
          </section>
        </div>
      )}
    </section>
  );
}

function badgeTone(status: string): "success" | "warning" | "critical" | "info" {
  if (status === "ready") {
    return "success";
  }
  if (status === "warning") {
    return "warning";
  }
  if (status === "blocked") {
    return "critical";
  }
  return "info";
}
