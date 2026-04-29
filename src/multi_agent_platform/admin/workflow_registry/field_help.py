from __future__ import annotations

from multi_agent_platform.api.schemas.workflow_editor import (
    EditorActionUrls,
    EditorCapability,
    EditorFieldDefinition,
    EditorOption,
    EditorSectionDefinition,
    FieldHelpDefinition,
    ValidationCodeMapping,
    WorkflowEditorMetadataResponse,
)

FIELD_HELP: dict[str, FieldHelpDefinition] = {
    "scope_type": FieldHelpDefinition(
        field_key="scope_type",
        label="Scope",
        title="Workflow Scope",
        explanation=(
            "Choose whether this draft belongs to one tenant or becomes a "
            "platform-scoped reusable asset."
        ),
        runtime_impact=(
            "Scope controls who can see and edit the workflow and whether "
            "later sharing grants are required."
        ),
        example=(
            "Tenant scope for customer-specific automations, platform scope "
            "for reusable templates."
        ),
    ),
    "display_name": FieldHelpDefinition(
        field_key="display_name",
        label="Display Name",
        title="Workflow Display Name",
        explanation=(
            "Use a clear name that operators can recognize in the registry list."
        ),
        runtime_impact=(
            "The display name appears in the registry and draft editor, so it "
            "helps reviewers distinguish similar drafts."
        ),
        example="Customer Intake Triage",
    ),
    "workflow_kind": FieldHelpDefinition(
        field_key="workflow_kind",
        label="Workflow Kind",
        title="Workflow Kind",
        explanation=(
            "Choose a main workflow for an end-to-end orchestration or a "
            "subworkflow for a reusable nested flow."
        ),
        runtime_impact=(
            "Workflow kind influences how future validation and publish flows "
            "treat the asset."
        ),
        example="Use subworkflow for a reusable document-extraction block.",
    ),
    "roles[].input_contract_key": FieldHelpDefinition(
        field_key="roles[].input_contract_key",
        label="Role Input Contract",
        title="Role Input Contract",
        explanation=(
            "Reference the contract the role expects to receive before it runs."
        ),
        runtime_impact=(
            "Contract wiring is how later validation detects mismatched data "
            "between nodes and roles."
        ),
        example="customer_profile_v1",
    ),
    "roles[].output_contract_key": FieldHelpDefinition(
        field_key="roles[].output_contract_key",
        label="Role Output Contract",
        title="Role Output Contract",
        explanation=(
            "Reference the contract the role promises to emit for downstream nodes."
        ),
        runtime_impact=(
            "Stable output contracts keep downstream consumers predictable and "
            "reviewable."
        ),
        example="triage_decision_v1",
    ),
    "roles[].skill_bindings[].skill_slug": FieldHelpDefinition(
        field_key="roles[].skill_bindings[].skill_slug",
        label="Skill Slug",
        title="Skill Slug",
        explanation="Point the role at the named skill capability it needs.",
        runtime_impact=(
            "Later publish steps will pin the exact skill version behind this "
            "authored slug."
        ),
        example="doc-extractor",
    ),
    "roles[].skill_bindings[].skill_version": FieldHelpDefinition(
        field_key="roles[].skill_bindings[].skill_version",
        label="Skill Version",
        title="Exact Skill Version",
        explanation=(
            "Record the intended skill version instead of a floating alias so "
            "later publish output stays deterministic."
        ),
        runtime_impact=(
            "Exact versions reduce drift between what was reviewed and what "
            "later executes."
        ),
        example="2026.04.1",
    ),
    "subworkflow_refs[].workflow_version_ref": FieldHelpDefinition(
        field_key="subworkflow_refs[].workflow_version_ref",
        label="Subworkflow Version",
        title="Subworkflow Version Reference",
        explanation="Reference a published subworkflow version, not an editable draft.",
        runtime_impact=(
            "Published version references keep nested workflow dependencies "
            "immutable and traceable."
        ),
        example="document-extraction@v3",
    ),
    "join_policies[].strategy": FieldHelpDefinition(
        field_key="join_policies[].strategy",
        label="Join Strategy",
        title="Join Policy Strategy",
        explanation=(
            "Describe how multiple branches rejoin before the workflow continues."
        ),
        runtime_impact=(
            "Join strategy determines whether the future runtime waits for all "
            "branches, a quorum, or a single winner."
        ),
        example="all_success",
        validation_hint="Use quorum only when you also provide the quorum count.",
    ),
    "approval_gates[].approver_scope": FieldHelpDefinition(
        field_key="approval_gates[].approver_scope",
        label="Approver Scope",
        title="Approval Scope",
        explanation="Describe who is allowed to approve this gate at design time.",
        runtime_impact=(
            "Approval metadata becomes durable runtime wait-state configuration later."
        ),
        example="tenant_admin",
    ),
    "prompt_profile_references[].readiness_status": FieldHelpDefinition(
        field_key="prompt_profile_references[].readiness_status",
        label="Prompt/Profile Readiness",
        title="Prompt And Runtime Profile Readiness",
        explanation=(
            "Shows whether selected prompt and runtime profile versions are active, "
            "authorized, and digest-compatible."
        ),
        runtime_impact=(
            "Publication is blocked until every required role has ready prompt and "
            "profile evidence."
        ),
        example="ready",
    ),
    "skill_installations[].skill_version": FieldHelpDefinition(
        field_key="skill_installations[].skill_version",
        label="Installed Skill Version",
        title="Installed Skill Version",
        explanation="Pin an installed skill by exact version for this workflow.",
        runtime_impact=(
            "The publish gate stores exact skill pins so runtime execution uses the "
            "reviewed capability."
        ),
        example="2026.04.1",
    ),
    "nodes[].node_key": FieldHelpDefinition(
        field_key="nodes[].node_key",
        label="Graph Node",
        title="Graph Node Key",
        explanation=(
            "A stable semantic node key used by graph preview and runtime wiring."
        ),
        runtime_impact="Validation findings and audit summaries use this stable key.",
        example="triage-node",
    ),
    "edges[].edge_key": FieldHelpDefinition(
        field_key="edges[].edge_key",
        label="Graph Edge",
        title="Graph Edge Key",
        explanation="A stable semantic edge key between two workflow nodes.",
        runtime_impact="Graph validation maps edge findings back to this key.",
        example="triage-to-approval",
    ),
    "test_requirements[].latest_result_status": FieldHelpDefinition(
        field_key="test_requirements[].latest_result_status",
        label="Required Test Result",
        title="Required Test Result",
        explanation=(
            "The latest safe status for a required workflow or profile test suite."
        ),
        runtime_impact=("Missing, stale, or failing required tests block publication."),
        example="passed",
    ),
}

