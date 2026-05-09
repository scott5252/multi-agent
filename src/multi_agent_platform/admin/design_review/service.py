from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.design_review.models import DesignReviewMutationResult
from multi_agent_platform.admin.design_review.redaction import (
    UnsafeDesignReviewContentError,
    digest_safe_text,
    safe_metadata,
    validate_safe_text,
)
from multi_agent_platform.api.ui.admin_console import is_platform_admin
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignDevelopmentHandoffStatus,
    DesignManualDecision,
    DesignManualDecisionType,
    DesignQuorumDecision,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerAssignment,
    DesignReviewerVerdict,
    DesignReviewerVerdictValue,
    DesignReviewRound,
    DesignReviewRoundStatus,
    DesignReviewSession,
    DesignReviewSessionStatus,
    DesignRevision,
)
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository


class DesignReviewError(RuntimeError):
    status_code = 400


class DesignReviewAccessError(DesignReviewError):
    status_code = 403


class DesignReviewNotFoundError(DesignReviewError):
    status_code = 404


class DesignReviewValidationError(DesignReviewError):
    status_code = 422


class DesignReviewConflictError(DesignReviewError):
    status_code = 409


class DesignReviewService:
    def __init__(self, repository: DesignReviewRepository) -> None:
        self.repository = repository

    async def create_session(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        request_summary: str,
        quorum_policy_key: str,
        idempotency_key: str,
        workflow_version_bundle_id: UUID | None = None,
        revision_author_role_key: str = "requester",
        revision_safe_summary: str | None = None,
        revision_artifact_id: UUID | None = None,
        revision_payload_digest: str | None = None,
    ) -> tuple[DesignReviewMutationResult[DesignReviewSession], DesignRevision]:
        self._ensure_tenant_access(principal, tenant_id)
        safe_request_summary = self._safe_text(
            request_summary,
            field_name="request_summary",
        )
        safe_quorum_policy_key = self._safe_key(
            quorum_policy_key,
            field_name="quorum_policy_key",
        )
        safe_idempotency_key = self._safe_key(
            idempotency_key,
            field_name="idempotency_key",
        )
        safe_revision_summary = self._safe_text(
            revision_safe_summary or safe_request_summary,
            field_name="initial_revision.safe_summary",
        )
        safe_author_role_key = self._safe_key(
            revision_author_role_key,
            field_name="initial_revision.author_role_key",
        )
        digest = revision_payload_digest or digest_safe_text(safe_revision_summary)
        (
            session,
            revision,
            replayed,
        ) = await self.repository.create_session_with_revision(
            tenant_id=tenant_id,
            owner_principal_id=principal.principal_id,
            request_summary=safe_request_summary,
            quorum_policy_key=safe_quorum_policy_key,
            idempotency_key=safe_idempotency_key,
            workflow_version_bundle_id=workflow_version_bundle_id,
            revision_author_role_key=safe_author_role_key,
            revision_safe_summary=safe_revision_summary,
            revision_artifact_id=revision_artifact_id,
            revision_payload_digest=self._safe_digest(digest),
        )
        return DesignReviewMutationResult(session, replayed=replayed), revision

    async def list_sessions(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        status: str | None = None,
    ) -> list[DesignReviewSession]:
        self._ensure_tenant_access(principal, tenant_id)
        try:
            parsed_status = (
                DesignReviewSessionStatus(status) if status is not None else None
            )
        except ValueError as exc:
            raise DesignReviewValidationError(
                "unsupported design review status"
            ) from exc
        return await self.repository.list_sessions_for_tenant(
            tenant_id=tenant_id,
            status=parsed_status,
        )

    async def require_session(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
    ) -> DesignReviewSession:
        self._ensure_tenant_access(principal, tenant_id)
        session = await self.repository.get_session_for_tenant(
            session_id=session_id,
            tenant_id=tenant_id,
        )
        if session is None:
            raise DesignReviewNotFoundError("design review session not found")
        return session

    async def list_revisions(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignRevision]:
        await self.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        return await self.repository.list_revisions(
            session_id=session_id,
            tenant_id=tenant_id,
        )

    async def list_rounds(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewRound]:
        await self.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        return await self.repository.list_rounds(
            session_id=session_id,
            tenant_id=tenant_id,
        )

    async def require_round(
        self,
        *,
        principal: PrincipalContext,
        round_id: UUID,
        tenant_id: UUID,
    ) -> DesignReviewRound:
        self._ensure_tenant_access(principal, tenant_id)
        round_record = await self.repository.get_round_for_tenant(
            round_id=round_id,
            tenant_id=tenant_id,
        )
        if round_record is None:
            raise DesignReviewNotFoundError("design review round not found")
        return round_record

    async def round_assignments(
        self,
        *,
        principal: PrincipalContext,
        round_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewerAssignment]:
        await self.require_round(
            principal=principal, round_id=round_id, tenant_id=tenant_id
        )
        return await self.repository.list_assignments(
            round_id=round_id, tenant_id=tenant_id
        )

    async def round_verdicts(
        self,
        *,
        principal: PrincipalContext,
        round_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewerVerdict]:
        await self.require_round(
            principal=principal, round_id=round_id, tenant_id=tenant_id
        )
        return await self.repository.list_verdicts(
            round_id=round_id, tenant_id=tenant_id
        )

    async def get_quorum_decision(
        self,
        *,
        principal: PrincipalContext,
        round_id: UUID,
        tenant_id: UUID,
    ) -> DesignQuorumDecision | None:
        await self.require_round(
            principal=principal, round_id=round_id, tenant_id=tenant_id
        )
        return await self.repository.get_quorum_decision_for_round(
            round_id=round_id,
            tenant_id=tenant_id,
        )

    async def list_manual_decisions(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignManualDecision]:
        await self.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        return await self.repository.list_manual_decisions(
            session_id=session_id,
            tenant_id=tenant_id,
        )

    async def record_manual_decision(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
        decision_type: str,
        safe_rationale: str,
        idempotency_key: str,
        accepted_risk: bool = False,
        round_id: UUID | None = None,
    ) -> DesignReviewMutationResult[DesignManualDecision]:
        await self.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        if round_id is not None:
            await self.require_round(
                principal=principal,
                round_id=round_id,
                tenant_id=tenant_id,
            )
        safe_reason = self._safe_text(safe_rationale, field_name="safe_rationale")
        decision, replayed = await self.repository.create_manual_decision(
            session_id=session_id,
            tenant_id=tenant_id,
            round_id=round_id,
            decision_type=DesignManualDecisionType(decision_type),
            actor_principal_id=principal.principal_id,
            safe_rationale=safe_reason,
            accepted_risk=accepted_risk,
            idempotency_key=self._safe_key(
                idempotency_key,
                field_name="idempotency_key",
            ),
        )
        return DesignReviewMutationResult(decision, replayed=replayed)

    async def get_handoff(
        self,
        *,
        principal: PrincipalContext,
        session_id: UUID,
        tenant_id: UUID,
    ) -> DesignDevelopmentHandoff | None:
        await self.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
        return await self.repository.get_handoff_for_session(
            session_id=session_id,
            tenant_id=tenant_id,
        )

    async def record_round(
        self,
        *,
        tenant_id: UUID,
        session_id: UUID,
        revision_id: UUID,
        round_number: int,
        reviewer_count: int,
        quorum_count: int,
        idempotency_key: str | None = None,
        workflow_run_id: UUID | None = None,
        status: str = DesignReviewRoundStatus.PENDING.value,
    ) -> DesignReviewMutationResult[DesignReviewRound]:
        self._validate_counts(reviewer_count=reviewer_count, quorum_count=quorum_count)
        round_record, replayed = await self.repository.create_round(
            session_id=session_id,
            revision_id=revision_id,
            tenant_id=tenant_id,
            round_number=round_number,
            reviewer_count=reviewer_count,
            quorum_count=quorum_count,
            idempotency_key=(
                self._safe_key(idempotency_key, field_name="idempotency_key")
                if idempotency_key
                else None
            ),
            workflow_run_id=workflow_run_id,
            status=DesignReviewRoundStatus(status),
        )
        return DesignReviewMutationResult(round_record, replayed=replayed)

    async def record_assignment(
        self,
        *,
        tenant_id: UUID,
        round_id: UUID,
        reviewer_key: str,
        role_key: str,
        prompt_version_id: UUID | None = None,
        profile_version_id: UUID | None = None,
        provider_reference: str | None = None,
        enabled: bool = True,
    ) -> DesignReviewerAssignment:
        return await self.repository.create_assignment(
            round_id=round_id,
            tenant_id=tenant_id,
            reviewer_key=self._safe_key(reviewer_key, field_name="reviewer_key"),
            role_key=self._safe_key(role_key, field_name="role_key"),
            prompt_version_id=prompt_version_id,
            profile_version_id=profile_version_id,
            provider_reference=(
                self._safe_text(provider_reference, field_name="provider_reference")
                if provider_reference
                else None
            ),
            enabled=enabled,
        )

    async def record_verdict(
        self,
        *,
        tenant_id: UUID,
        round_id: UUID,
        reviewer_key: str,
        verdict: str,
        score: int,
        blocking_issue_count: int,
        safe_feedback_summary: str,
        output_digest: str,
        artifact_id: UUID | None = None,
        usage_summary: dict[str, object] | None = None,
        idempotency_key: str | None = None,
    ) -> DesignReviewMutationResult[DesignReviewerVerdict]:
        if score < 0 or blocking_issue_count < 0:
            raise DesignReviewValidationError(
                "score and issue counts must be non-negative"
            )
        safe_feedback = self._safe_text(
            safe_feedback_summary,
            field_name="safe_feedback_summary",
        )
        verdict_record, replayed = await self.repository.create_verdict(
            round_id=round_id,
            tenant_id=tenant_id,
            reviewer_key=self._safe_key(reviewer_key, field_name="reviewer_key"),
            verdict=DesignReviewerVerdictValue(verdict),
            score=score,
            blocking_issue_count=blocking_issue_count,
            safe_feedback_summary=safe_feedback,
            artifact_id=artifact_id,
            output_digest=self._safe_digest(output_digest),
            usage_summary=safe_metadata(usage_summary),
            idempotency_key=(
                self._safe_key(idempotency_key, field_name="idempotency_key")
                if idempotency_key
                else None
            ),
        )
        return DesignReviewMutationResult(verdict_record, replayed=replayed)

    async def record_quorum_decision(
        self,
        *,
        tenant_id: UUID,
        round_id: UUID,
        status: str,
        approval_count: int,
        blocking_issue_count: int,
        next_action: str,
        policy_version: str,
        safe_rationale: str,
    ) -> DesignQuorumDecision:
        if approval_count < 0 or blocking_issue_count < 0:
            raise DesignReviewValidationError("decision counts must be non-negative")
        return await self.repository.create_quorum_decision(
            round_id=round_id,
            tenant_id=tenant_id,
            status=DesignQuorumDecisionStatus(status),
            approval_count=approval_count,
            blocking_issue_count=blocking_issue_count,
            next_action=DesignQuorumNextAction(next_action),
            policy_version=self._safe_key(policy_version, field_name="policy_version"),
            safe_rationale=self._safe_text(safe_rationale, field_name="safe_rationale"),
        )

    async def record_handoff(
        self,
        *,
        tenant_id: UUID,
        session_id: UUID,
        approved_revision_id: UUID,
        safe_summary: str,
        output_digest: str,
        idempotency_key: str,
        artifact_id: UUID | None = None,
        status: str = DesignDevelopmentHandoffStatus.READY.value,
    ) -> DesignReviewMutationResult[DesignDevelopmentHandoff]:
        handoff, replayed = await self.repository.create_handoff(
            session_id=session_id,
            tenant_id=tenant_id,
            approved_revision_id=approved_revision_id,
            artifact_id=artifact_id,
            safe_summary=self._safe_text(safe_summary, field_name="safe_summary"),
            output_digest=self._safe_digest(output_digest),
            idempotency_key=self._safe_key(
                idempotency_key, field_name="idempotency_key"
            ),
            status=DesignDevelopmentHandoffStatus(status),
        )
        return DesignReviewMutationResult(handoff, replayed=replayed)

    @staticmethod
    def _ensure_tenant_access(
        principal: PrincipalContext,
        tenant_id: UUID,
    ) -> None:
        if is_platform_admin(principal):
            return
        if (
            principal.tenant_id != tenant_id
            or "tenant_admin" not in principal.role_codes
        ):
            raise DesignReviewAccessError("design review access denied")

    @staticmethod
    def _safe_text(value: str, *, field_name: str) -> str:
        try:
            return validate_safe_text(value, field_name=field_name)
        except UnsafeDesignReviewContentError as exc:
            raise DesignReviewValidationError(str(exc)) from exc

    @classmethod
    def _safe_key(cls, value: str, *, field_name: str) -> str:
        safe_value = cls._safe_text(value, field_name=field_name)
        if len(safe_value) > 160:
            raise DesignReviewValidationError(
                f"{field_name} exceeds the key length limit"
            )
        return safe_value

    @classmethod
    def _safe_digest(cls, value: str) -> str:
        safe_digest = cls._safe_key(value, field_name="digest")
        if len(safe_digest) > 128:
            raise DesignReviewValidationError("digest exceeds the length limit")
        return safe_digest

    @staticmethod
    def _validate_counts(*, reviewer_count: int, quorum_count: int) -> None:
        if reviewer_count < 0 or quorum_count < 0:
            raise DesignReviewValidationError(
                "reviewer and quorum counts must be non-negative"
            )
        if quorum_count > reviewer_count:
            raise DesignReviewValidationError(
                "quorum count cannot exceed reviewer count"
            )
