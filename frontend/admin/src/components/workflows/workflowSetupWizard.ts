import type {
  WorkflowPublishReadiness,
  WorkflowValidationSummary,
} from "../../api/generated/reactAdminApi";
import type {
  WorkflowContractItem,
  WorkflowEditorDocument,
  WorkflowJoinPolicyItem,
  WorkflowNodeItem,
  WorkflowPromptProfileReferenceItem,
  WorkflowRoleItem,
} from "./workflowDocumentEditor";

export type WorkflowSetupStepKey =
  | "scenario"
  | "metadata"
  | "agents"
  | "bindings"
  | "graph"
  | "contracts"
  | "evidence"
  | "validation"
  | "publish"
  | "runtime";

export type WorkflowSetupStepStatus = "complete" | "active" | "blocked";

export interface WorkflowSetupStep {
  key: WorkflowSetupStepKey;
  title: string;
  summary: string;
  href: string;
  status: WorkflowSetupStepStatus;
}

export interface WorkflowSetupProgress {
  completeCount: number;
  percent: number;
  steps: WorkflowSetupStep[];
  totalCount: number;
}

export interface WorkflowScenarioIntake {
  agentCount: number;
  approvalNeeds: string;
  coordinationPattern: "parallel_review" | "sequential_handoff";
  desiredOutputs: string;
  evidencePreference: "deterministic_safe_run" | "manual_before_publish";
  expectedInputs: string;
  optionalChannels: string;
  purpose: string;
  triggerMode: "manual_launch" | "channel_or_api";
  workflowKey: string;
  workflowName: string;
}

export const DEFAULT_WORKFLOW_SCENARIO_INTAKE: WorkflowScenarioIntake = {
  agentCount: 3,
  approvalNeeds: "No approval required before publish.",
  coordinationPattern: "parallel_review",
  desiredOutputs: "A safe final result with a concise operational summary.",
  evidencePreference: "deterministic_safe_run",
  expectedInputs: "A user request with enough context to start the workflow.",
  optionalChannels: "Browser launch first; channels can be configured later.",
  purpose: "Coordinate a reusable workflow for the selected tenant scenario.",
  triggerMode: "manual_launch",
  workflowKey: "tenant-workflow",
  workflowName: "Tenant workflow",
};

export const WORKFLOW_ONBOARDING_STEPS: WorkflowSetupStep[] = [
  {
    href: "#wizard-scenario",
    key: "scenario",
    status: "active",
    summary: "Describe the workflow goal, inputs, outputs, and coordination.",
    title: "Scenario",
  },
  {
    href: "#wizard-metadata",
    key: "metadata",
    status: "blocked",
    summary: "Name and save the durable workflow draft.",
    title: "Draft",
  },
  {
    href: "#wizard-agents",
    key: "agents",
    status: "blocked",
    summary: "Review agent roles and responsibilities one at a time.",
    title: "Agents",
  },
  {
    href: "#wizard-contracts",
    key: "contracts",
    status: "blocked",
    summary: "Review input, handoff, output, and approval contracts.",
    title: "Contracts",
  },
  {
    href: "#wizard-graph",
    key: "graph",
    status: "blocked",
    summary: "Check nodes, edges, joins, and approval gates.",
    title: "Graph",
  },
  {
    href: "#wizard-bindings",
    key: "bindings",
    status: "blocked",
    summary: "Review prompt, profile, provider, skill, and channel readiness.",
    title: "Resources",
  },
  {
    href: "#wizard-evidence",
    key: "evidence",
    status: "blocked",
    summary: "Attach required Test Bench evidence to the draft.",
    title: "Evidence",
  },
  {
    href: "#wizard-publish",
    key: "publish",
    status: "blocked",
    summary: "Validate and publish through backend-owned gates.",
    title: "Publish",
  },
  {
    href: "#wizard-runtime",
    key: "runtime",
    status: "blocked",
    summary: "Launch or inspect safe runtime and graph evidence.",
    title: "Launch",
  },
];

