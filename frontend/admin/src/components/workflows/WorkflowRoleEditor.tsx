import { Plus } from "lucide-react";

import type { WorkflowReferenceCatalog } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";
import {
  AddButton,
  DependencyWarnings,
  EditorField,
  EditorGrid,
  EditorItem,
  EditorPanel,
  EditorToolbar,
  EmptyEditorState,
  ItemActionRow,
} from "./WorkflowEditorControls";
import {
  csvToStringList,
  duplicateRole,
  makeUniqueKey,
  moveCollectionItem,
  removeCollectionItem,
  replaceCollectionItem,
  roleDependencyWarnings,
  roleKeys,
  ROLE_KIND_OPTIONS,
  stringListToCsv,
  stringListToLines,
  linesToStringList,
  type WorkflowEditorDocument,
  type WorkflowRoleItem,
} from "./workflowDocumentEditor";

interface WorkflowRoleEditorProps {
  catalog: WorkflowReferenceCatalog;
  document: WorkflowEditorDocument;
  onChange: (document: WorkflowEditorDocument) => void;
}

export function WorkflowRoleEditor({
  catalog,
  document,
  onChange,
}: WorkflowRoleEditorProps) {
  function updateRole(index: number, role: WorkflowRoleItem) {
    onChange({
      ...document,
      roles: replaceCollectionItem(document.roles, index, role),
    });
  }

  function addRole() {
    const roleKey = makeUniqueKey("agent", roleKeys(document));
    onChange({
      ...document,
      roles: [
        ...document.roles,
        {
          display_name: "New agent",
          graph_node_keys: [],
          input_contract_key: document.contracts[0]?.contract_key ?? null,
          output_contract_key: document.contracts.at(-1)?.contract_key ?? null,
          prompt_reference_keys: [],
          purpose: "",
          responsibilities: [],
          role_key: roleKey,
          role_kind: "agent",
          skill_installation_keys: [],
        },
      ],
    });
  }

  return (
    <EditorPanel
      badge={<Badge tone={document.roles.length > 0 ? "success" : "warning"}>{document.roles.length} roles</Badge>}
      id="workflow-roles"
      summary="Agent and sub-agent definitions persist through the workflow document save."
      title="Roles"
    >
      <EditorToolbar>
        <AddButton onClick={addRole}>
          <Plus aria-hidden="true" size={16} />
          Add role
        </AddButton>
      </EditorToolbar>
      {document.roles.length === 0 ? (
        <EmptyEditorState>No roles are defined for this draft.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.roles.map((role, index) => (
            <EditorItem
              badge={<Badge tone={role.role_kind === "subagent" ? "info" : "success"}>{role.role_kind ?? "agent"}</Badge>}
              key={`${role.role_key}-${index}`}
              title={role.display_name || role.role_key}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        role_key: event.target.value,
                      })
                    }
                    value={role.role_key}
                  />
                </EditorField>
                <EditorField label="Name">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        display_name: event.target.value,
                      })
                    }
                    value={role.display_name}
                  />
                </EditorField>
                <EditorField label="Kind">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        role_kind: event.target.value,
                      })
                    }
                    value={role.role_kind ?? "agent"}
                  >
                    {ROLE_KIND_OPTIONS.map((kind) => (
                      <option key={kind} value={kind}>
                        {kind}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Input contract">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        input_contract_key: event.target.value || null,
                      })
                    }
                    value={role.input_contract_key ?? ""}
                  >
                    <option value="">None</option>
                    {document.contracts.map((contract) => (
                      <option key={contract.contract_key} value={contract.contract_key}>
                        {contract.display_name ?? contract.contract_key}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Output contract">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        output_contract_key: event.target.value || null,
                      })
                    }
                    value={role.output_contract_key ?? ""}
                  >
                    <option value="">None</option>
                    {document.contracts.map((contract) => (
                      <option key={contract.contract_key} value={contract.contract_key}>
                        {contract.display_name ?? contract.contract_key}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Profile reference">
                  <>
                    <input
                      className="ui-input"
                      list="workflow-profile-options"
                      onChange={(event) =>
                        updateRole(index, {
                          ...role,
                          profile_reference_key: event.target.value || null,
                        })
                      }
                      value={role.profile_reference_key ?? ""}
                    />
                    <a className="inline-link" href="#workflow-prompt-profiles">
                      Use binding matrix
                    </a>
                  </>
                </EditorField>
                <EditorField label="Prompt refs">
                  <>
                    <input
                      className="ui-input"
                      list="workflow-prompt-options"
                      onChange={(event) =>
                        updateRole(index, {
                          ...role,
                          prompt_reference_keys: csvToStringList(event.target.value),
                        })
                      }
                      value={stringListToCsv(role.prompt_reference_keys)}
                    />
                    <a className="inline-link" href="#workflow-prompt-profiles">
                      Use binding matrix
                    </a>
                  </>
                </EditorField>
                <EditorField label="Skill refs">
                  <input
                    className="ui-input"
                    list="workflow-skill-options"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        skill_installation_keys: csvToStringList(event.target.value),
                      })
                    }
                    value={stringListToCsv(role.skill_installation_keys)}
                  />
                </EditorField>
                <EditorField label="Purpose">
                  <textarea
                    className="ui-input workflow-textarea compact"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        purpose: event.target.value,
                      })
                    }
                    rows={3}
                    value={role.purpose}
                  />
                </EditorField>
                <EditorField label="Responsibilities">
                  <textarea
                    className="ui-input workflow-textarea compact"
                    onChange={(event) =>
                      updateRole(index, {
                        ...role,
                        responsibilities: linesToStringList(event.target.value),
                      })
                    }
                    rows={3}
                    value={stringListToLines(role.responsibilities)}
                  />
                </EditorField>
              </div>
              <DependencyWarnings
                warnings={roleDependencyWarnings(document, role.role_key)}
              />
              <ItemActionRow
                canMoveDown={index < document.roles.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() =>
                  onChange({
                    ...document,
                    roles: [...document.roles, duplicateRole(document, role)],
                  })
                }
                onMoveDown={() =>
                  onChange({
                    ...document,
                    roles: moveCollectionItem(document.roles, index, 1),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    roles: moveCollectionItem(document.roles, index, -1),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    roles: removeCollectionItem(document.roles, index),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}
      <datalist id="workflow-profile-options">
        {catalog.profile_options.map((option) => (
          <option key={option.reference_id} value={option.reference_id}>
            {option.label}
          </option>
        ))}
      </datalist>
      <datalist id="workflow-prompt-options">
        {catalog.prompt_options.map((option) => (
          <option key={option.reference_id} value={option.reference_id}>
            {option.label}
          </option>
        ))}
      </datalist>
      <datalist id="workflow-skill-options">
        {catalog.skill_options.map((option) => (
          <option key={option.reference_id} value={option.reference_id}>
            {option.label}
          </option>
        ))}
      </datalist>
    </EditorPanel>
  );
}
