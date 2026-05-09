import type {
  WorkflowBuilderStatus,
  WorkflowGraphPreview,
} from "../../api/generated/reactAdminApi";
import type { WorkflowDraftFormValues } from "./WorkflowSectionForm";

export type WorkflowDocumentRecord = Record<string, unknown>;

export interface WorkflowRoleItem extends WorkflowDocumentRecord {
  role_key: string;
  display_name: string;
  role_kind?: string;
  purpose: string;
  responsibilities?: string[];
  profile_reference_key?: string | null;
  prompt_reference_keys?: string[];
  input_contract_key?: string | null;
  output_contract_key?: string | null;
  skill_installation_keys?: string[];
  allowed_tool_policy_refs?: string[];
  graph_node_keys?: string[];
}

export interface WorkflowContractItem extends WorkflowDocumentRecord {
  contract_key: string;
  display_name?: string | null;
  semantic_version?: string;
  contract_kind?: string;
  json_schema?: Record<string, unknown>;
  example_payload?: Record<string, unknown>;
  compatibility_notes?: string | null;
  producer_keys?: string[];
  consumer_keys?: string[];
}

export interface WorkflowNodeItem extends WorkflowDocumentRecord {
  node_key: string;
  node_type: string;
  display_name: string;
  description?: string | null;
  role_key?: string | null;
  subworkflow_alias?: string | null;
  join_policy_key?: string | null;
  approval_gate_key?: string | null;
  active?: boolean;
  retry_policy_key?: string | null;
  editor_position?: Record<string, number>;
}

export interface WorkflowEdgeItem extends WorkflowDocumentRecord {
  edge_key: string;
  source_node_key: string;
  target_node_key: string;
  contract_key?: string | null;
  edge_type?: string;
  branch_condition?: string | null;
  failure_path?: boolean;
  loop_type?: string | null;
  max_attempts?: number | null;
  timeout_seconds?: number | null;
}

export interface WorkflowJoinPolicyItem extends WorkflowDocumentRecord {
  join_policy_key: string;
  strategy: string;
  inbound_edge_keys?: string[];
  required_branches?: string[];
  quorum_count?: number | null;
  timeout_seconds?: number | null;
  failure_behavior?: string;
  output_merge_contract_key?: string | null;
}

export interface WorkflowApprovalGateItem extends WorkflowDocumentRecord {
  approval_gate_key: string;
  display_name: string;
  approver_scope: string;
  approver_role_code?: string | null;
  reason?: string | null;
  decision_contract_key?: string | null;
  resume_behavior?: string | null;
  instructions?: string | null;
}

export interface WorkflowSubworkflowReferenceItem extends WorkflowDocumentRecord {
  alias: string;
  workflow_version_ref: string;
  display_name?: string | null;
  input_contract_key?: string | null;
  output_contract_key?: string | null;
  compatibility_status?: string;
}

export interface WorkflowPromptProfileReferenceItem extends WorkflowDocumentRecord {
  reference_key: string;
  role_key?: string | null;
  agent_key?: string | null;
  agent_kind?: string;
  agent_profile_version_id?: string | null;
  prompt_reference_version_ids?: string[];
  prompt_version_ids?: string[];
  source_scope?: string | null;
  resolution_digest?: string | null;
  readiness_status?: string;
}

export interface WorkflowTestRequirementItem extends WorkflowDocumentRecord {
  requirement_key: string;
  suite_id: string;
  target_type?: string;
  freshness_policy?: string;
  latest_result_id?: string | null;
  latest_result_status?: string;
  executed_at?: string | null;
  safe_summary?: string | null;
}

export interface WorkflowEditorAnnotations extends WorkflowDocumentRecord {
  section_notes: Record<string, string>;
  graph_layout: Record<string, Record<string, number>>;
  collapsed_sections: string[];
}

export interface WorkflowEditorDocument extends WorkflowDocumentRecord {
  workflow_key: string;
  display_name: string;
  description?: string | null;
  workflow_kind: string;
  entry_node_key: string;
  roles: WorkflowRoleItem[];
  prompt_profile_references: WorkflowPromptProfileReferenceItem[];
  contracts: WorkflowContractItem[];
  nodes: WorkflowNodeItem[];
  edges: WorkflowEdgeItem[];
  join_policies: WorkflowJoinPolicyItem[];
  approval_gates: WorkflowApprovalGateItem[];
  subworkflow_refs: WorkflowSubworkflowReferenceItem[];
  test_requirements: WorkflowTestRequirementItem[];
  editor_annotations: WorkflowEditorAnnotations;
}