export function buildWorkflowSetupProgress({
  document,
  publishedVersionId,
  publishReadiness,
  validation,
}: {
  document: WorkflowEditorDocument;
  publishedVersionId: string | null;
  publishReadiness: WorkflowPublishReadiness;
  validation: WorkflowValidationSummary;
}): WorkflowSetupProgress {
  const promptProfileReady = document.roles.every(
    (role) =>
      Boolean(role.profile_reference_key) &&
      (role.prompt_reference_keys ?? []).length > 0,
  );
  const referenceReady = document.prompt_profile_references.every((reference) =>
    ["ready", "active"].includes(reference.readiness_status ?? ""),
  );
  const hasJoinNode = document.nodes.some(
    (node) => node.node_type === "join" && Boolean(node.join_policy_key),
  );
  const evidenceReady =
    publishReadiness.required_evidence.some((item) =>
      ["ready", "passed", "passing"].includes(item.status),
    ) ||
    document.test_requirements.some((requirement) =>
      ["passed", "passing"].includes(requirement.latest_result_status ?? ""),
    );
  const validationReady = ["ready", "passed"].includes(validation.status);
  const published =
    Boolean(publishedVersionId) ||
    publishReadiness.decision === "accepted" ||
    Boolean(publishReadiness.published_bundle_summary);

  const checks = [
    {
      href: "#workflow-metadata",
      key: "metadata" as const,
      ready: Boolean(document.display_name.trim() && document.workflow_key.trim()),
      summary: document.display_name
        ? `${document.display_name} is named for this draft.`
        : "Add a workflow name before publish.",
      title: "Metadata",
    },
    {
      href: "#workflow-roles",
      key: "agents" as const,
      ready: document.roles.length >= 3,
      summary: `${document.roles.length}/3 agent roles are present.`,
      title: "Agents",
    },
    {
      href: "#workflow-prompt-profiles",
      key: "bindings" as const,
      ready:
        document.roles.length >= 3 &&
        promptProfileReady &&
        referenceReady &&
        document.prompt_profile_references.length >= document.roles.length,
      summary: promptProfileReady
        ? "Each role has prompt and runtime profile references."
        : "Bind prompt and runtime profile references to every role.",
      title: "Prompts And Profiles",
    },
    {
      href: "#workflow-graph",
      key: "graph" as const,
      ready:
        document.nodes.length >= 4 &&
        document.edges.length >= 4 &&
        document.join_policies.length > 0 &&
        hasJoinNode,
      summary: `${document.nodes.length} nodes, ${document.edges.length} edges, ${document.join_policies.length} join policies.`,
      title: "Graph",
    },
    {
      href: "#workflow-contracts",
      key: "contracts" as const,
      ready: document.contracts.length >= 2,
      summary: `${document.contracts.length} durable contracts are defined.`,
      title: "Contracts",
    },
    {
      href: "#workflow-test-evidence",
      key: "evidence" as const,
      ready: document.test_requirements.length > 0 && evidenceReady,
      summary:
        document.test_requirements.length > 0
          ? publishReadiness.required_evidence[0]?.summary ??
            "Required evidence is attached."
          : "Attach a required suite and launch deterministic evidence.",
      title: "Evidence",
    },
    {
      href: "#workflow-validation",
      key: "validation" as const,
      ready: validationReady,
      summary: validation.summary,
      title: "Validation",
    },
    {
      href: "#workflow-publish",
      key: "publish" as const,
      ready: published,
      summary: published
        ? publishReadiness.published_bundle_summary ??
          "Published workflow bundle is available."
        : publishReadiness.summary,
      title: "Publish",
    },
    {
      href: "#workflow-runtime-launch",
      key: "runtime" as const,
      ready: published,
      summary: published
        ? "Runtime and Design Review surfaces can select this workflow."
        : "Publish before launching or selecting the workflow.",
      title: "Launch",
    },
  ];

  const firstIncomplete = checks.findIndex((step) => !step.ready);
  const steps = checks.map((step, index) => {
    const status: WorkflowSetupStepStatus = step.ready
      ? "complete"
      : index === firstIncomplete
        ? "active"
        : "blocked";
    return {
      href: step.href,
      key: step.key,
      status,
      summary: step.summary,
      title: step.title,
    };
  });
  const completeCount = steps.filter((step) => step.status === "complete").length;
  return {
    completeCount,
    percent: Math.round((completeCount / steps.length) * 100),
    steps,
    totalCount: steps.length,
  };
}