SECTION_ORDER = [
    "Overview",
    "Roles And Skills",
    "Contracts",
    "Prompt And Runtime Profile References",
    "Model Routing Preview",
    "Skill Installations",
    "Graph Builder",
    "Join Policies",
    "Approval Gates",
    "Reusable Subworkflows",
    "Test Requirements",
    "Validation And Publish",
    "Revision History",
]

SECTIONS = [
    EditorSectionDefinition(
        section_key="overview",
        label="Overview",
        description="Scope, name, owner, tags, and publication intent.",
        field_paths=[
            "metadata.scope_type",
            "workflow_kind",
            "workflow_key",
            "display_name",
            "description",
        ],
    ),
    EditorSectionDefinition(
        section_key="roles",
        label="Roles And Sub-Agent Roles",
        description="Agent and sub-agent responsibilities, contracts, and skills.",
        field_paths=[
            "roles[].role_key",
            "roles[].input_contract_key",
            "roles[].output_contract_key",
        ],
    ),
    EditorSectionDefinition(
        section_key="prompt_profile_references",
        label="Prompt And Runtime Profile References",
        description="Prompt/profile governance references and readiness evidence.",
        field_paths=["prompt_profile_references[].readiness_status"],
    ),
    EditorSectionDefinition(
        section_key="model_routing",
        label="Model Routing Preview",
        description="Safe routing preview links and provider readiness summaries.",
        field_paths=["prompt_profile_references[].model_routing_preview"],
    ),
    EditorSectionDefinition(
        section_key="skills",
        label="Skill Installations",
        description="Exact skill pins, policies, and credential readiness.",
        field_paths=["skill_installations[].skill_version"],
    ),
    EditorSectionDefinition(
        section_key="contracts",
        label="Contracts",
        description="Workflow, handoff, approval, memory, and failure contracts.",
        field_paths=["contracts[].json_schema"],
    ),
    EditorSectionDefinition(
        section_key="graph",
        label="Graph Builder",
        description="Server-derived nodes, edges, terminal paths, and graph policy.",
        field_paths=["nodes[].node_key", "edges[].edge_key"],
    ),
    EditorSectionDefinition(
        section_key="joins",
        label="Join Policies",
        description="Branch merge strategy, quorum, timeout, and merge contracts.",
        field_paths=["join_policies[].strategy"],
    ),
    EditorSectionDefinition(
        section_key="approvals",
        label="Approval Gates",
        description="Approver scope, decision contracts, timeout, and resume behavior.",
        field_paths=["approval_gates[].approver_scope"],
    ),
    EditorSectionDefinition(
        section_key="subworkflows",
        label="Reusable Subworkflows",
        description="Pinned subworkflow bundle references and compatibility status.",
        field_paths=["subworkflow_refs[].workflow_version_ref"],
    ),
    EditorSectionDefinition(
        section_key="tests",
        label="Test Requirements",
        description="Required suite evidence and freshness status.",
        field_paths=["test_requirements[].latest_result_status"],
    ),
    EditorSectionDefinition(
        section_key="validation_publish",
        label="Validation And Publish",
        description="Field findings, publish gate status, and confirmation state.",
        field_paths=["validation"],
    ),
    EditorSectionDefinition(
        section_key="revision_history",
        label="Revision History",
        description="Safe revision summaries, copy, restore, and lineage links.",
        field_paths=["revisions"],
    ),
]