export const ROLE_KIND_OPTIONS = ["agent", "subagent"];

export const CONTRACT_KIND_OPTIONS = [
  "workflow_input",
  "workflow_output",
  "handoff",
  "artifact",
  "memory",
  "tool_access",
  "approval_decision",
  "failure_outcome",
  "data_contract",
];

export const NODE_TYPE_OPTIONS = [
  "role",
  "join",
  "approval",
  "subworkflow",
  "terminal",
];

export const JOIN_STRATEGY_OPTIONS = [
  "all_success",
  "quorum",
  "first_success",
  "manual_resolution",
];

export const APPROVER_SCOPE_OPTIONS = [
  "tenant_admin",
  "platform_admin",
  "named_role",
];

export function cloneWorkflowDocument(
  document: WorkflowDocumentRecord,
): WorkflowEditorDocument {
  return normalizeWorkflowDocument(
    JSON.parse(JSON.stringify(document)) as WorkflowDocumentRecord,
  );
}

export function normalizeWorkflowDocument(
  document: WorkflowDocumentRecord,
): WorkflowEditorDocument {
  const annotations = asRecord(document.editor_annotations);
  return {
    ...document,
    workflow_key: stringValue(document.workflow_key, "workflow"),
    display_name: stringValue(document.display_name, "Untitled workflow"),
    description: nullableString(document.description),
    workflow_kind: stringValue(document.workflow_kind, "main_workflow"),
    entry_node_key: stringValue(document.entry_node_key, "start"),
    roles: arrayValue(document.roles).map(normalizeRole),
    prompt_profile_references: arrayValue(document.prompt_profile_references).map(
      normalizePromptProfileReference,
    ),
    contracts: arrayValue(document.contracts).map(normalizeContract),
    nodes: arrayValue(document.nodes).map(normalizeNode),
    edges: arrayValue(document.edges).map(normalizeEdge),
    join_policies: arrayValue(document.join_policies).map(normalizeJoinPolicy),
    approval_gates: arrayValue(document.approval_gates).map(normalizeApprovalGate),
    subworkflow_refs: arrayValue(document.subworkflow_refs).map(
      normalizeSubworkflowRef,
    ),
    test_requirements: arrayValue(document.test_requirements).map(
      normalizeTestRequirement,
    ),
    editor_annotations: {
      ...annotations,
      section_notes: stringRecord(annotations.section_notes),
      graph_layout: graphLayoutRecord(annotations.graph_layout),
      collapsed_sections: stringArray(annotations.collapsed_sections),
    },
  };
}

export function applyWorkflowMetadata(
  document: WorkflowEditorDocument,
  values: WorkflowDraftFormValues,
): WorkflowEditorDocument {
  return {
    ...document,
    description: values.description,
    display_name: values.name,
  };
}

export function makeUniqueKey(prefix: string, usedKeys: Iterable<string>): string {
  const normalizedPrefix = slugify(prefix) || "item";
  const used = new Set(Array.from(usedKeys));
  let candidate = normalizedPrefix;
  let index = 2;
  while (used.has(candidate)) {
    candidate = `${normalizedPrefix}-${index}`;
    index += 1;
  }
  return candidate;
}

export function replaceCollectionItem<T extends Record<string, unknown>>(
  items: T[],
  index: number,
  nextItem: T,
): T[] {
  return items.map((item, itemIndex) => (itemIndex === index ? nextItem : item));
}

export function removeCollectionItem<T>(items: T[], index: number): T[] {
  return items.filter((_, itemIndex) => itemIndex !== index);
}

export function moveCollectionItem<T>(
  items: T[],
  index: number,
  direction: -1 | 1,
): T[] {
  const nextIndex = index + direction;
  if (nextIndex < 0 || nextIndex >= items.length) {
    return items;
  }
  const next = [...items];
  const [item] = next.splice(index, 1);
  next.splice(nextIndex, 0, item);
  return next;
}

export function duplicateRole(
  document: WorkflowEditorDocument,
  role: WorkflowRoleItem,
): WorkflowRoleItem {
  const roleKey = makeUniqueKey(`${role.role_key}-copy`, roleKeys(document));
  return {
    ...role,
    display_name: `${role.display_name} copy`,
    graph_node_keys: [],
    role_key: roleKey,
  };
}

