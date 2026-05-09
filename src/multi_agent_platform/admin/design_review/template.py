from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.design_review.redaction import (
    UnsafeDesignReviewContentError,
    validate_safe_text,
)
from multi_agent_platform.admin.design_review.service import (
    DesignReviewAccessError,
    DesignReviewConflictError,
    DesignReviewValidationError,
)
from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
    WorkflowRegistryError,
    WorkflowRegistryService,
)
from multi_agent_platform.api.schemas.workflow_editor import PublishGateRequest
from multi_agent_platform.api.schemas.workflow_registry import (
    AgentRoleDefinition,
    ContractSchemaDefinition,
    JoinPolicyDefinition,
    RoleKind,
    TestSuiteRequirement,
    WorkflowBuilderMetadata,
    WorkflowContractKind,
    WorkflowDraftCreateRequest,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowDraftSaveRequest,
    WorkflowEdgeDefinition,
    WorkflowKind,
    WorkflowNodeDefinition,
    WorkflowNodeType,
    WorkflowScopeType,
)
from multi_agent_platform.api.ui.admin_console import is_platform_admin
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.agent_tests import (
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestSuite,
    AgentTestTargetType,
)
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowDraftRecord,
    WorkflowRegistryRepository,
)
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.testing.agent_bench.service import (
    AgentTestBenchError,
    AgentTestBenchService,
)

COUNCIL_TEMPLATE_KEY = "design-reviewer-council"
COUNCIL_TEMPLATE_DISPLAY_NAME = "Design Reviewer Council"
COUNCIL_REQUIRED_SUITE_NAME = "Design Reviewer Council Required Evidence"
COUNCIL_REQUIREMENT_KEY = "design-reviewer-council-required-evidence"
WORKFLOW_TARGET_TYPE = "workflow_draft"
SafeEvidenceMode = Literal["deterministic", "model_backed_safe", "both"]


@dataclass(frozen=True)
class DesignReviewTemplateState:
    status: str
    template_key: str
    publish_gate_status: str
    safe_summary: str
    workflow_draft_id: UUID | None = None
    workflow_lineage_id: UUID | None = None
    workflow_draft_revision_id: UUID | None = None
    workflow_key: str | None = None
    display_name: str | None = None
    agent_test_suite_id: UUID | None = None
    latest_run_id: UUID | None = None
    deterministic_run_id: UUID | None = None
    model_safe_run_id: UUID | None = None
    required_evidence_status: str = "missing"
    evidence_modes: tuple[str, ...] = ()
    ready_to_publish: bool = False


@dataclass(frozen=True)
class DesignReviewTemplateInstallResult:
    state: DesignReviewTemplateState
    replayed: bool


