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