export function duplicateContract(
  document: WorkflowEditorDocument,
  contract: WorkflowContractItem,
): WorkflowContractItem {
  const contractKey = makeUniqueKey(
    `${contract.contract_key}-copy`,
    contractKeys(document),
  );
  return {
    ...contract,
    contract_key: contractKey,
    display_name: `${contract.display_name ?? contract.contract_key} copy`,
  };
}

export function buildGraphPreviewFromDocument(
  document: WorkflowEditorDocument,
  fallback: WorkflowGraphPreview,
): WorkflowGraphPreview {
  const rolesByKey = new Map(document.roles.map((role) => [role.role_key, role]));
  const roleByKey = new Map(
    document.roles.map((role) => [role.role_key, role.display_name]),
  );
  const fallbackNodes = new Map(fallback.nodes.map((node) => [node.node_id, node]));
  const nodes = document.nodes.map((node, index) => {
    const fallbackNode = fallbackNodes.get(node.node_key);
    const layout = layoutForNode(document, node, index, fallbackNode);
    const status: WorkflowBuilderStatus =
      node.active === false ? "warning" : "ready";
    return {
      label: node.display_name || node.node_key,
      node_id: node.node_key,
      node_type: node.node_type,
      role_label: node.role_key ? roleByKey.get(node.role_key) ?? node.role_key : null,
      status,
      summary: summaryForNode(
        node,
        node.role_key ? rolesByKey.get(node.role_key) : undefined,
      ),
      x: layout.x,
      y: layout.y,
    };
  });
  const edges = document.edges.map((edge) => ({
    condition_category: edge.edge_type ?? (edge.failure_path ? "failure" : "success"),
    edge_id: edge.edge_key,
    label: edge.branch_condition ?? edge.edge_type ?? null,
    source: edge.source_node_key,
    target: edge.target_node_key,
  }));
  const joinPolicies = document.join_policies.map((policy) => ({
    label: readableLabel(policy.join_policy_key),
    policy_id: policy.join_policy_key,
    required_branch_count:
      policy.required_branches?.length || policy.inbound_edge_keys?.length || 0,
    summary: `${policy.strategy} / ${policy.failure_behavior ?? "block"}`,
  }));
  return {
    accessibility_summary: `Editable graph has ${nodes.length} nodes, ${edges.length} edges, ${joinPolicies.length} join policies, ${testEvidenceSummary(document)}, and ${bindingReadinessSummary(document)}.`,
    edges,
    join_policies: joinPolicies,
    layout_is_authoritative: false,
    layout_revision: "dirty-document",
    nodes,
  };
}

export function roleDependencyWarnings(
  document: WorkflowEditorDocument,
  roleKey: string,
): string[] {
  const nodes = document.nodes.filter((node) => node.role_key === roleKey);
  const warnings = nodes.map((node) => `Referenced by node ${node.node_key}`);
  const role = document.roles.find((item) => item.role_key === roleKey);
  if (role?.graph_node_keys?.length) {
    warnings.push(`Lists ${role.graph_node_keys.length} graph node associations`);
  }
  return warnings;
}

export function contractDependencyWarnings(
  document: WorkflowEditorDocument,
  contractKey: string,
): string[] {
  const warnings: string[] = [];
  document.roles.forEach((role) => {
    if (
      role.input_contract_key === contractKey ||
      role.output_contract_key === contractKey
    ) {
      warnings.push(`Referenced by role ${role.role_key}`);
    }
  });
  document.edges.forEach((edge) => {
    if (edge.contract_key === contractKey) {
      warnings.push(`Referenced by edge ${edge.edge_key}`);
    }
  });
  document.join_policies.forEach((policy) => {
    if (policy.output_merge_contract_key === contractKey) {
      warnings.push(`Referenced by join ${policy.join_policy_key}`);
    }
  });
  document.approval_gates.forEach((gate) => {
    if (gate.decision_contract_key === contractKey) {
      warnings.push(`Referenced by approval ${gate.approval_gate_key}`);
    }
  });
  document.subworkflow_refs.forEach((reference) => {
    if (
      reference.input_contract_key === contractKey ||
      reference.output_contract_key === contractKey
    ) {
      warnings.push(`Referenced by subworkflow ${reference.alias}`);
    }
  });
  return warnings;
}