class DesignReviewTemplateService:
    def __init__(
        self,
        *,
        workflow_service: WorkflowRegistryService,
        agent_service: AgentTestBenchService,
        agent_repository: AgentTestRepository,
    ) -> None:
        self.workflow_service = workflow_service
        self.agent_service = agent_service
        self.agent_repository = agent_repository

    async def install_council_template(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        idempotency_key: str,
        template_key: str = COUNCIL_TEMPLATE_KEY,
        run_required_tests: bool = True,
        safe_mode: SafeEvidenceMode = "both",
    ) -> DesignReviewTemplateInstallResult:
        self._ensure_tenant_admin(principal, tenant_id)
        safe_template_key = self._safe_key(template_key, field_name="template_key")
        safe_idempotency_key = self._safe_key(
            idempotency_key,
            field_name="idempotency_key",
        )
        draft, replayed = await self._get_or_create_draft(
            principal=principal,
            tenant_id=tenant_id,
            template_key=safe_template_key,
        )
        suite = await self._ensure_required_suite(
            tenant_id=tenant_id,
            workflow_draft_id=draft.workflow_draft_id,
            actor_principal_id=principal.principal_id,
        )
        await self._ensure_publication_requirement(
            tenant_id=tenant_id,
            workflow_draft_id=draft.workflow_draft_id,
            suite=suite,
            actor_principal_id=principal.principal_id,
        )
        draft = await self._ensure_draft_requires_suite(
            principal=principal,
            draft=draft,
            suite=suite,
        )
        current_target_version = str(draft.latest_revision.workflow_draft_revision_id)
        if run_required_tests:
            await self._ensure_current_evidence(
                tenant_id=tenant_id,
                suite=suite,
                target_version=current_target_version,
                actor_principal_id=principal.principal_id,
                trace_id=principal.trace_id,
                safe_idempotency_key=safe_idempotency_key,
                safe_mode=safe_mode,
            )
        try:
            validation = await self.workflow_service.validate_draft(
                principal=principal,
                workflow_draft_id=draft.workflow_draft_id,
            )
            gate = await self.workflow_service.evaluate_publish_gate(
                principal=principal,
                workflow_draft_id=draft.workflow_draft_id,
                payload=PublishGateRequest(
                    validation_result_id=str(validation.validation_result_id),
                ),
            )
        except WorkflowRegistryError as exc:
            raise DesignReviewConflictError(str(exc)) from exc
        state = await self.get_council_template_state(
            principal=principal,
            tenant_id=tenant_id,
            template_key=safe_template_key,
        )
        if gate.status == "ready" and state.status != "ready":
            state = DesignReviewTemplateState(
                **{
                    **state.__dict__,
                    "status": "ready",
                    "publish_gate_status": gate.status,
                    "ready_to_publish": True,
                    "safe_summary": "Council template has current required evidence.",
                }
            )
        return DesignReviewTemplateInstallResult(
            state=state,
            replayed=replayed,
        )

    async def get_council_template_state(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        template_key: str = COUNCIL_TEMPLATE_KEY,
    ) -> DesignReviewTemplateState:
        self._ensure_tenant_admin(principal, tenant_id)
        safe_template_key = self._safe_key(template_key, field_name="template_key")
        record = await self._find_template_draft_record(
            tenant_id=tenant_id,
            template_key=safe_template_key,
        )
        if record is None:
            return DesignReviewTemplateState(
                status="not_installed",
                template_key=safe_template_key,
                publish_gate_status="not_evaluated",
                safe_summary="Council template is not installed for this tenant.",
            )
        document = WorkflowDraftDocument.model_validate(
            record.revision.authoring_document_json
        )
        suite = await self.agent_repository.find_suite_for_tenant(
            tenant_id=tenant_id,
            target_type=WORKFLOW_TARGET_TYPE,
            target_id=str(record.draft.workflow_draft_id),
            name=COUNCIL_REQUIRED_SUITE_NAME,
        )
        if suite is None:
            return self._state_from_record(
                record=record,
                document=document,
                required_evidence_status="missing",
                publish_gate_status="blocked",
                safe_summary="Council template is installed and waiting for evidence.",
            )
        target_version = str(record.revision.workflow_draft_revision_id)
        latest_current = await self.agent_repository.latest_passing_run_for_suite(
            suite_id=suite.agent_test_suite_id,
            tenant_id=tenant_id,
            target_version=target_version,
        )
        latest_any = await self.agent_repository.latest_run_for_suite(
            suite_id=suite.agent_test_suite_id,
            tenant_id=tenant_id,
            target_type=WORKFLOW_TARGET_TYPE,
            target_id=str(record.draft.workflow_draft_id),
        )
        deterministic = await self._latest_run_for_safe_mode(
            tenant_id=tenant_id,
            suite=suite,
            target_version=target_version,
            safe_mode="mock_model",
        )
        model_safe = await self._latest_run_for_safe_mode(
            tenant_id=tenant_id,
            suite=suite,
            target_version=target_version,
            safe_mode="real_model_side_effects_disabled",
        )
        validation_passed = (
            record.latest_validation is not None
            and record.latest_validation.status.value == "passed"
        )
        if latest_current is not None and validation_passed:
            status_value = "ready"
            evidence_status = "passing"
            gate_status = "ready"
            summary = "Council template has current required evidence."
        elif latest_current is not None:
            status_value = "evidence_pending"
            evidence_status = "passing"
            gate_status = "blocked"
            summary = "Council template evidence is current and validation is pending."
        elif latest_any is not None and latest_any.status is AgentTestRunStatus.PASSED:
            status_value = "stale"
            evidence_status = "stale"
            gate_status = "blocked"
            summary = "Council template needs evidence for the current revision."
        elif latest_any is not None:
            status_value = "evidence_failed"
            evidence_status = "failed"
            gate_status = "blocked"
            summary = "Council template evidence needs attention."
        else:
            status_value = "evidence_pending"
            evidence_status = "missing"
            gate_status = "blocked"
            summary = "Council template is installed and waiting for evidence."
        return self._state_from_record(
            record=record,
            document=document,
            suite=suite,
            latest_run=latest_current or latest_any,
            deterministic_run=deterministic,
            model_safe_run=model_safe,
            required_evidence_status=evidence_status,
            publish_gate_status=gate_status,
            safe_summary=summary,
            status=status_value,
        )

    async def _get_or_create_draft(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        template_key: str,
    ) -> tuple[WorkflowDraftResponse, bool]:
        record = await self._find_template_draft_record(
            tenant_id=tenant_id,
            template_key=template_key,
        )
        if record is not None:
            return (
                await self.workflow_service.get_draft(
                    principal=principal,
                    workflow_draft_id=record.draft.workflow_draft_id,
                ),
                True,
            )
        try:
            created = await self.workflow_service.create_draft(
                principal=principal,
                payload=WorkflowDraftCreateRequest(
                    scope_type=WorkflowScopeType.TENANT,
                    tenant_id=tenant_id,
                    workflow_kind=WorkflowKind.MAIN_WORKFLOW,
                    slug=template_key,
                    display_name=COUNCIL_TEMPLATE_DISPLAY_NAME,
                    description="Reusable council workflow for design review.",
                    document=build_council_template_document(
                        tenant_id=tenant_id,
                        template_key=template_key,
                        owner_principal_id=principal.principal_id,
                    ),
                ),
            )
        except WorkflowAccessError as exc:
            raise DesignReviewAccessError(str(exc)) from exc
        except WorkflowRegistryError as exc:
            raise DesignReviewConflictError(str(exc)) from exc
        return created, False

    async def _find_template_draft_record(
        self,
        *,
        tenant_id: UUID,
        template_key: str,
    ) -> WorkflowDraftRecord | None:
        lineage = await self.workflow_service.repository.get_lineage_by_slug(
            scope_type=WorkflowScopeType.TENANT.value,
            tenant_id=tenant_id,
            slug=template_key,
        )
        if lineage is None:
            return None
        draft = await self.workflow_service.repository.find_active_draft_for_lineage(
            lineage.workflow_lineage_id
        )
        if draft is None:
            return None
        return await self.workflow_service.repository.get_draft_record(
            draft.workflow_draft_id
        )

    async def _ensure_required_suite(
        self,
        *,
        tenant_id: UUID,
        workflow_draft_id: UUID,
        actor_principal_id: str,
    ) -> AgentTestSuite:
        suite = await self.agent_repository.find_suite_for_tenant(
            tenant_id=tenant_id,
            target_type=WORKFLOW_TARGET_TYPE,
            target_id=str(workflow_draft_id),
            name=COUNCIL_REQUIRED_SUITE_NAME,
        )
        if suite is None:
            try:
                suite = await self.agent_service.create_suite(
                    tenant_id=tenant_id,
                    name=COUNCIL_REQUIRED_SUITE_NAME,
                    description="Required safe evidence for council template publish.",
                    target_type=WORKFLOW_TARGET_TYPE,
                    target_id=str(workflow_draft_id),
                    actor_principal_id=actor_principal_id,
                    default_safe_mode="mock_model",
                    model_mode="safe",
                    tool_mode="safe",
                    pass_threshold=1.0,
                    required_for_publish=True,
                )
            except AgentTestBenchError as exc:
                raise DesignReviewConflictError(str(exc)) from exc
        suite.is_required_for_publish = True
        await self._ensure_required_cases(
            tenant_id=tenant_id,
            suite=suite,
            actor_principal_id=actor_principal_id,
        )
        return suite

    async def _ensure_publication_requirement(
        self,
        *,
        tenant_id: UUID,
        workflow_draft_id: UUID,
        suite: AgentTestSuite,
        actor_principal_id: str,
    ) -> None:
        requirements = await self.agent_repository.list_publication_requirements(
            tenant_id=tenant_id,
            target_type=WORKFLOW_TARGET_TYPE,
            target_id=str(workflow_draft_id),
        )
        if any(
            item.agent_test_suite_id == suite.agent_test_suite_id
            for item in requirements
        ):
            return
        await self.agent_repository.add_publication_requirement(
            AgentTestPublicationRequirement(
                tenant_id=tenant_id,
                target_type=AgentTestTargetType(WORKFLOW_TARGET_TYPE),
                target_id=str(workflow_draft_id),
                agent_test_suite_id=suite.agent_test_suite_id,
                created_by_principal_id=actor_principal_id,
            )
        )

    async def _ensure_required_cases(
        self,
        *,
        tenant_id: UUID,
        suite: AgentTestSuite,
        actor_principal_id: str,
    ) -> None:
        existing = {
            case.name
            for case in await self.agent_repository.list_cases_for_suite(
                suite.agent_test_suite_id
            )
        }
        for order, case_name in enumerate(_required_case_names(), start=1):
            if case_name in existing:
                continue
            await self.agent_service.create_case(
                suite_id=suite.agent_test_suite_id,
                tenant_id=tenant_id,
                name=case_name,
                actor_principal_id=actor_principal_id,
                description=f"Safe evidence case for {case_name.lower()}.",
                fixture={"request": case_name},
                expected_contract_shape={"status": {}, "contract": {}},
                assertions=[
                    {
                        "kind": "deterministic",
                        "path": "status",
                        "comparator": "equals",
                        "expected_value": "passed",
                        "severity": "blocking",
                    },
                    {
                        "kind": "deterministic",
                        "path": "latency_ms",
                        "comparator": "latency_under_ms",
                        "threshold": 1000,
                        "severity": "blocking",
                    },
                    {
                        "kind": "deterministic",
                        "path": "usage.total_tokens",
                        "comparator": "usage_under_tokens",
                        "threshold": 500,
                        "severity": "blocking",
                    },
                ],
                case_order=order,
            )

    async def _ensure_draft_requires_suite(
        self,
        *,
        principal: PrincipalContext,
        draft: WorkflowDraftResponse,
        suite: AgentTestSuite,
    ) -> WorkflowDraftResponse:
        requirement = TestSuiteRequirement(
            requirement_key=COUNCIL_REQUIREMENT_KEY,
            suite_id=str(suite.agent_test_suite_id),
            target_type=WORKFLOW_TARGET_TYPE,
            freshness_policy="latest_revision",
            latest_result_status="missing",
        )
        current = draft.document
        existing = [
            item
            for item in current.test_requirements
            if item.requirement_key == COUNCIL_REQUIREMENT_KEY
        ]
        if existing and existing[0].suite_id == str(suite.agent_test_suite_id):
            return draft
        updated_requirements = [
            item
            for item in current.test_requirements
            if item.requirement_key != COUNCIL_REQUIREMENT_KEY
        ]
        updated = current.model_copy(
            update={"test_requirements": [*updated_requirements, requirement]}
        )
        try:
            return await self.workflow_service.save_draft(
                principal=principal,
                workflow_draft_id=draft.workflow_draft_id,
                payload=WorkflowDraftSaveRequest(
                    base_revision_number=draft.current_revision_number,
                    display_name=draft.display_name,
                    description=draft.description,
                    document=updated,
                    change_summary="Attach required council evidence.",
                ),
            )
        except (DraftConflictError, WorkflowNotFoundError) as exc:
            raise DesignReviewConflictError(str(exc)) from exc
        except WorkflowAccessError as exc:
            raise DesignReviewAccessError(str(exc)) from exc

    async def _ensure_current_evidence(
        self,
        *,
        tenant_id: UUID,
        suite: AgentTestSuite,
        target_version: str,
        actor_principal_id: str,
        trace_id: str | None,
        safe_idempotency_key: str,
        safe_mode: SafeEvidenceMode,
    ) -> None:
        modes = {
            "deterministic": ("mock_model",),
            "model_backed_safe": ("real_model_side_effects_disabled",),
            "both": ("mock_model", "real_model_side_effects_disabled"),
        }[safe_mode]
        for mode in modes:
            existing = await self._latest_run_for_safe_mode(
                tenant_id=tenant_id,
                suite=suite,
                target_version=target_version,
                safe_mode=mode,
            )
            if existing is not None and existing.status is AgentTestRunStatus.PASSED:
                continue
            await self.agent_service.launch_run(
                suite_id=suite.agent_test_suite_id,
                tenant_id=tenant_id,
                actor_principal_id=actor_principal_id,
                safe_mode=mode,
                target_version=target_version,
                idempotency_key=(
                    f"design-review-template:{safe_idempotency_key}:"
                    f"{target_version}:{mode}"
                ),
                trace_id=trace_id,
            )

    async def _latest_run_for_safe_mode(
        self,
        *,
        tenant_id: UUID,
        suite: AgentTestSuite,
        target_version: str,
        safe_mode: str,
    ) -> AgentTestRun | None:
        runs = await self.agent_repository.list_runs_for_suite(
            suite_id=suite.agent_test_suite_id,
            tenant_id=tenant_id,
            limit=20,
        )
        for run in runs:
            if (
                run.target_version == target_version
                and run.safe_mode.value == safe_mode
            ):
                return run
        return None

    def _state_from_record(
        self,
        *,
        record: WorkflowDraftRecord,
        document: WorkflowDraftDocument,
        required_evidence_status: str,
        publish_gate_status: str,
        safe_summary: str,
        status: str = "evidence_pending",
        suite: AgentTestSuite | None = None,
        latest_run: AgentTestRun | None = None,
        deterministic_run: AgentTestRun | None = None,
        model_safe_run: AgentTestRun | None = None,
    ) -> DesignReviewTemplateState:
        modes = []
        if deterministic_run is not None:
            modes.append("deterministic")
        if model_safe_run is not None:
            modes.append("model backed safe")
        return DesignReviewTemplateState(
            status=status,
            template_key=document.workflow_key,
            workflow_draft_id=record.draft.workflow_draft_id,
            workflow_lineage_id=record.lineage.workflow_lineage_id,
            workflow_draft_revision_id=record.revision.workflow_draft_revision_id,
            workflow_key=document.workflow_key,
            display_name=document.display_name,
            agent_test_suite_id=suite.agent_test_suite_id if suite else None,
            latest_run_id=latest_run.agent_test_run_id if latest_run else None,
            deterministic_run_id=deterministic_run.agent_test_run_id
            if deterministic_run
            else None,
            model_safe_run_id=model_safe_run.agent_test_run_id
            if model_safe_run
            else None,
            required_evidence_status=required_evidence_status,
            publish_gate_status=publish_gate_status,
            evidence_modes=tuple(modes),
            ready_to_publish=status == "ready",
            safe_summary=safe_summary,
        )

    @staticmethod
    def _ensure_tenant_admin(principal: PrincipalContext, tenant_id: UUID) -> None:
        if is_platform_admin(principal):
            return
        if (
            principal.tenant_id != tenant_id
            or "tenant_admin" not in principal.role_codes
        ):
            raise DesignReviewAccessError("design review template access denied")

    @staticmethod
    def _safe_key(value: str, *, field_name: str) -> str:
        try:
            safe_value = validate_safe_text(value, field_name=field_name)
        except UnsafeDesignReviewContentError as exc:
            raise DesignReviewValidationError(str(exc)) from exc
        if len(safe_value) > 160:
            raise DesignReviewValidationError(f"{field_name} exceeds the key limit")
        return safe_value