def _lookup_source_for_field(field_path: str) -> str | None:
    if "prompt_profile_references" in field_path:
        return "profiles"
    if "skill_installations" in field_path:
        return "skills"
    if "contract" in field_path:
        return "contracts"
    if "subworkflow_refs" in field_path:
        return "subworkflows"
    if "test_requirements" in field_path:
        return "test_suites"
    return None


FIELDS = [
    EditorFieldDefinition(
        field_path=field_path,
        label=FIELD_HELP.get(field_path, FIELD_HELP["display_name"]).label,
        section_key=section.section_key,
        required=not field_path.endswith("reviewer_notes"),
        lookup_source=_lookup_source_for_field(field_path),
        help_key=field_path if field_path in FIELD_HELP else None,
    )
    for section in SECTIONS
    for field_path in section.field_paths
]

VALIDATION_CODES = [
    ValidationCodeMapping(
        code="graph.node.disconnected",
        section_key="graph",
        field_path_template="nodes[]",
        remediation="Connect the node to the entry path or mark it inactive.",
    ),
    ValidationCodeMapping(
        code="reference.prompt_profile.not_ready",
        section_key="prompt_profile_references",
        field_path_template="prompt_profile_references[].readiness_status",
        remediation="Select an active profile and prompt versions.",
    ),
    ValidationCodeMapping(
        code="reference.skill.not_ready",
        section_key="skills",
        field_path_template="skill_installations[].skill_version",
        remediation="Pin an installed skill with ready credential references.",
    ),
    ValidationCodeMapping(
        code="reference.required_test.not_passing",
        section_key="tests",
        field_path_template="test_requirements[].latest_result_status",
        remediation="Attach a current passing test result.",
    ),
]


def build_editor_metadata() -> WorkflowEditorMetadataResponse:
    return WorkflowEditorMetadataResponse(
        field_help=FIELD_HELP,
        scope_options=[
            EditorOption(value="tenant", label="Tenant"),
            EditorOption(value="platform", label="Platform"),
        ],
        workflow_kind_options=[
            EditorOption(value="main_workflow", label="Main Workflow"),
            EditorOption(value="subworkflow", label="Subworkflow"),
        ],
        section_order=SECTION_ORDER,
        sections=SECTIONS,
        fields=FIELDS,
        lookup_sources={
            "profiles": "/admin/workflows/editor-lookups?lookup_kind=profiles",
            "skills": "/admin/workflows/editor-lookups?lookup_kind=skills",
            "contracts": "/admin/workflows/editor-lookups?lookup_kind=contracts",
            "subworkflows": "/admin/workflows/editor-lookups?lookup_kind=subworkflows",
            "test_suites": "/admin/workflows/editor-lookups?lookup_kind=test_suites",
        },
        capabilities=[
            EditorCapability(capability_key="create_draft", allowed=True),
            EditorCapability(capability_key="save_draft", allowed=True),
            EditorCapability(capability_key="validate", allowed=True),
            EditorCapability(capability_key="publish_gate", allowed=True),
            EditorCapability(capability_key="restore_revision", allowed=True),
            EditorCapability(capability_key="copy_draft", allowed=True),
        ],
        action_urls=EditorActionUrls(),
        validation_codes=VALIDATION_CODES,
    )
