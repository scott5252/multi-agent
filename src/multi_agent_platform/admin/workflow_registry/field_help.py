from __future__ import annotations

from multi_agent_platform.api.schemas.workflow_editor import (
    EditorOption,
    FieldHelpDefinition,
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
}

SECTION_ORDER = [
    "Overview",
    "Roles And Skills",
    "Contracts",
    "Nodes And Flow",
    "Subworkflow References",
    "Join Policies",
    "Approval Gates",
    "Validation And Publish",
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
    )