def build_design_review_template_service(
    *,
    session: AsyncSession,
    storage_provider: StorageProvider,
    workflow_registry_artifact_prefix: str,
    logger: Logger | None = None,
) -> DesignReviewTemplateService:
    workflow_repository = WorkflowRegistryRepository(session)
    return DesignReviewTemplateService(
        workflow_service=WorkflowRegistryService(
            repository=workflow_repository,
            artifact_repository=ArtifactRepository(session),
            audit_service=AuditService(AuditRepository(session)),
            storage_provider=storage_provider,
            artifact_prefix=workflow_registry_artifact_prefix,
            logger=logger,
        ),
        agent_service=AgentTestBenchService(AgentTestRepository(session)),
        agent_repository=AgentTestRepository(session),
    )


def build_council_template_document(
    *,
    tenant_id: UUID,
    template_key: str = COUNCIL_TEMPLATE_KEY,
    owner_principal_id: str | None = None,
) -> WorkflowDraftDocument:
    reviewer_nodes = [f"reviewer-{index}" for index in range(1, 6)]
    reviewer_edges = [f"edge-reviewer-{index}-quorum" for index in range(1, 6)]
    return WorkflowDraftDocument(
        workflow_key=template_key,
        display_name=COUNCIL_TEMPLATE_DISPLAY_NAME,
        description=(
            "Reusable workflow for design council review, synthesis, and handoff."
        ),
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        metadata=WorkflowBuilderMetadata(
            name=COUNCIL_TEMPLATE_DISPLAY_NAME,
            description="Tenant-owned council template with required evidence.",
            owner_principal_id=owner_principal_id,
            scope_type=WorkflowScopeType.TENANT,
            tenant_id=tenant_id,
            status="draft",
            tags=["design-review", "council", "template"],
            publication_intent="Require current safe evidence before publish.",
            reviewer_notes="Acyclic review round with manual-resolution quorum.",
        ),
        entry_node_key="lead-intake",
        roles=[
            AgentRoleDefinition(
                role_key="lead",
                display_name="Lead",
                role_kind=RoleKind.AGENT,
                purpose="Prepare the design review brief.",
                responsibilities=[
                    "Summarize request context",
                    "Prepare reviewer input",
                ],
                input_contract_key="design-request",
                output_contract_key="design-brief",
                graph_node_keys=["lead-intake"],
            ),
            *[
                AgentRoleDefinition(
                    role_key=f"reviewer-{index}",
                    display_name=f"Reviewer {index}",
                    role_kind=RoleKind.SUBAGENT,
                    purpose="Evaluate the design brief from an assigned perspective.",
                    responsibilities=[
                        "Assess safe design evidence",
                        "Return verdict and blocker count",
                    ],
                    input_contract_key="design-brief",
                    output_contract_key="reviewer-verdict",
                    graph_node_keys=[f"reviewer-{index}"],
                )
                for index in range(1, 6)
            ],
            AgentRoleDefinition(
                role_key="synthesis",
                display_name="Synthesis",
                role_kind=RoleKind.AGENT,
                purpose="Summarize quorum result and reviewer feedback.",
                responsibilities=["Produce safe synthesis", "Identify next action"],
                input_contract_key="reviewer-verdict",
                output_contract_key="synthesis-result",
                graph_node_keys=["synthesis"],
            ),
            AgentRoleDefinition(
                role_key="handoff",
                display_name="Handoff",
                role_kind=RoleKind.AGENT,
                purpose="Prepare approved development handoff reference.",
                responsibilities=["Create safe handoff summary", "Reference artifact"],
                input_contract_key="synthesis-result",
                output_contract_key="development-handoff",
                graph_node_keys=["handoff"],
            ),
        ],
        contracts=_contracts(),
        nodes=[
            WorkflowNodeDefinition(
                node_key="lead-intake",
                node_type=WorkflowNodeType.ROLE,
                display_name="Lead intake",
                role_key="lead",
            ),
            *[
                WorkflowNodeDefinition(
                    node_key=node_key,
                    node_type=WorkflowNodeType.ROLE,
                    display_name=f"Reviewer {index}",
                    role_key=node_key,
                )
                for index, node_key in enumerate(reviewer_nodes, start=1)
            ],
            WorkflowNodeDefinition(
                node_key="review-quorum",
                node_type=WorkflowNodeType.JOIN,
                display_name="Review quorum",
                join_policy_key="four-of-five-quorum",
            ),
            WorkflowNodeDefinition(
                node_key="synthesis",
                node_type=WorkflowNodeType.ROLE,
                display_name="Synthesis",
                role_key="synthesis",
            ),
            WorkflowNodeDefinition(
                node_key="handoff",
                node_type=WorkflowNodeType.ROLE,
                display_name="Development handoff",
                role_key="handoff",
            ),
            WorkflowNodeDefinition(
                node_key="complete",
                node_type=WorkflowNodeType.TERMINAL,
                display_name="Complete",
            ),
        ],
        edges=[
            *[
                WorkflowEdgeDefinition(
                    edge_key=f"edge-lead-reviewer-{index}",
                    source_node_key="lead-intake",
                    target_node_key=f"reviewer-{index}",
                    contract_key="design-brief",
                )
                for index in range(1, 6)
            ],
            *[
                WorkflowEdgeDefinition(
                    edge_key=edge_key,
                    source_node_key=f"reviewer-{index}",
                    target_node_key="review-quorum",
                    contract_key="reviewer-verdict",
                )
                for index, edge_key in enumerate(reviewer_edges, start=1)
            ],
            WorkflowEdgeDefinition(
                edge_key="edge-quorum-synthesis",
                source_node_key="review-quorum",
                target_node_key="synthesis",
                contract_key="reviewer-verdict",
            ),
            WorkflowEdgeDefinition(
                edge_key="edge-synthesis-handoff",
                source_node_key="synthesis",
                target_node_key="handoff",
                contract_key="synthesis-result",
            ),
            WorkflowEdgeDefinition(
                edge_key="edge-handoff-complete",
                source_node_key="handoff",
                target_node_key="complete",
                contract_key="development-handoff",
            ),
        ],
        join_policies=[
            JoinPolicyDefinition(
                join_policy_key="four-of-five-quorum",
                strategy="quorum",
                inbound_edge_keys=reviewer_edges,
                required_branches=tuple(reviewer_edges),
                quorum_count=4,
                failure_behavior="manual_resolution",
                output_merge_contract_key="reviewer-verdict",
            )
        ],
    )


