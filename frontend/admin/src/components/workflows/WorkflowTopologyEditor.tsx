import { GitBranchPlus, Plus } from "lucide-react";

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
  contractKeys,
  edgeDependencyWarnings,
  edgeKeys,
  makeUniqueKey,
  moveCollectionItem,
  NODE_TYPE_OPTIONS,
  nodeDependencyWarnings,
  nodeKeys,
  removeCollectionItem,
  replaceCollectionItem,
  type WorkflowEdgeItem,
  type WorkflowEditorDocument,
  type WorkflowNodeItem,
} from "./workflowDocumentEditor";

interface WorkflowTopologyEditorProps {
  document: WorkflowEditorDocument;
  onChange: (document: WorkflowEditorDocument) => void;
}

export function WorkflowTopologyEditor({
  document,
  onChange,
}: WorkflowTopologyEditorProps) {
  function updateNode(index: number, node: WorkflowNodeItem) {
    onChange({
      ...document,
      nodes: replaceCollectionItem(document.nodes, index, node),
    });
  }

  function updateEdge(index: number, edge: WorkflowEdgeItem) {
    onChange({
      ...document,
      edges: replaceCollectionItem(document.edges, index, edge),
    });
  }

  function addNode(nodeType = "role") {
    const nodeKey = makeUniqueKey(nodeType, nodeKeys(document));
    onChange({
      ...document,
      entry_node_key: document.nodes.length === 0 ? nodeKey : document.entry_node_key,
      nodes: [
        ...document.nodes,
        {
          active: true,
          display_name: `New ${nodeType}`,
          editor_position: {
            x: (document.nodes.length % 4) * 240,
            y: Math.floor(document.nodes.length / 4) * 150,
          },
          node_key: nodeKey,
          node_type: nodeType,
          role_key:
            nodeType === "role" ? document.roles[0]?.role_key ?? null : null,
        },
      ],
    });
  }

  function addEdge() {
    const edgeKey = makeUniqueKey("edge", edgeKeys(document));
    const firstNode = document.nodes[0]?.node_key ?? "";
    const secondNode = document.nodes[1]?.node_key ?? firstNode;
    onChange({
      ...document,
      edges: [
        ...document.edges,
        {
          branch_condition: "success",
          contract_key: document.contracts[0]?.contract_key ?? null,
          edge_key: edgeKey,
          edge_type: "success",
          failure_path: false,
          source_node_key: firstNode,
          target_node_key: secondNode,
        },
      ],
    });
  }

  return (
    <EditorPanel
      badge={<Badge tone={document.nodes.length > 0 ? "success" : "warning"}>{document.nodes.length} nodes / {document.edges.length} edges</Badge>}
      id="workflow-graph"
      summary="Topology controls update the graph canvas and keyboard-readable lists before save."
      title="Graph Topology"
    >
      <EditorToolbar>
        <AddButton onClick={() => addNode("role")}>
          <Plus aria-hidden="true" size={16} />
          Add node
        </AddButton>
        <AddButton onClick={() => addNode("join")}>
          <GitBranchPlus aria-hidden="true" size={16} />
          Add join node
        </AddButton>
        <AddButton onClick={addEdge}>
          <Plus aria-hidden="true" size={16} />
          Add edge
        </AddButton>
      </EditorToolbar>

      <EditorField label="Entry node">
        <select
          className="ui-input"
          onChange={(event) =>
            onChange({ ...document, entry_node_key: event.target.value })
          }
          value={document.entry_node_key}
        >
          {document.nodes.map((node) => (
            <option key={node.node_key} value={node.node_key}>
              {node.display_name || node.node_key}
            </option>
          ))}
        </select>
      </EditorField>

      <h3 className="workflow-editor-subtitle">Nodes</h3>
      {document.nodes.length === 0 ? (
        <EmptyEditorState>No graph nodes are defined for this draft.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.nodes.map((node, index) => (
            <EditorItem
              badge={<Badge tone={node.active === false ? "warning" : "success"}>{node.node_type}</Badge>}
              key={`${node.node_key}-${index}`}
              title={node.display_name || node.node_key}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        node_key: event.target.value,
                      })
                    }
                    value={node.node_key}
                  />
                </EditorField>
                <EditorField label="Name">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        display_name: event.target.value,
                      })
                    }
                    value={node.display_name}
                  />
                </EditorField>
                <EditorField label="Type">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        approval_gate_key: null,
                        join_policy_key: null,
                        node_type: event.target.value,
                        role_key:
                          event.target.value === "role"
                            ? node.role_key ?? document.roles[0]?.role_key ?? null
                            : null,
                        subworkflow_alias: null,
                      })
                    }
                    value={node.node_type}
                  >
                    {NODE_TYPE_OPTIONS.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </EditorField>
                {node.node_type === "role" ? (
                  <EditorField label="Role">
                    <select
                      className="ui-input"
                      onChange={(event) =>
                        updateNode(index, {
                          ...node,
                          role_key: event.target.value || null,
                        })
                      }
                      value={node.role_key ?? ""}
                    >
                      <option value="">None</option>
                      {document.roles.map((role) => (
                        <option key={role.role_key} value={role.role_key}>
                          {role.display_name}
                        </option>
                      ))}
                    </select>
                  </EditorField>
                ) : null}
                {node.node_type === "join" ? (
                  <EditorField label="Join policy">
                    <select
                      className="ui-input"
                      onChange={(event) =>
                        updateNode(index, {
                          ...node,
                          join_policy_key: event.target.value || null,
                        })
                      }
                      value={node.join_policy_key ?? ""}
                    >
                      <option value="">None</option>
                      {document.join_policies.map((policy) => (
                        <option
                          key={policy.join_policy_key}
                          value={policy.join_policy_key}
                        >
                          {policy.join_policy_key}
                        </option>
                      ))}
                    </select>
                  </EditorField>
                ) : null}
                {node.node_type === "approval" ? (
                  <EditorField label="Approval gate">
                    <select
                      className="ui-input"
                      onChange={(event) =>
                        updateNode(index, {
                          ...node,
                          approval_gate_key: event.target.value || null,
                        })
                      }
                      value={node.approval_gate_key ?? ""}
                    >
                      <option value="">None</option>
                      {document.approval_gates.map((gate) => (
                        <option
                          key={gate.approval_gate_key}
                          value={gate.approval_gate_key}
                        >
                          {gate.display_name}
                        </option>
                      ))}
                    </select>
                  </EditorField>
                ) : null}
                {node.node_type === "subworkflow" ? (
                  <EditorField label="Subworkflow">
                    <select
                      className="ui-input"
                      onChange={(event) =>
                        updateNode(index, {
                          ...node,
                          subworkflow_alias: event.target.value || null,
                        })
                      }
                      value={node.subworkflow_alias ?? ""}
                    >
                      <option value="">None</option>
                      {document.subworkflow_refs.map((reference) => (
                        <option key={reference.alias} value={reference.alias}>
                          {reference.display_name ?? reference.alias}
                        </option>
                      ))}
                    </select>
                  </EditorField>
                ) : null}
                <EditorField label="X">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        editor_position: {
                          ...(node.editor_position ?? {}),
                          x: Number(event.target.value) || 0,
                        },
                      })
                    }
                    type="number"
                    value={node.editor_position?.x ?? 0}
                  />
                </EditorField>
                <EditorField label="Y">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        editor_position: {
                          ...(node.editor_position ?? {}),
                          y: Number(event.target.value) || 0,
                        },
                      })
                    }
                    type="number"
                    value={node.editor_position?.y ?? 0}
                  />
                </EditorField>
                <label className="checkbox-row">
                  <input
                    checked={node.active !== false}
                    onChange={(event) =>
                      updateNode(index, {
                        ...node,
                        active: event.target.checked,
                      })
                    }
                    type="checkbox"
                  />
                  Active
                </label>
              </div>
              <DependencyWarnings
                warnings={nodeDependencyWarnings(document, node.node_key)}
              />
              <ItemActionRow
                canMoveDown={index < document.nodes.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() => {
                  const nodeKey = makeUniqueKey(
                    `${node.node_key}-copy`,
                    nodeKeys(document),
                  );
                  onChange({
                    ...document,
                    nodes: [
                      ...document.nodes,
                      {
                        ...node,
                        display_name: `${node.display_name} copy`,
                        node_key: nodeKey,
                      },
                    ],
                  });
                }}
                onMoveDown={() =>
                  onChange({
                    ...document,
                    nodes: moveCollectionItem(document.nodes, index, 1),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    nodes: moveCollectionItem(document.nodes, index, -1),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    nodes: removeCollectionItem(document.nodes, index),
                  })
                }
              />
            </EditorItem>
          ))}
        </EditorGrid>
      )}

      <h3 className="workflow-editor-subtitle">Edges</h3>
      {document.edges.length === 0 ? (
        <EmptyEditorState>No graph edges are defined for this draft.</EmptyEditorState>
      ) : (
        <EditorGrid>
          {document.edges.map((edge, index) => (
            <EditorItem
              badge={<Badge tone={edge.failure_path ? "warning" : "info"}>{edge.edge_type ?? "success"}</Badge>}
              key={`${edge.edge_key}-${index}`}
              title={edge.edge_key}
            >
              <div className="workflow-editor-fields">
                <EditorField label="Key">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        edge_key: event.target.value,
                      })
                    }
                    value={edge.edge_key}
                  />
                </EditorField>
                <EditorField label="Source">
                  <NodeSelect
                    document={document}
                    onChange={(value) =>
                      updateEdge(index, {
                        ...edge,
                        source_node_key: value,
                      })
                    }
                    value={edge.source_node_key}
                  />
                </EditorField>
                <EditorField label="Target">
                  <NodeSelect
                    document={document}
                    onChange={(value) =>
                      updateEdge(index, {
                        ...edge,
                        target_node_key: value,
                      })
                    }
                    value={edge.target_node_key}
                  />
                </EditorField>
                <EditorField label="Contract">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        contract_key: event.target.value || null,
                      })
                    }
                    value={edge.contract_key ?? ""}
                  >
                    <option value="">None</option>
                    {contractKeys(document).map((contractKey) => (
                      <option key={contractKey} value={contractKey}>
                        {contractKey}
                      </option>
                    ))}
                  </select>
                </EditorField>
                <EditorField label="Type">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        edge_type: event.target.value,
                      })
                    }
                    value={edge.edge_type ?? "success"}
                  >
                    <option value="success">success</option>
                    <option value="failure">failure</option>
                    <option value="conditional">conditional</option>
                    <option value="approval_resume">approval_resume</option>
                  </select>
                </EditorField>
                <EditorField label="Branch label">
                  <input
                    className="ui-input"
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        branch_condition: event.target.value || null,
                      })
                    }
                    value={edge.branch_condition ?? ""}
                  />
                </EditorField>
                <EditorField label="Loop type">
                  <select
                    className="ui-input"
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        loop_type: event.target.value || null,
                      })
                    }
                    value={edge.loop_type ?? ""}
                  >
                    <option value="">None</option>
                    <option value="retry">retry</option>
                    <option value="approval_resume">approval_resume</option>
                  </select>
                </EditorField>
                <label className="checkbox-row">
                  <input
                    checked={edge.failure_path === true}
                    onChange={(event) =>
                      updateEdge(index, {
                        ...edge,
                        failure_path: event.target.checked,
                      })
                    }
                    type="checkbox"
                  />
                  Failure path
                </label>
              </div>
              <DependencyWarnings
                warnings={edgeDependencyWarnings(document, edge.edge_key)}
              />
              <ItemActionRow
                canMoveDown={index < document.edges.length - 1}
                canMoveUp={index > 0}
                onDuplicate={() => {
                  const edgeKey = makeUniqueKey(
                    `${edge.edge_key}-copy`,
                    edgeKeys(document),
                  );
                  onChange({
                    ...document,
                    edges: [
                      ...document.edges,
                      {
                        ...edge,
                        edge_key: edgeKey,
                      },
                    ],
                  });
                }}
                onMoveDown={() =>
                  onChange({
                    ...document,
                    edges: moveCollectionItem(document.edges, index, 1),
                  })
                }
                onMoveUp={() =>
                  onChange({
                    ...document,
                    edges: moveCollectionItem(document.edges, index, -1),
                  })
                }
                onRemove={() =>
                  onChange({
                    ...document,
                    edges: removeCollectionItem(document.edges, index),
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

function NodeSelect({
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
      {document.nodes.map((node) => (
        <option key={node.node_key} value={node.node_key}>
          {node.display_name || node.node_key}
        </option>
      ))}
    </select>
  );
}