export function nodeDependencyWarnings(
  document: WorkflowEditorDocument,
  nodeKey: string,
): string[] {
  const warnings: string[] = [];
  document.edges.forEach((edge) => {
    if (edge.source_node_key === nodeKey || edge.target_node_key === nodeKey) {
      warnings.push(`Referenced by edge ${edge.edge_key}`);
    }
  });
  document.roles.forEach((role) => {
    if (role.graph_node_keys?.includes(nodeKey)) {
      warnings.push(`Referenced by role ${role.role_key}`);
    }
  });
  if (document.entry_node_key === nodeKey) {
    warnings.push("Current entry node");
  }
  return warnings;
}

export function edgeDependencyWarnings(
  document: WorkflowEditorDocument,
  edgeKey: string,
): string[] {
  return document.join_policies
    .filter((policy) => policy.inbound_edge_keys?.includes(edgeKey))
    .map((policy) => `Referenced by join ${policy.join_policy_key}`);
}

export function joinDependencyWarnings(
  document: WorkflowEditorDocument,
  joinKey: string,
): string[] {
  return document.nodes
    .filter((node) => node.join_policy_key === joinKey)
    .map((node) => `Referenced by node ${node.node_key}`);
}

export function approvalDependencyWarnings(
  document: WorkflowEditorDocument,
  approvalKey: string,
): string[] {
  return document.nodes
    .filter((node) => node.approval_gate_key === approvalKey)
    .map((node) => `Referenced by node ${node.node_key}`);
}

export function subworkflowDependencyWarnings(
  document: WorkflowEditorDocument,
  alias: string,
): string[] {
  return document.nodes
    .filter((node) => node.subworkflow_alias === alias)
    .map((node) => `Referenced by node ${node.node_key}`);
}

export function roleKeys(document: WorkflowEditorDocument): string[] {
  return document.roles.map((role) => role.role_key);
}

export function promptProfileReferenceKeys(
  document: WorkflowEditorDocument,
): string[] {
  return document.prompt_profile_references.map(
    (reference) => reference.reference_key,
  );
}

export function contractKeys(document: WorkflowEditorDocument): string[] {
  return document.contracts.map((contract) => contract.contract_key);
}

export function nodeKeys(document: WorkflowEditorDocument): string[] {
  return document.nodes.map((node) => node.node_key);
}

export function edgeKeys(document: WorkflowEditorDocument): string[] {
  return document.edges.map((edge) => edge.edge_key);
}

export function joinKeys(document: WorkflowEditorDocument): string[] {
  return document.join_policies.map((policy) => policy.join_policy_key);
}

export function approvalKeys(document: WorkflowEditorDocument): string[] {
  return document.approval_gates.map((gate) => gate.approval_gate_key);
}

export function subworkflowAliases(document: WorkflowEditorDocument): string[] {
  return document.subworkflow_refs.map((reference) => reference.alias);
}

export function testRequirementKeys(document: WorkflowEditorDocument): string[] {
  return document.test_requirements.map(
    (requirement) => requirement.requirement_key,
  );
}