export function normalizeWorkflowKey(value: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 64);
  return normalized || "tenant-workflow";
}

export function intakeWithDerivedKey(
  intake: WorkflowScenarioIntake,
): WorkflowScenarioIntake {
  const workflowKey = normalizeWorkflowKey(
    intake.workflowKey || intake.workflowName || DEFAULT_WORKFLOW_SCENARIO_INTAKE.workflowKey,
  );
  return {
    ...intake,
    agentCount: Math.min(Math.max(Math.round(intake.agentCount || 3), 1), 5),
    workflowKey,
    workflowName: intake.workflowName.trim() || readableFromKey(workflowKey),
  };
}

export function buildBlankWorkflowDocument(
  intake: WorkflowScenarioIntake,
): WorkflowEditorDocument {
  const normalized = intakeWithDerivedKey(intake);
  return {
    approval_gates: [],
    contracts: [],
    description: normalized.purpose,
    display_name: normalized.workflowName,
    edges: [],
    editor_annotations: {
      collapsed_sections: [],
      graph_layout: {},
      section_notes: {},
    },
    entry_node_key: "intake",
    join_policies: [],
    nodes: [],
    prompt_profile_references: [],
    roles: [],
    subworkflow_refs: [],
    test_requirements: [],
    workflow_key: normalized.workflowKey,
    workflow_kind: "main_workflow",
  };
}

export function buildGenericBlueprintDocument(
  current: WorkflowEditorDocument,
  intake: WorkflowScenarioIntake,
): WorkflowEditorDocument {
  const normalized = intakeWithDerivedKey(intake);
  const roleKeys = buildRoleKeys(normalized.agentCount);
  const roles = roleKeys.map((roleKey, index) =>
    roleForScenario(roleKey, index, roleKeys.length, normalized),
  );
  const contracts = scenarioContracts(normalized);
  const promptProfileReferences = roleKeys.flatMap((roleKey) => [
    promptReference(roleKey),
    profileReference(roleKey),
  ]);
  const nodes = scenarioNodes(roleKeys, normalized);
  const edges = scenarioEdges(roleKeys, normalized);
  const joinPolicies = scenarioJoinPolicies(roleKeys, normalized);
  const approvalGates =
    normalized.approvalNeeds.trim().toLowerCase().startsWith("no approval")
      ? []
      : [
          {
            approval_gate_key: "operator-approval",
            approver_scope: "tenant_admin",
            decision_contract_key: "approval-decision",
            display_name: "Operator approval",
            instructions: normalized.approvalNeeds,
            reason: "Configured during generic workflow onboarding.",
            resume_behavior: "resume_same_bundle",
          },
        ];

  return {
    ...current,
    approval_gates: approvalGates,
    contracts,
    description: normalized.purpose,
    display_name: normalized.workflowName,
    edges,
    editor_annotations: {
      ...current.editor_annotations,
      graph_layout: Object.fromEntries(
        nodes.map((node, index) => [
          node.node_key,
          node.editor_position ?? { x: index * 220, y: 120 },
        ]),
      ),
      section_notes: {
        ...current.editor_annotations.section_notes,
        onboarding: `Scenario: ${safeCompactText(normalized.purpose)}`,
      },
    },
    entry_node_key: "intake",
    join_policies: joinPolicies,
    nodes,
    prompt_profile_references: promptProfileReferences,
    roles,
    workflow_key: normalized.workflowKey,
    workflow_kind: "main_workflow",
  };
}

