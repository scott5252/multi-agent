from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


class DesignReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_session(
        self,
        session_id: UUID,
    ) -> DesignReviewSession | None:
        return await self.session.get(DesignReviewSession, session_id)

    async def get_session_for_tenant(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> DesignReviewSession | None:
        stmt = select(DesignReviewSession).where(
            DesignReviewSession.design_review_session_id == session_id,
            DesignReviewSession.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_session_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> DesignReviewSession | None:
        stmt = select(DesignReviewSession).where(
            DesignReviewSession.tenant_id == tenant_id,
            DesignReviewSession.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_sessions_for_tenant(
        self,
        *,
        tenant_id: UUID,
        status: DesignReviewSessionStatus | None = None,
        limit: int = 50,
    ) -> list[DesignReviewSession]:
        stmt = select(DesignReviewSession).where(
            DesignReviewSession.tenant_id == tenant_id
        )
        if status is not None:
            stmt = stmt.where(DesignReviewSession.status == status)
        stmt = stmt.order_by(
            DesignReviewSession.updated_at.desc(),
            DesignReviewSession.created_at.desc(),
        ).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_session_with_revision(
        self,
        *,
        tenant_id: UUID,
        owner_principal_id: str,
        request_summary: str,
        quorum_policy_key: str,
        idempotency_key: str,
        revision_safe_summary: str,
        revision_payload_digest: str,
        workflow_version_bundle_id: UUID | None = None,
        revision_author_role_key: str = "requester",
        revision_artifact_id: UUID | None = None,
    ) -> tuple[DesignReviewSession, DesignRevision, bool]:
        existing = await self.get_session_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            revision = await self.get_revision_by_number(
                session_id=existing.design_review_session_id,
                tenant_id=tenant_id,
                revision_number=existing.active_revision_number,
            )
            if revision is None:
                raise RuntimeError("design review session is missing active revision")
            return existing, revision, True

        session = DesignReviewSession(
            tenant_id=tenant_id,
            status=DesignReviewSessionStatus.DRAFT,
            request_summary=request_summary,
            active_revision_number=1,
            quorum_policy_key=quorum_policy_key,
            workflow_version_bundle_id=workflow_version_bundle_id,
            owner_principal_id=owner_principal_id,
            idempotency_key=idempotency_key,
        )
        self.session.add(session)
        await self.session.flush()
        revision = DesignRevision(
            design_review_session_id=session.design_review_session_id,
            tenant_id=tenant_id,
            revision_number=1,
            author_role_key=revision_author_role_key,
            safe_summary=revision_safe_summary,
            artifact_id=revision_artifact_id,
            payload_digest=revision_payload_digest,
        )
        self.session.add(revision)
        await self.session.flush()
        return session, revision, False

    async def get_revision_by_number(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
        revision_number: int,
    ) -> DesignRevision | None:
        stmt = select(DesignRevision).where(
            DesignRevision.design_review_session_id == session_id,
            DesignRevision.tenant_id == tenant_id,
            DesignRevision.revision_number == revision_number,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_revisions(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignRevision]:
        stmt = (
            select(DesignRevision)
            .where(
                DesignRevision.design_review_session_id == session_id,
                DesignRevision.tenant_id == tenant_id,
            )
            .order_by(DesignRevision.revision_number)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_active_revision(
        self,
        *,
        session: DesignReviewSession,
    ) -> DesignRevision | None:
        return await self.get_revision_by_number(
            session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
            revision_number=session.active_revision_number,
        )

    async def create_next_revision(
        self,
        *,
        session: DesignReviewSession,
        author_role_key: str,
        safe_summary: str,
        payload_digest: str,
        previous_revision_id: UUID,
        artifact_id: UUID | None = None,
    ) -> DesignRevision:
        next_number = session.active_revision_number + 1
        revision = DesignRevision(
            design_review_session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
            revision_number=next_number,
            author_role_key=author_role_key,
            safe_summary=safe_summary,
            artifact_id=artifact_id,
            payload_digest=payload_digest,
            previous_revision_id=previous_revision_id,
        )
        self.session.add(revision)
        session.active_revision_number = next_number
        await self.session.flush()
        return revision

    async def update_session_state(
        self,
        *,
        session: DesignReviewSession,
        status: DesignReviewSessionStatus,
        workflow_version_bundle_id: UUID | None = None,
    ) -> DesignReviewSession:
        session.status = status
        if workflow_version_bundle_id is not None:
            session.workflow_version_bundle_id = workflow_version_bundle_id
        await self.session.flush()
        return session

    async def create_round(
        self,
        *,
        session_id: UUID,
        revision_id: UUID,
        tenant_id: UUID,
        round_number: int,
        reviewer_count: int,
        quorum_count: int,
        idempotency_key: str | None = None,
        workflow_run_id: UUID | None = None,
        status: DesignReviewRoundStatus = DesignReviewRoundStatus.PENDING,
    ) -> tuple[DesignReviewRound, bool]:
        if idempotency_key is not None:
            existing = await self.get_round_by_idempotency_key(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
            )
            if existing is not None:
                return existing, True
        round_record = DesignReviewRound(
            design_review_session_id=session_id,
            design_revision_id=revision_id,
            tenant_id=tenant_id,
            round_number=round_number,
            status=status,
            workflow_run_id=workflow_run_id,
            reviewer_count=reviewer_count,
            quorum_count=quorum_count,
            idempotency_key=idempotency_key,
        )
        self.session.add(round_record)
        await self.session.flush()
        return round_record, False

    async def get_round(
        self,
        round_id: UUID,
    ) -> DesignReviewRound | None:
        return await self.session.get(DesignReviewRound, round_id)

    async def get_round_for_tenant(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
    ) -> DesignReviewRound | None:
        stmt = select(DesignReviewRound).where(
            DesignReviewRound.design_review_round_id == round_id,
            DesignReviewRound.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_round_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> DesignReviewRound | None:
        stmt = select(DesignReviewRound).where(
            DesignReviewRound.tenant_id == tenant_id,
            DesignReviewRound.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_rounds(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewRound]:
        stmt = (
            select(DesignReviewRound)
            .where(
                DesignReviewRound.design_review_session_id == session_id,
                DesignReviewRound.tenant_id == tenant_id,
            )
            .order_by(DesignReviewRound.round_number)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_latest_round(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> DesignReviewRound | None:
        stmt = (
            select(DesignReviewRound)
            .where(
                DesignReviewRound.design_review_session_id == session_id,
                DesignReviewRound.tenant_id == tenant_id,
            )
            .order_by(DesignReviewRound.round_number.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def update_round_state(
        self,
        *,
        round_record: DesignReviewRound,
        status: DesignReviewRoundStatus,
        workflow_run_id: UUID | None = None,
    ) -> DesignReviewRound:
        round_record.status = status
        if workflow_run_id is not None:
            round_record.workflow_run_id = workflow_run_id
        now = datetime.now(UTC)
        if (
            status is DesignReviewRoundStatus.RUNNING
            and round_record.started_at is None
        ):
            round_record.started_at = now
        if status in {
            DesignReviewRoundStatus.COMPLETED,
            DesignReviewRoundStatus.REVISION_REQUIRED,
            DesignReviewRoundStatus.MANUAL_RESOLUTION,
            DesignReviewRoundStatus.FAILED,
        }:
            round_record.completed_at = now
        await self.session.flush()
        return round_record

    async def create_assignment(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
        reviewer_key: str,
        role_key: str,
        prompt_version_id: UUID | None = None,
        profile_version_id: UUID | None = None,
        provider_reference: str | None = None,
        enabled: bool = True,
    ) -> DesignReviewerAssignment:
        assignment = DesignReviewerAssignment(
            design_review_round_id=round_id,
            tenant_id=tenant_id,
            reviewer_key=reviewer_key,
            role_key=role_key,
            prompt_version_id=prompt_version_id,
            profile_version_id=profile_version_id,
            provider_reference=provider_reference,
            enabled=enabled,
        )
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def list_assignments(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewerAssignment]:
        stmt = (
            select(DesignReviewerAssignment)
            .where(
                DesignReviewerAssignment.design_review_round_id == round_id,
                DesignReviewerAssignment.tenant_id == tenant_id,
            )
            .order_by(DesignReviewerAssignment.reviewer_key)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_verdict(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
        reviewer_key: str,
        verdict: DesignReviewerVerdictValue,
        score: int,
        blocking_issue_count: int,
        safe_feedback_summary: str,
        output_digest: str,
        artifact_id: UUID | None = None,
        usage_summary: dict[str, object] | None = None,
        idempotency_key: str | None = None,
    ) -> tuple[DesignReviewerVerdict, bool]:
        if idempotency_key is not None:
            existing = await self.get_verdict_by_idempotency_key(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
            )
            if existing is not None:
                return existing, True
        verdict_record = DesignReviewerVerdict(
            design_review_round_id=round_id,
            tenant_id=tenant_id,
            reviewer_key=reviewer_key,
            verdict=verdict,
            score=score,
            blocking_issue_count=blocking_issue_count,
            safe_feedback_summary=safe_feedback_summary,
            artifact_id=artifact_id,
            output_digest=output_digest,
            usage_summary=usage_summary or {},
            idempotency_key=idempotency_key,
        )
        self.session.add(verdict_record)
        await self.session.flush()
        return verdict_record, False

    async def get_verdict_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> DesignReviewerVerdict | None:
        stmt = select(DesignReviewerVerdict).where(
            DesignReviewerVerdict.tenant_id == tenant_id,
            DesignReviewerVerdict.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_verdicts(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignReviewerVerdict]:
        stmt = (
            select(DesignReviewerVerdict)
            .where(
                DesignReviewerVerdict.design_review_round_id == round_id,
                DesignReviewerVerdict.tenant_id == tenant_id,
            )
            .order_by(DesignReviewerVerdict.reviewer_key)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_quorum_decision(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
        status: DesignQuorumDecisionStatus,
        approval_count: int,
        blocking_issue_count: int,
        next_action: DesignQuorumNextAction,
        policy_version: str,
        safe_rationale: str,
    ) -> DesignQuorumDecision:
        decision = DesignQuorumDecision(
            design_review_round_id=round_id,
            tenant_id=tenant_id,
            status=status,
            approval_count=approval_count,
            blocking_issue_count=blocking_issue_count,
            next_action=next_action,
            policy_version=policy_version,
            safe_rationale=safe_rationale,
        )
        self.session.add(decision)
        await self.session.flush()
        return decision

    async def get_quorum_decision_for_round(
        self,
        *,
        round_id: UUID,
        tenant_id: UUID,
    ) -> DesignQuorumDecision | None:
        stmt = select(DesignQuorumDecision).where(
            DesignQuorumDecision.design_review_round_id == round_id,
            DesignQuorumDecision.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_manual_decision(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
        decision_type: DesignManualDecisionType,
        actor_principal_id: str,
        safe_rationale: str,
        accepted_risk: bool,
        idempotency_key: str,
        round_id: UUID | None = None,
    ) -> tuple[DesignManualDecision, bool]:
        existing = await self.get_manual_decision_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            return existing, True
        decision = DesignManualDecision(
            design_review_session_id=session_id,
            design_review_round_id=round_id,
            tenant_id=tenant_id,
            decision_type=decision_type,
            actor_principal_id=actor_principal_id,
            safe_rationale=safe_rationale,
            accepted_risk=accepted_risk,
            idempotency_key=idempotency_key,
        )
        self.session.add(decision)
        await self.session.flush()
        return decision, False

    async def get_manual_decision_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> DesignManualDecision | None:
        stmt = select(DesignManualDecision).where(
            DesignManualDecision.tenant_id == tenant_id,
            DesignManualDecision.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_manual_decisions(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> list[DesignManualDecision]:
        stmt = (
            select(DesignManualDecision)
            .where(
                DesignManualDecision.design_review_session_id == session_id,
                DesignManualDecision.tenant_id == tenant_id,
            )
            .order_by(DesignManualDecision.created_at)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_handoff(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
        approved_revision_id: UUID,
        safe_summary: str,
        output_digest: str,
        idempotency_key: str,
        artifact_id: UUID | None = None,
        status: DesignDevelopmentHandoffStatus = DesignDevelopmentHandoffStatus.READY,
    ) -> tuple[DesignDevelopmentHandoff, bool]:
        existing = await self.get_handoff_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            return existing, True
        handoff = DesignDevelopmentHandoff(
            design_review_session_id=session_id,
            tenant_id=tenant_id,
            approved_revision_id=approved_revision_id,
            artifact_id=artifact_id,
            safe_summary=safe_summary,
            output_digest=output_digest,
            status=status,
            idempotency_key=idempotency_key,
        )
        self.session.add(handoff)
        await self.session.flush()
        return handoff, False

    async def get_handoff_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> DesignDevelopmentHandoff | None:
        stmt = select(DesignDevelopmentHandoff).where(
            DesignDevelopmentHandoff.tenant_id == tenant_id,
            DesignDevelopmentHandoff.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_handoff_for_session(
        self,
        *,
        session_id: UUID,
        tenant_id: UUID,
    ) -> DesignDevelopmentHandoff | None:
        stmt = select(DesignDevelopmentHandoff).where(
            DesignDevelopmentHandoff.design_review_session_id == session_id,
            DesignDevelopmentHandoff.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()