export function csvToStringList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function linesToStringList(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function stringListToLines(value: string[] | undefined): string {
  return (value ?? []).join("\n");
}

export function stringListToCsv(value: string[] | undefined): string {
  return (value ?? []).join(", ");
}

function normalizeRole(value: unknown): WorkflowRoleItem {
  const record = asRecord(value);
  return {
    ...record,
    allowed_tool_policy_refs: stringArray(record.allowed_tool_policy_refs),
    display_name: stringValue(record.display_name, "Role"),
    graph_node_keys: stringArray(record.graph_node_keys),
    input_contract_key: nullableString(record.input_contract_key),
    output_contract_key: nullableString(record.output_contract_key),
    profile_reference_key: nullableString(record.profile_reference_key),
    prompt_reference_keys: stringArray(record.prompt_reference_keys),
    purpose: stringValue(record.purpose, ""),
    responsibilities: stringArray(record.responsibilities),
    role_key: stringValue(record.role_key, "role"),
    role_kind: stringValue(record.role_kind, "agent"),
    skill_installation_keys: stringArray(record.skill_installation_keys),
  };
}

function normalizePromptProfileReference(
  value: unknown,
): WorkflowPromptProfileReferenceItem {
  const record = asRecord(value);
  return {
    ...record,
    agent_kind: stringValue(record.agent_kind, "agent"),
    agent_key: nullableString(record.agent_key),
    agent_profile_version_id: nullableString(record.agent_profile_version_id),
    prompt_reference_version_ids: stringArray(
      record.prompt_reference_version_ids,
    ),
    prompt_version_ids: stringArray(record.prompt_version_ids),
    readiness_status: stringValue(record.readiness_status, "unknown"),
    reference_key: stringValue(record.reference_key, "prompt-profile"),
    resolution_digest: nullableString(record.resolution_digest),
    role_key: nullableString(record.role_key),
    source_scope: nullableString(record.source_scope),
  };
}

function normalizeTestRequirement(value: unknown): WorkflowTestRequirementItem {
  const record = asRecord(value);
  return {
    ...record,
    executed_at: nullableString(record.executed_at),
    freshness_policy: stringValue(record.freshness_policy, "latest_revision"),
    latest_result_id: nullableString(record.latest_result_id),
    latest_result_status: stringValue(record.latest_result_status, "missing"),
    requirement_key: stringValue(record.requirement_key, "required-test-evidence"),
    safe_summary: nullableString(record.safe_summary),
    suite_id: stringValue(record.suite_id, ""),
    target_type: stringValue(record.target_type, "workflow_revision"),
  };
}

function normalizeContract(value: unknown): WorkflowContractItem {
  const record = asRecord(value);
  return {
    ...record,
    compatibility_notes: nullableString(record.compatibility_notes),
    consumer_keys: stringArray(record.consumer_keys),
    contract_key: stringValue(record.contract_key, "contract"),
    contract_kind: stringValue(record.contract_kind, "data_contract"),
    display_name: nullableString(record.display_name),
    example_payload: asRecord(record.example_payload),
    json_schema: asRecord(record.json_schema),
    producer_keys: stringArray(record.producer_keys),
    semantic_version: stringValue(record.semantic_version, "1.0.0"),
  };
}

function normalizeNode(value: unknown): WorkflowNodeItem {
  const record = asRecord(value);
  return {
    ...record,
    active: record.active !== false,
    approval_gate_key: nullableString(record.approval_gate_key),
    description: nullableString(record.description),
    display_name: stringValue(record.display_name, "Node"),
    editor_position: numberRecord(record.editor_position),
    join_policy_key: nullableString(record.join_policy_key),
    node_key: stringValue(record.node_key, "node"),
    node_type: stringValue(record.node_type, "role"),
    role_key: nullableString(record.role_key),
    subworkflow_alias: nullableString(record.subworkflow_alias),
  };
}

function normalizeEdge(value: unknown): WorkflowEdgeItem {
  const record = asRecord(value);
  return {
    ...record,
    branch_condition: nullableString(record.branch_condition),
    contract_key: nullableString(record.contract_key),
    edge_key: stringValue(record.edge_key, "edge"),
    edge_type: stringValue(record.edge_type, "success"),
    failure_path: record.failure_path === true,
    loop_type: nullableString(record.loop_type),
    max_attempts: nullableNumber(record.max_attempts),
    source_node_key: stringValue(record.source_node_key, ""),
    target_node_key: stringValue(record.target_node_key, ""),
    timeout_seconds: nullableNumber(record.timeout_seconds),
  };
}

function normalizeJoinPolicy(value: unknown): WorkflowJoinPolicyItem {
  const record = asRecord(value);
  return {
    ...record,
    failure_behavior: stringValue(record.failure_behavior, "block"),
    inbound_edge_keys: stringArray(record.inbound_edge_keys),
    join_policy_key: stringValue(record.join_policy_key, "join-policy"),
    output_merge_contract_key: nullableString(record.output_merge_contract_key),
    quorum_count: nullableNumber(record.quorum_count),
    required_branches: stringArray(record.required_branches),
    strategy: stringValue(record.strategy, "all_success"),
    timeout_seconds: nullableNumber(record.timeout_seconds),
  };
}

function normalizeApprovalGate(value: unknown): WorkflowApprovalGateItem {
  const record = asRecord(value);
  return {
    ...record,
    approval_gate_key: stringValue(record.approval_gate_key, "approval"),
    approver_role_code: nullableString(record.approver_role_code),
    approver_scope: stringValue(record.approver_scope, "tenant_admin"),
    decision_contract_key: nullableString(record.decision_contract_key),
    display_name: stringValue(record.display_name, "Approval gate"),
    instructions: nullableString(record.instructions),
    reason: nullableString(record.reason),
    resume_behavior: nullableString(record.resume_behavior),
  };
}

function normalizeSubworkflowRef(value: unknown): WorkflowSubworkflowReferenceItem {
  const record = asRecord(value);
  return {
    ...record,
    alias: stringValue(record.alias, "subworkflow"),
    compatibility_status: stringValue(record.compatibility_status, "unknown"),
    display_name: nullableString(record.display_name),
    input_contract_key: nullableString(record.input_contract_key),
    output_contract_key: nullableString(record.output_contract_key),
    workflow_version_ref: stringValue(record.workflow_version_ref, ""),
  };
}

function layoutForNode(
  document: WorkflowEditorDocument,
  node: WorkflowNodeItem,
  index: number,
  fallbackNode: { x: number; y: number } | undefined,
): { x: number; y: number } {
  const annotated = document.editor_annotations.graph_layout[node.node_key];
  const editor = node.editor_position ?? {};
  return {
    x:
      numberValue(editor.x) ??
      numberValue(annotated?.x) ??
      fallbackNode?.x ??
      (index % 4) * 240,
    y:
      numberValue(editor.y) ??
      numberValue(annotated?.y) ??
      fallbackNode?.y ??
      Math.floor(index / 4) * 150,
  };
}

function summaryForNode(
  node: WorkflowNodeItem,
  role: WorkflowRoleItem | undefined,
): string {
  if (node.description) {
    return node.description;
  }
  if (node.node_type === "role" && node.role_key) {
    return `Runs role ${node.role_key}. ${bindingStatusSummary(role)}`;
  }
  if (node.node_type === "join" && node.join_policy_key) {
    return `Applies join policy ${node.join_policy_key}.`;
  }
  if (node.node_type === "approval" && node.approval_gate_key) {
    return `Waits for approval ${node.approval_gate_key}.`;
  }
  if (node.node_type === "subworkflow" && node.subworkflow_alias) {
    return `Calls subworkflow ${node.subworkflow_alias}.`;
  }
  return `${node.node_type} node.`;
}

function bindingReadinessSummary(document: WorkflowEditorDocument): string {
  const readyRoles = document.roles.filter(
    (role) =>
      (role.prompt_reference_keys ?? []).length > 0 &&
      Boolean(role.profile_reference_key),
  ).length;
  return `${readyRoles} of ${document.roles.length} roles with prompt/profile bindings`;
}

function testEvidenceSummary(document: WorkflowEditorDocument): string {
  const total = document.test_requirements.length;
  const ready = document.test_requirements.filter((requirement) =>
    ["passed", "passing", "ready"].includes(
      requirement.latest_result_status ?? "missing",
    ),
  ).length;
  if (total === 0) {
    return "0 required evidence items";
  }
  return `${ready} of ${total} required evidence items current`;
}

function bindingStatusSummary(role: WorkflowRoleItem | undefined): string {
  if (!role) {
    return "Prompt/profile binding is unknown.";
  }
  const hasPrompt = (role.prompt_reference_keys ?? []).length > 0;
  const hasProfile = Boolean(role.profile_reference_key);
  if (hasPrompt && hasProfile) {
    return "Prompt/profile binding is ready.";
  }
  if (hasPrompt) {
    return "Runtime profile binding is missing.";
  }
  if (hasProfile) {
    return "Prompt binding is missing.";
  }
  return "Prompt/profile bindings are missing.";
}

function readableLabel(value: string): string {
  return value
    .split(/[-_]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function slugify(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function asRecord(value: unknown): WorkflowDocumentRecord {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as WorkflowDocumentRecord;
  }
  return {};
}

function arrayValue(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map((item) => String(item)).filter(Boolean);
}

function stringRecord(value: unknown): Record<string, string> {
  const record = asRecord(value);
  return Object.fromEntries(
    Object.entries(record).map(([key, item]) => [key, String(item)]),
  );
}

function graphLayoutRecord(value: unknown): Record<string, Record<string, number>> {
  const record = asRecord(value);
  return Object.fromEntries(
    Object.entries(record).map(([key, item]) => [key, numberRecord(item)]),
  );
}

function numberRecord(value: unknown): Record<string, number> {
  const record = asRecord(value);
  return Object.fromEntries(
    Object.entries(record)
      .map(([key, item]) => [key, numberValue(item)])
      .filter((entry): entry is [string, number] => entry[1] !== null),
  );
}

function stringValue(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function nullableString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function nullableNumber(value: unknown): number | null {
  const valueAsNumber = numberValue(value);
  return valueAsNumber === null ? null : valueAsNumber;
}

function numberValue(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}