export function attachWorkflowEvidenceRequirement(
  document: WorkflowEditorDocument,
  suiteId: string,
): WorkflowEditorDocument {
  const requirement = {
    freshness_policy: "latest_revision",
    latest_result_id: null,
    latest_result_status: "pending",
    requirement_key: "onboarding-required-evidence",
    safe_summary: "Required deterministic evidence is configured for publish gates.",
    suite_id: suiteId,
    target_type: "workflow_draft",
  };
  return {
    ...document,
    test_requirements: [
      requirement,
      ...document.test_requirements.filter(
        (item) => item.requirement_key !== requirement.requirement_key,
      ),
    ],
  };
}

export function buildThreeAgentStarterDocument(
  current: WorkflowEditorDocument,
): WorkflowEditorDocument {
  const contracts = starterContracts();
  const promptProfiles = starterPromptProfiles();
  const roles = starterRoles();
  const nodes = starterNodes();
  const joinPolicies = starterJoinPolicies();
  return {
    ...current,
    contracts,
    editor_annotations: {
      ...current.editor_annotations,
      graph_layout: {
        intake: { x: 0, y: 120 },
        research: { x: 260, y: 20 },
        synthesis: { x: 260, y: 220 },
        review: { x: 540, y: 120 },
        publish: { x: 800, y: 120 },
      },
      section_notes: {
        ...current.editor_annotations.section_notes,
        setup: "Three-agent setup template applied from the guided workflow setup.",
      },
    },
    edges: [
      {
        branch_condition: "fan-out",
        contract_key: "workflow-request",
        edge_key: "edge-intake-research",
        edge_type: "parallel",
        source_node_key: "intake",
        target_node_key: "research",
      },
      {
        branch_condition: "fan-out",
        contract_key: "workflow-request",
        edge_key: "edge-intake-synthesis",
        edge_type: "parallel",
        source_node_key: "intake",
        target_node_key: "synthesis",
      },
      {
        branch_condition: "required",
        contract_key: "analysis-brief",
        edge_key: "edge-research-review",
        edge_type: "join",
        source_node_key: "research",
        target_node_key: "review",
      },
      {
        branch_condition: "required",
        contract_key: "analysis-brief",
        edge_key: "edge-synthesis-review",
        edge_type: "join",
        source_node_key: "synthesis",
        target_node_key: "review",
      },
      {
        branch_condition: "complete",
        contract_key: "workflow-result",
        edge_key: "edge-review-publish",
        edge_type: "success",
        source_node_key: "review",
        target_node_key: "publish",
      },
    ],
    entry_node_key: "intake",
    join_policies: joinPolicies,
    nodes,
    prompt_profile_references: promptProfiles,
    roles,
  };
}

function buildRoleKeys(agentCount: number): string[] {
  if (agentCount <= 1) {
    return ["coordinator"];
  }
  if (agentCount === 2) {
    return ["intake", "delivery"];
  }
  const middleCount = agentCount - 2;
  return [
    "intake",
    ...Array.from({ length: middleCount }, (_, index) => `workstream-${index + 1}`),
    "synthesis",
  ];
}

function roleForScenario(
  roleKey: string,
  index: number,
  total: number,
  intake: WorkflowScenarioIntake,
): WorkflowRoleItem {
  const isFirst = index === 0;
  const isLast = index === total - 1;
  const displayName = isFirst
    ? "Intake coordinator"
    : isLast
      ? "Synthesis lead"
      : `Workstream ${index}`;
  return {
    display_name: displayName,
    graph_node_keys: [roleKey],
    input_contract_key: isFirst ? "scenario-request" : "scenario-handoff",
    output_contract_key: isLast ? "scenario-result" : "scenario-handoff",
    profile_reference_key: `${roleKey}-profile`,
    prompt_reference_keys: [`${roleKey}-prompt`],
    purpose: isFirst
      ? `Frame incoming ${triggerLabel(intake.triggerMode)} requests for ${intake.workflowName}.`
      : isLast
        ? `Produce the final ${safeCompactText(intake.desiredOutputs)}.`
        : `Handle a bounded workstream for ${safeCompactText(intake.purpose)}.`,
    responsibilities: isFirst
      ? ["Check launch context", "Prepare structured handoff"]
      : isLast
        ? ["Merge branch evidence", "Prepare safe result"]
        : ["Review assigned input", "Return concise evidence"],
    role_key: roleKey,
    role_kind: "agent",
    skill_installation_keys: [],
  };
}

