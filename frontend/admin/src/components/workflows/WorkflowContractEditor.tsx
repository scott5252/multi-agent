import { Plus } from "lucide-react";

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
  contractDependencyWarnings,
  contractKeys,
  CONTRACT_KIND_OPTIONS,
  csvToStringList,
  duplicateContract,
  makeUniqueKey,
  moveCollectionItem,
  removeCollectionItem,
  replaceCollectionItem,
  stringListToCsv,
  type WorkflowContractItem,
  type WorkflowEditorDocument,
} from "./workflowDocumentEditor";

interface WorkflowContractEditorProps {
  document: WorkflowEditorDocument;
  onChange: (document: WorkflowEditorDocument) => void;
}

export function WorkflowContractEditor({
  document,
  onChange,
}: WorkflowContractEditorProps) {
  function updateContract(index: number, contract: WorkflowContractItem) {
    onChange({
      ...document,
      contracts: replaceCollectionItem(document.contracts, index, contract),
    });
  }

  function addContract() {
    const contractKey = makeUniqueKey("contract", contractKeys(document));
    onChange({
      ...document,
      contracts: [
        ...document.contracts,
        {
          compatibility_notes: "",
          consumer_keys: [],
          contract_key: contractKey,
          contract_kind: "data_contract",
          display_name: "New contract",
          example_payload: {},
          json_schema: { type: "object" },
          producer_keys: [],
          semantic_version: "1.0.0",
        },
      ],
    });
  }

  return (
    <EditorPanel
      badge={<Badge tone={document.contracts.length > 0 ? "success" : "warning"}>{document.contracts.length} contracts</Badge>}
      id="workflow-contracts"
      summary="Contracts define safe references for roles, edges, joins, approvals, and subworkflows."
      title="Contracts"
    >
      <EditorToolbar>
        <AddButton onClick={addContract}>
          <Plus aria-hidden="true" size={16} />
          Add contract
        </AddButton>
      </EditorToolbar>
      {document.contracts.length === 0 ? (
        <EmptyEditorState>No contracts are defined for this draft.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.contracts.map((contract, index) => (
            <EditorItem
              badge={<Badge tone="info">{contract.contract_kind ?? "data_contract"}</Badge>}
              key={`${contract.contract_key}-${index}`}
              title={contract.display_name ?? contract.contract_key}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        contract_key: event.target.value,
                      })
                    }
                    value={contract.contract_key}
                  />
                </EditorField>
                <EditorField label="Name">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        display_name: event.target.value || null,
                      })
                    }
                    value={contract.display_name ?? ""}
                  />
                </EditorField>
                <EditorField label="Kind">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        contract_kind: event.target.value,
                      })
                    }
                    value={contract.contract_kind ?? "data_contract"}
                  >
                    {CONTRACT_KIND_OPTIONS.map((kind) => (
                      <option key={kind} value={kind}>
                        {kind}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Schema type">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        json_schema: {
                          ...(contract.json_schema ?? {}),
                          type: event.target.value,
                        },
                      })
                    }
                    value={String(contract.json_schema?.type ?? "object")}
                  >
                    <option value="object">object</option>
                    <option value="array">array</option>
                    <option value="string">string</option>
                    <option value="number">number</option>
                    <option value="boolean">boolean</option>
                  </select>
                </EditorField>
                <EditorField label="Producers">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        producer_keys: csvToStringList(event.target.value),
                      })
                    }
                    value={stringListToCsv(contract.producer_keys)}
                  />
                </EditorField>
                <EditorField label="Consumers">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        consumer_keys: csvToStringList(event.target.value),
                      })
                    }
                    value={stringListToCsv(contract.consumer_keys)}
                  />
                </EditorField>
                <EditorField label="Version">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        semantic_version: event.target.value,
                      })
                    }
                    value={contract.semantic_version ?? "1.0.0"}
                  />
                </EditorField>
                <EditorField label="Compatibility notes">
                  <textarea
                    className="ui-input workflow-textarea compact"
                    onChange={(event) =>
                      updateContract(index, {
                        ...contract,
                        compatibility_notes: event.target.value || null,
                      })
                    }
                    rows={3}
                    value={contract.compatibility_notes ?? ""}
                  />
                </EditorField>
              </div>
              <DependencyWarnings
                warnings={contractDependencyWarnings(document, contract.contract_key)}
              />
              <ItemActionRow
                canMoveDown={index < document.contracts.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() =>
                  onChange({
                    ...document,
                    contracts: [
                      ...document.contracts,
                      duplicateContract(document, contract),
                    ],
                  })
                }
                onMoveDown={() =>
                  onChange({
                    ...document,
                    contracts: moveCollectionItem(document.contracts, index, 1),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    contracts: moveCollectionItem(document.contracts, index, -1),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    contracts: removeCollectionItem(document.contracts, index),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}
    </EditorPanel>
  );
}
