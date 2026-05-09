import { GitMerge, Plus } from "lucide-react";

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
  APPROVER_SCOPE_OPTIONS,
  approvalDependencyWarnings,
  approvalKeys,
  contractKeys,
  csvToStringList,
  JOIN_STRATEGY_OPTIONS,
  joinDependencyWarnings,
  joinKeys,
  makeUniqueKey,
  moveCollectionItem,
  removeCollectionItem,
  replaceCollectionItem,
  stringListToCsv,
  subworkflowAliases,
  subworkflowDependencyWarnings,
  type WorkflowApprovalGateItem,
  type WorkflowEditorDocument,
  type WorkflowJoinPolicyItem,
  type WorkflowSubworkflowReferenceItem,
} from "./workflowDocumentEditor";

interface WorkflowJoinApprovalEditorProps {
  catalog: WorkflowReferenceCatalog;
  document: WorkflowEditorDocument;
  onChange: (document: WorkflowEditorDocument) => void;
}

export function WorkflowJoinApprovalEditor({
  catalog,
  document,
  onChange,
}: WorkflowJoinApprovalEditorProps) {
  function updateJoin(index: number, policy: WorkflowJoinPolicyItem) {
    onChange({
      ...document,
      join_policies: replaceCollectionItem(document.join_policies, index, policy),
    });
  }

  function updateApproval(index: number, gate: WorkflowApprovalGateItem) {
    onChange({
      ...document,
      approval_gates: replaceCollectionItem(document.approval_gates, index, gate),
    });
  }

  function updateSubworkflow(
    index: number,
    reference: WorkflowSubworkflowReferenceItem,
  ) {
    onChange({
      ...document,
      subworkflow_refs: replaceCollectionItem(
        document.subworkflow_refs,
        index,
        reference,
      ),
    });
  }

  function addJoin() {
    const joinKey = makeUniqueKey("join", joinKeys(document));
    onChange({
      ...document,
      join_policies: [
        ...document.join_policies,
        {
          failure_behavior: "block",
          inbound_edge_keys: [],
          join_policy_key: joinKey,
          output_merge_contract_key: null,
          quorum_count: null,
          required_branches: [],
          strategy: "all_success",
          timeout_seconds: null,
        },
      ],
    });
  }

  function addApproval() {
    const approvalKey = makeUniqueKey("approval", approvalKeys(document));
    onChange({
      ...document,
      approval_gates: [
        ...document.approval_gates,
        {
          approval_gate_key: approvalKey,
          approver_scope: "tenant_admin",
          decision_contract_key: null,
          display_name: "New approval",
          instructions: "",
          resume_behavior: "continue",
        },
      ],
    });
  }

  function addSubworkflow() {
    const alias = makeUniqueKey("subworkflow", subworkflowAliases(document));
    onChange({
      ...document,
      subworkflow_refs: [
        ...document.subworkflow_refs,
        {
          alias,
          compatibility_status: "unknown",
          display_name: "New subworkflow",
          input_contract_key: null,
          output_contract_key: null,
          workflow_version_ref:
            catalog.subworkflow_options[0]?.reference_id ?? "select-version",
        },
      ],
    });
  }

  return (
    <EditorPanel
      badge={<Badge tone="info">{document.join_policies.length} joins / {document.approval_gates.length} approvals</Badge>}
      id="workflow-joins"
      summary="Coordination rules, approvals, and subworkflow references remain durable document entries."
      title="Joins, Approvals, And Subworkflows"
    >
      <EditorToolbar>
        <AddButton onClick={addJoin}>
          <GitMerge aria-hidden="true" size={16} />
          Add join
        </AddButton>
        <AddButton onClick={addApproval}>
          <Plus aria-hidden="true" size={16} />
          Add approval
        </AddButton>
        <AddButton onClick={addSubworkflow}>
          <Plus aria-hidden="true" size={16} />
          Add subworkflow
        </AddButton>
      </EditorToolbar>

      <h3 className="workflow-editor-subtitle">Join Policies</h3>
      {document.join_policies.length === 0 ? (
        <EmptyEditorState>No join policies are defined.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.join_policies.map((policy, index) => (
            <EditorItem
              badge={<Badge tone={policy.strategy === "quorum" ? "warning" : "info"}>{policy.strategy}</Badge>}
              key={`${policy.join_policy_key}-${index}`}
              title={policy.join_policy_key}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        join_policy_key: event.target.value,
                      })
                    }
                    value={policy.join_policy_key}
                  />
                </EditorField>
                <EditorField label="Strategy">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        strategy: event.target.value,
                      })
                    }
                    value={policy.strategy}
                  >
                    {JOIN_STRATEGY_OPTIONS.map((strategy) => (
                      <option key={strategy} value={strategy}>
                        {strategy}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Inbound edges">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        inbound_edge_keys: csvToStringList(event.target.value),
                      })
                    }
                    value={stringListToCsv(policy.inbound_edge_keys)}
                  />
                </EditorField>
                <EditorField label="Required branches">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        required_branches: csvToStringList(event.target.value),
                      })
                    }
                    value={stringListToCsv(policy.required_branches)}
                  />
                </EditorField>
                <EditorField label="Quorum">
                  <input
                    className="ui-input"
                    min={0}
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        quorum_count: event.target.value
                          ? Number(event.target.value)
                          : null,
                      })
                    }
                    type="number"
                    value={policy.quorum_count ?? ""}
                  />
                </EditorField>
                <EditorField label="Timeout seconds">
                  <input
                    className="ui-input"
                    min={0}
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        timeout_seconds: event.target.value
                          ? Number(event.target.value)
                          : null,
                      })
                    }
                    type="number"
                    value={policy.timeout_seconds ?? ""}
                  />
                </EditorField>
                <EditorField label="Failure behavior">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        failure_behavior: event.target.value,
                      })
                    }
                    value={policy.failure_behavior ?? "block"}
                  >
                    <option value="block">block</option>
                    <option value="manual_resolution">manual_resolution</option>
                    <option value="fail_workflow">fail_workflow</option>
                    <option value="continue_partial">continue_partial</option>
                  </select>
                </EditorField>
                <EditorField label="Output contract">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateJoin(index, {
                        ...policy,
                        output_merge_contract_key: event.target.value || null,
                      })
                    }
                    value={policy.output_merge_contract_key ?? ""}
                  >
                    <option value="">None</option>
                    {contractKeys(document).map((contractKey) => (
                      <option key={contractKey} value={contractKey}>
                        {contractKey}
                      </option>
                    ))}
                  </select>
                </EditorField>
              </div>
              <DependencyWarnings
                warnings={joinDependencyWarnings(document, policy.join_policy_key)}
              />
              <ItemActionRow
                canMoveDown={index < document.join_policies.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() => {
                  const joinKey = makeUniqueKey(
                    `${policy.join_policy_key}-copy`,
                    joinKeys(document),
                  );
                  onChange({
                    ...document,
                    join_policies: [
                      ...document.join_policies,
                      { ...policy, join_policy_key: joinKey },
                    ],
                  });
                }}
                onMoveDown={() =>
                  onChange({
                    ...document,
                    join_policies: moveCollectionItem(
                      document.join_policies,
                      index,
                      1,
                    ),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    join_policies: moveCollectionItem(
                      document.join_policies,
                      index,
                      -1,
                    ),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    join_policies: removeCollectionItem(
                      document.join_policies,
                      index,
                    ),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}

      <h3 className="workflow-editor-subtitle" id="workflow-approvals">
        Approval Gates
      </h3>
      {document.approval_gates.length === 0 ? (
        <EmptyEditorState>No approval gates are defined.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.approval_gates.map((gate, index) => (
            <EditorItem
              badge={<Badge tone="warning">{gate.approver_scope}</Badge>}
              key={`${gate.approval_gate_key}-${index}`}
              title={gate.display_name}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        approval_gate_key: event.target.value,
                      })
                    }
                    value={gate.approval_gate_key}
                  />
                </EditorField>
                <EditorField label="Name">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        display_name: event.target.value,
                      })
                    }
                    value={gate.display_name}
                  />
                </EditorField>
                <EditorField label="Approver scope">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        approver_scope: event.target.value,
                      })
                    }
                    value={gate.approver_scope}
                  >
                    {APPROVER_SCOPE_OPTIONS.map((scope) => (
                      <option key={scope} value={scope}>
                        {scope}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Role code">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        approver_role_code: event.target.value || null,
                      })
                    }
                    value={gate.approver_role_code ?? ""}
                  />
                </EditorField>
                <EditorField label="Decision contract">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        decision_contract_key: event.target.value || null,
                      })
                    }
                    value={gate.decision_contract_key ?? ""}
                  >
                    <option value="">None</option>
                    {contractKeys(document).map((contractKey) => (
                      <option key={contractKey} value={contractKey}>
                        {contractKey}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Resume behavior">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        resume_behavior: event.target.value || null,
                      })
                    }
                    value={gate.resume_behavior ?? ""}
                  >
                    <option value="">None</option>
                    <option value="continue">continue</option>
                    <option value="branch">branch</option>
                    <option value="halt">halt</option>
                  </select>
                </EditorField>
                <EditorField label="Instructions">
                  <textarea
                    className="ui-input workflow-textarea compact"
                    onChange={(event) =>
                      updateApproval(index, {
                        ...gate,
                        instructions: event.target.value || null,
                      })
                    }
                    rows={3}
                    value={gate.instructions ?? ""}
                  />
                </EditorField>
              </div>
              <DependencyWarnings
                warnings={approvalDependencyWarnings(
                  document,
                  gate.approval_gate_key,
                )}
              />
              <ItemActionRow
                canMoveDown={index < document.approval_gates.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() => {
                  const approvalKey = makeUniqueKey(
                    `${gate.approval_gate_key}-copy`,
                    approvalKeys(document),
                  );
                  onChange({
                    ...document,
                    approval_gates: [
                      ...document.approval_gates,
                      {
                        ...gate,
                        approval_gate_key: approvalKey,
                        display_name: `${gate.display_name} copy`,
                      },
                    ],
                  });
                }}
                onMoveDown={() =>
                  onChange({
                    ...document,
                    approval_gates: moveCollectionItem(
                      document.approval_gates,
                      index,
                      1,
                    ),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    approval_gates: moveCollectionItem(
                      document.approval_gates,
                      index,
                      -1,
                    ),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    approval_gates: removeCollectionItem(
                      document.approval_gates,
                      index,
                    ),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}

      <h3 className="workflow-editor-subtitle" id="workflow-subworkflows">
        Subworkflow References
      </h3>
      {document.subworkflow_refs.length === 0 ? (
        <EmptyEditorState>No subworkflow references are defined.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.subworkflow_refs.map((reference, index) => (
            <EditorItem
              badge={<Badge tone="info">{reference.compatibility_status ?? "unknown"}</Badge>}
              key={`${reference.alias}-${index}`}
              title={reference.display_name ?? reference.alias}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Alias">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateSubworkflow(index, {
                        ...reference,
                        alias: event.target.value,
                      })
                    }
                    value={reference.alias}
                  />
                </EditorField>
                <EditorField label="Name">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateSubworkflow(index, {
                        ...reference,
                        display_name: event.target.value || null,
                      })
                    }
                    value={reference.display_name ?? ""}
                  />
                </EditorField>
                <EditorField label="Version reference">
                  <input
                    className="ui-input"
                    list="workflow-subworkflow-options"
                    onChange={(event) =>
                      updateSubworkflow(index, {
                        ...reference,
                        workflow_version_ref: event.target.value,
                      })
                    }
                    value={reference.workflow_version_ref}
                  />
                </EditorField>
                <EditorField label="Input contract">
                  <ContractSelect
                    document={document}
                    onChange={(value) =>
                      updateSubworkflow(index, {
                        ...reference,
                        input_contract_key: value || null,
                      })
                    }
                    value={reference.input_contract_key ?? ""}
                  />
                </EditorField>
                <EditorField label="Output contract">
                  <ContractSelect
                    document={document}
                    onChange={(value) =>
                      updateSubworkflow(index, {
                        ...reference,
                        output_contract_key: value || null,
                      })
                    }
                    value={reference.output_contract_key ?? ""}
                  />
                </EditorField>
              </div>
              <DependencyWarnings
                warnings={subworkflowDependencyWarnings(document, reference.alias)}
              />
              <ItemActionRow
                canMoveDown={index < document.subworkflow_refs.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() => {
                  const alias = makeUniqueKey(
                    `${reference.alias}-copy`,
                    subworkflowAliases(document),
                  );
                  onChange({
                    ...document,
                    subworkflow_refs: [
                      ...document.subworkflow_refs,
                      {
                        ...reference,
                        alias,
                        display_name: `${reference.display_name ?? reference.alias} copy`,
                      },
                    ],
                  });
                }}
                onMoveDown={() =>
                  onChange({
                    ...document,
                    subworkflow_refs: moveCollectionItem(
                      document.subworkflow_refs,
                      index,
                      1,
                    ),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    subworkflow_refs: moveCollectionItem(
                      document.subworkflow_refs,
                      index,
                      -1,
                    ),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    subworkflow_refs: removeCollectionItem(
                      document.subworkflow_refs,
                      index,
                    ),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}
      <datalist id="workflow-subworkflow-options">
        {catalog.subworkflow_options.map((option) => (
          <option key={option.reference_id} value={option.reference_id}>
            {option.label}
          </option>
        ))}
      </datalist>
    </EditorPanel>
  );
}

function ContractSelect({
  document,
  onChange,
  value,
}: {
  document: WorkflowEditorDocument;
  onChange: (value: string) => void;
  value: string;
}) {
  return (
    <select
      className="ui-input"
      onChange={(event) => onChange(event.target.value)}
      value={value}
    >
      <option value="">None</option>
      {contractKeys(document).map((contractKey) => (
        <option key={contractKey} value={contractKey}>
          {contractKey}
        </option>
      ))}
    </select>
  );
}