function scenarioContracts(intake: WorkflowScenarioIntake): WorkflowContractItem[] {
  const contracts: WorkflowContractItem[] = [
    {
      contract_key: "scenario-request",
      contract_kind: "workflow_input",
      display_name: "Scenario request",
      json_schema: {
        properties: {
          request: { description: safeCompactText(intake.expectedInputs), type: "string" },
        },
        required: ["request"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
    {
      contract_key: "scenario-handoff",
      contract_kind: "handoff",
      display_name: "Scenario handoff",
      json_schema: {
        properties: {
          safe_summary: { type: "string" },
          evidence_notes: { type: "array", items: { type: "string" } },
        },
        required: ["safe_summary"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
    {
      contract_key: "scenario-result",
      contract_kind: "workflow_output",
      display_name: "Scenario result",
      json_schema: {
        properties: {
          result: { description: safeCompactText(intake.desiredOutputs), type: "string" },
          status: { type: "string" },
        },
        required: ["result", "status"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
  ];
  if (!intake.approvalNeeds.trim().toLowerCase().startsWith("no approval")) {
    contracts.push({
      contract_key: "approval-decision",
      contract_kind: "approval_decision",
      display_name: "Approval decision",
      json_schema: {
        properties: {
          approved: { type: "boolean" },
          safe_reason: { type: "string" },
        },
        required: ["approved"],
        type: "object",
      },
      semantic_version: "1.0.0",
    });
  }
  return contracts;
}

function scenarioNodes(
  roleKeys: string[],
  intake: WorkflowScenarioIntake,
): WorkflowNodeItem[] {
  const roleNodes = roleKeys.map((roleKey, index) => ({
    active: true,
    display_name: readableFromKey(roleKey),
    editor_position:
      intake.coordinationPattern === "parallel_review"
        ? { x: index === 0 ? 0 : 260, y: index === 0 ? 140 : index * 92 }
        : { x: index * 220, y: 140 },
    node_key: roleKey,
    node_type: "role",
    role_key: roleKey,
  }));
  const terminal: WorkflowNodeItem = {
    active: true,
    display_name: "Ready result",
    editor_position: { x: 760, y: 140 },
    node_key: "result",
    node_type: "terminal",
  };
  if (intake.coordinationPattern === "parallel_review" && roleKeys.length > 2) {
    return [
      ...roleNodes,
      {
        active: true,
        display_name: "Review join",
        editor_position: { x: 560, y: 140 },
        join_policy_key: "scenario-review-join",
        node_key: "review-join",
        node_type: "join",
      },
      terminal,
    ];
  }
  return [...roleNodes, terminal];
}

function scenarioEdges(
  roleKeys: string[],
  intake: WorkflowScenarioIntake,
): WorkflowEditorDocument["edges"] {
  if (roleKeys.length <= 1) {
    return [
      {
        branch_condition: "complete",
        contract_key: "scenario-result",
        edge_key: "edge-coordinator-result",
        edge_type: "success",
        source_node_key: roleKeys[0] ?? "coordinator",
        target_node_key: "result",
      },
    ];
  }
  if (intake.coordinationPattern === "parallel_review" && roleKeys.length > 2) {
    const first = roleKeys[0];
    const branches = roleKeys.slice(1, -1);
    const finalRole = roleKeys.at(-1) ?? "synthesis";
    return [
      ...branches.map((roleKey) => ({
        branch_condition: "fan-out",
        contract_key: "scenario-request",
        edge_key: `edge-${first}-${roleKey}`,
        edge_type: "parallel",
        source_node_key: first,
        target_node_key: roleKey,
      })),
      ...branches.map((roleKey) => ({
        branch_condition: "required",
        contract_key: "scenario-handoff",
        edge_key: `edge-${roleKey}-join`,
        edge_type: "join",
        source_node_key: roleKey,
        target_node_key: "review-join",
      })),
      {
        branch_condition: "merge",
        contract_key: "scenario-handoff",
        edge_key: "edge-join-synthesis",
        edge_type: "success",
        source_node_key: "review-join",
        target_node_key: finalRole,
      },
      {
        branch_condition: "complete",
        contract_key: "scenario-result",
        edge_key: "edge-synthesis-result",
        edge_type: "success",
        source_node_key: finalRole,
        target_node_key: "result",
      },
    ];
  }
  return [
    ...roleKeys.slice(0, -1).map((roleKey, index) => ({
      branch_condition: "handoff",
      contract_key: "scenario-handoff",
      edge_key: `edge-${roleKey}-${roleKeys[index + 1]}`,
      edge_type: "success",
      source_node_key: roleKey,
      target_node_key: roleKeys[index + 1],
    })),
    {
      branch_condition: "complete",
      contract_key: "scenario-result",
      edge_key: `edge-${roleKeys.at(-1) ?? "delivery"}-result`,
      edge_type: "success",
      source_node_key: roleKeys.at(-1) ?? "delivery",
      target_node_key: "result",
    },
  ];
}

function scenarioJoinPolicies(
  roleKeys: string[],
  intake: WorkflowScenarioIntake,
): WorkflowJoinPolicyItem[] {
  if (intake.coordinationPattern !== "parallel_review" || roleKeys.length <= 2) {
    return [];
  }
  const branches = roleKeys.slice(1, -1);
  return [
    {
      failure_behavior: "block",
      inbound_edge_keys: branches.map((roleKey) => `edge-${roleKey}-join`),
      join_policy_key: "scenario-review-join",
      output_merge_contract_key: "scenario-result",
      quorum_count: null,
      required_branches: branches,
      strategy: "all_success",
      timeout_seconds: null,
    },
  ];
}

function promptReference(roleKey: string): WorkflowPromptProfileReferenceItem {
  return {
    agent_kind: "agent",
    agent_key: roleKey,
    prompt_reference_version_ids: [],
    prompt_version_ids: [],
    readiness_status: "ready",
    reference_key: `${roleKey}-prompt`,
    resolution_digest: `prompt:${roleKey}`,
    role_key: roleKey,
    source_scope: "tenant",
  };
}

function profileReference(roleKey: string): WorkflowPromptProfileReferenceItem {
  return {
    agent_kind: "agent",
    agent_key: roleKey,
    agent_profile_version_id: null,
    prompt_reference_version_ids: [],
    prompt_version_ids: [],
    readiness_status: "ready",
    reference_key: `${roleKey}-profile`,
    resolution_digest: `profile:${roleKey}`,
    role_key: roleKey,
    source_scope: "tenant",
  };
}

function triggerLabel(triggerMode: WorkflowScenarioIntake["triggerMode"]): string {
  return triggerMode === "channel_or_api" ? "channel or API" : "manual launch";
}

function readableFromKey(value: string): string {
  return value
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function safeCompactText(value: string): string {
  const compact = value.replace(/\s+/g, " ").trim();
  return compact.length > 120 ? `${compact.slice(0, 117)}...` : compact;
}

function starterContracts(): WorkflowContractItem[] {
  return [
    {
      contract_key: "workflow-request",
      contract_kind: "workflow_input",
      display_name: "Workflow request",
      json_schema: {
        properties: { text: { type: "string" } },
        required: ["text"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
    {
      contract_key: "analysis-brief",
      contract_kind: "handoff",
      display_name: "Analysis brief",
      json_schema: {
        properties: { safe_summary: { type: "string" } },
        required: ["safe_summary"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
    {
      contract_key: "workflow-result",
      contract_kind: "workflow_output",
      display_name: "Workflow result",
      json_schema: {
        properties: { status: { type: "string" } },
        required: ["status"],
        type: "object",
      },
      semantic_version: "1.0.0",
    },
  ];
}

function starterPromptProfiles(): WorkflowPromptProfileReferenceItem[] {
  return ["intake", "research", "synthesis"].flatMap((roleKey) => [
    {
      agent_kind: "agent",
      agent_key: roleKey,
      prompt_reference_version_ids: [],
      prompt_version_ids: [],
      readiness_status: "ready",
      reference_key: `${roleKey}-prompt`,
      resolution_digest: `prompt:${roleKey}`,
      role_key: roleKey,
      source_scope: "tenant",
    },
    {
      agent_kind: "agent",
      agent_key: roleKey,
      agent_profile_version_id: null,
      prompt_reference_version_ids: [],
      prompt_version_ids: [],
      readiness_status: "ready",
      reference_key: `${roleKey}-profile`,
      resolution_digest: `profile:${roleKey}`,
      role_key: roleKey,
      source_scope: "tenant",
    },
  ]);
}

function starterRoles(): WorkflowRoleItem[] {
  return [
    {
      display_name: "Intake coordinator",
      graph_node_keys: ["intake"],
      input_contract_key: "workflow-request",
      output_contract_key: "analysis-brief",
      profile_reference_key: "intake-profile",
      prompt_reference_keys: ["intake-prompt"],
      purpose: "Frame the workflow request and delegate safe analysis branches.",
      responsibilities: ["Classify the request", "Route branch work"],
      role_key: "intake",
      role_kind: "agent",
      skill_installation_keys: [],
    },
    {
      display_name: "Research agent",
      graph_node_keys: ["research"],
      input_contract_key: "workflow-request",
      output_contract_key: "analysis-brief",
      profile_reference_key: "research-profile",
      prompt_reference_keys: ["research-prompt"],
      purpose: "Collect safe facts and produce a concise evidence brief.",
      responsibilities: ["Check safe sources", "Summarize findings"],
      role_key: "research",
      role_kind: "agent",
      skill_installation_keys: [],
    },
    {
      display_name: "Synthesis agent",
      graph_node_keys: ["synthesis"],
      input_contract_key: "workflow-request",
      output_contract_key: "analysis-brief",
      profile_reference_key: "synthesis-profile",
      prompt_reference_keys: ["synthesis-prompt"],
      purpose: "Combine branch evidence into a publishable answer.",
      responsibilities: ["Merge branch context", "Prepare final response"],
      role_key: "synthesis",
      role_kind: "agent",
      skill_installation_keys: [],
    },
  ];
}

function starterNodes(): WorkflowNodeItem[] {
  return [
    {
      active: true,
      display_name: "Intake coordinator",
      editor_position: { x: 0, y: 120 },
      node_key: "intake",
      node_type: "role",
      role_key: "intake",
    },
    {
      active: true,
      display_name: "Research branch",
      editor_position: { x: 260, y: 20 },
      node_key: "research",
      node_type: "role",
      role_key: "research",
    },
    {
      active: true,
      display_name: "Synthesis branch",
      editor_position: { x: 260, y: 220 },
      node_key: "synthesis",
      node_type: "role",
      role_key: "synthesis",
    },
    {
      active: true,
      display_name: "Review join",
      editor_position: { x: 540, y: 120 },
      join_policy_key: "review-join",
      node_key: "review",
      node_type: "join",
    },
    {
      active: true,
      display_name: "Publish result",
      editor_position: { x: 800, y: 120 },
      node_key: "publish",
      node_type: "terminal",
    },
  ];
}

function starterJoinPolicies(): WorkflowJoinPolicyItem[] {
  return [
    {
      failure_behavior: "block",
      inbound_edge_keys: ["edge-research-review", "edge-synthesis-review"],
      join_policy_key: "review-join",
      output_merge_contract_key: "workflow-result",
      quorum_count: null,
      required_branches: ["research", "synthesis"],
      strategy: "all_success",
      timeout_seconds: null,
    },
  ];
}