def _contracts() -> list[ContractSchemaDefinition]:
    return [
        ContractSchemaDefinition(
            contract_key="design-request",
            display_name="Design request",
            contract_kind=WorkflowContractKind.WORKFLOW_INPUT,
            json_schema={
                "type": "object",
                "required": ["summary"],
                "properties": {"summary": {"type": "string"}},
            },
        ),
        ContractSchemaDefinition(
            contract_key="design-brief",
            display_name="Design brief",
            contract_kind=WorkflowContractKind.DATA_CONTRACT,
            json_schema={
                "type": "object",
                "required": ["safe_summary"],
                "properties": {"safe_summary": {"type": "string"}},
            },
        ),
        ContractSchemaDefinition(
            contract_key="reviewer-verdict",
            display_name="Reviewer verdict",
            contract_kind=WorkflowContractKind.DATA_CONTRACT,
            json_schema={
                "type": "object",
                "required": ["verdict", "blocking_issue_count"],
                "properties": {
                    "verdict": {"type": "string"},
                    "blocking_issue_count": {"type": "number"},
                    "safe_feedback_summary": {"type": "string"},
                },
            },
        ),
        ContractSchemaDefinition(
            contract_key="synthesis-result",
            display_name="Synthesis result",
            contract_kind=WorkflowContractKind.DATA_CONTRACT,
            json_schema={
                "type": "object",
                "required": ["safe_synthesis_summary", "next_action"],
                "properties": {
                    "safe_synthesis_summary": {"type": "string"},
                    "next_action": {"type": "string"},
                },
            },
        ),
        ContractSchemaDefinition(
            contract_key="development-handoff",
            display_name="Development handoff",
            contract_kind=WorkflowContractKind.HANDOFF,
            json_schema={
                "type": "object",
                "required": ["safe_summary", "artifact_reference"],
                "properties": {
                    "safe_summary": {"type": "string"},
                    "artifact_reference": {"type": "string"},
                },
            },
        ),
    ]


def _required_case_names() -> tuple[str, ...]:
    return (
        "Four of five quorum success",
        "Three of four quorum success",
        "Revision required outcome",
        "Blocking issue handling",
        "Manual resolution pause",
        "Retry behavior",
        "Cancel behavior",
        "Approved handoff",
        "Cross tenant denial",
        "Redaction guard",
        "Admin live data states",
        "Model backed safe boundary",
    )
