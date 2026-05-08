from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.agent_tests import (
    AgentTestArtifact,
    AgentTestAssertion,
    AgentTestCase,
    AgentTestPublicationRequirement,
    AgentTestRun,
    AgentTestRunStatus,
    AgentTestRunStep,
    AgentTestStatus,
    AgentTestSuite,
    AgentTestTargetType,
)


class StaleAgentTestWriteError(RuntimeError):
    pass


class AgentTestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_suite(self, suite: AgentTestSuite) -> AgentTestSuite:
        self.session.add(suite)
        await self.session.flush()
        return suite

    async def get_suite(self, suite_id: UUID) -> AgentTestSuite | None:
        return await self.session.get(AgentTestSuite, suite_id)

    async def get_suite_for_tenant(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
    ) -> AgentTestSuite | None:
        stmt = select(AgentTestSuite).where(
            AgentTestSuite.agent_test_suite_id == suite_id,
            AgentTestSuite.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_suites_for_tenant(
        self,
        *,
        tenant_id: UUID,
        include_archived: bool = False,
        limit: int | None = None,
    ) -> list[AgentTestSuite]:
        stmt = select(AgentTestSuite).where(AgentTestSuite.tenant_id == tenant_id)
        if not include_archived:
            stmt = stmt.where(AgentTestSuite.status != AgentTestStatus.ARCHIVED)
        stmt = stmt.order_by(AgentTestSuite.updated_at.desc(), AgentTestSuite.name)
        if limit is not None:
            stmt = stmt.limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def find_suite_for_tenant(
        self,
        *,
        tenant_id: UUID,
        target_type: str,
        target_id: str,
        name: str | None = None,
    ) -> AgentTestSuite | None:
        stmt = select(AgentTestSuite).where(
            AgentTestSuite.tenant_id == tenant_id,
            AgentTestSuite.target_type == AgentTestTargetType(target_type),
            AgentTestSuite.target_id == target_id,
            AgentTestSuite.status != AgentTestStatus.ARCHIVED,
        )
        if name is not None:
            stmt = stmt.where(AgentTestSuite.name == name)
        stmt = stmt.order_by(AgentTestSuite.updated_at.desc())
        return (await self.session.execute(stmt.limit(1))).scalar_one_or_none()

    async def require_suite_revision(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        expected_revision: int,
    ) -> AgentTestSuite:
        suite = await self.get_suite_for_tenant(suite_id=suite_id, tenant_id=tenant_id)
        if suite is None:
            raise LookupError("agent test suite not found")
        if suite.revision != expected_revision:
            raise StaleAgentTestWriteError("stale agent test suite revision")
        return suite

    async def add_case(self, case: AgentTestCase) -> AgentTestCase:
        self.session.add(case)
        await self.session.flush()
        return case

    async def get_case_for_tenant(
        self,
        *,
        case_id: UUID,
        tenant_id: UUID,
    ) -> AgentTestCase | None:
        stmt = select(AgentTestCase).where(
            AgentTestCase.agent_test_case_id == case_id,
            AgentTestCase.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_cases_for_suite(self, suite_id: UUID) -> list[AgentTestCase]:
        stmt = (
            select(AgentTestCase)
            .where(
                AgentTestCase.agent_test_suite_id == suite_id,
                AgentTestCase.status != AgentTestStatus.ARCHIVED,
            )
            .order_by(AgentTestCase.case_order, AgentTestCase.created_at)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_assertion(
        self,
        assertion: AgentTestAssertion,
    ) -> AgentTestAssertion:
        self.session.add(assertion)
        await self.session.flush()
        return assertion

    async def list_assertions_for_case(
        self,
        case_id: UUID,
    ) -> list[AgentTestAssertion]:
        stmt = select(AgentTestAssertion).where(
            AgentTestAssertion.agent_test_case_id == case_id
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_run(self, run: AgentTestRun) -> AgentTestRun:
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run(self, run_id: UUID) -> AgentTestRun | None:
        return await self.session.get(AgentTestRun, run_id)

    async def get_run_for_tenant(
        self,
        *,
        run_id: UUID,
        tenant_id: UUID,
    ) -> AgentTestRun | None:
        stmt = select(AgentTestRun).where(
            AgentTestRun.agent_test_run_id == run_id,
            AgentTestRun.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_run_by_idempotency_key(
        self,
        *,
        tenant_id: UUID,
        idempotency_key: str,
    ) -> AgentTestRun | None:
        stmt = select(AgentTestRun).where(
            AgentTestRun.tenant_id == tenant_id,
            AgentTestRun.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_runs_for_suite(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        limit: int | None = None,
    ) -> list[AgentTestRun]:
        stmt = (
            select(AgentTestRun)
            .where(
                AgentTestRun.agent_test_suite_id == suite_id,
                AgentTestRun.tenant_id == tenant_id,
            )
            .order_by(AgentTestRun.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_runs_for_tenant(
        self,
        *,
        tenant_id: UUID,
        limit: int = 20,
    ) -> list[AgentTestRun]:
        stmt = (
            select(AgentTestRun)
            .where(AgentTestRun.tenant_id == tenant_id)
            .order_by(AgentTestRun.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_run_step(self, step: AgentTestRunStep) -> AgentTestRunStep:
        self.session.add(step)
        await self.session.flush()
        return step

    async def list_run_steps(self, run_id: UUID) -> list[AgentTestRunStep]:
        stmt = (
            select(AgentTestRunStep)
            .where(AgentTestRunStep.agent_test_run_id == run_id)
            .order_by(AgentTestRunStep.sequence, AgentTestRunStep.created_at)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_publication_requirement(
        self,
        requirement: AgentTestPublicationRequirement,
    ) -> AgentTestPublicationRequirement:
        self.session.add(requirement)
        await self.session.flush()
        return requirement

    async def list_publication_requirements(
        self,
        *,
        tenant_id: UUID,
        target_type: str,
        target_id: str,
    ) -> list[AgentTestPublicationRequirement]:
        stmt = select(AgentTestPublicationRequirement).where(
            AgentTestPublicationRequirement.tenant_id == tenant_id,
            AgentTestPublicationRequirement.target_type
            == AgentTestTargetType(target_type),
            AgentTestPublicationRequirement.target_id == target_id,
            AgentTestPublicationRequirement.required.is_(True),
            AgentTestPublicationRequirement.archived_at.is_(None),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_publication_requirements_for_tenant(
        self,
        *,
        tenant_id: UUID,
        limit: int = 20,
    ) -> list[AgentTestPublicationRequirement]:
        stmt = (
            select(AgentTestPublicationRequirement)
            .where(
                AgentTestPublicationRequirement.tenant_id == tenant_id,
                AgentTestPublicationRequirement.required.is_(True),
                AgentTestPublicationRequirement.archived_at.is_(None),
            )
            .order_by(AgentTestPublicationRequirement.updated_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def latest_passing_run_for_suite(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        target_version: str | None,
    ) -> AgentTestRun | None:
        stmt = (
            select(AgentTestRun)
            .where(
                AgentTestRun.agent_test_suite_id == suite_id,
                AgentTestRun.tenant_id == tenant_id,
                AgentTestRun.status == AgentTestRunStatus.PASSED,
            )
            .order_by(AgentTestRun.created_at.desc())
        )
        if target_version is not None:
            stmt = stmt.where(AgentTestRun.target_version == target_version)
        return (await self.session.execute(stmt.limit(1))).scalar_one_or_none()

    async def latest_run_for_suite(
        self,
        *,
        suite_id: UUID,
        tenant_id: UUID,
        target_type: str | None = None,
        target_id: str | None = None,
        target_version: str | None = None,
        match_target_version: bool = False,
    ) -> AgentTestRun | None:
        stmt = (
            select(AgentTestRun)
            .where(
                AgentTestRun.agent_test_suite_id == suite_id,
                AgentTestRun.tenant_id == tenant_id,
            )
            .order_by(AgentTestRun.created_at.desc())
        )
        if target_type is not None:
            stmt = stmt.where(
                AgentTestRun.target_type == AgentTestTargetType(target_type)
            )
        if target_id is not None:
            stmt = stmt.where(AgentTestRun.target_id == target_id)
        if match_target_version:
            if target_version is None:
                stmt = stmt.where(AgentTestRun.target_version.is_(None))
            else:
                stmt = stmt.where(AgentTestRun.target_version == target_version)
        return (await self.session.execute(stmt.limit(1))).scalar_one_or_none()

    async def add_artifact(
        self,
        artifact: AgentTestArtifact,
    ) -> AgentTestArtifact:
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def get_artifact_for_tenant(
        self,
        *,
        artifact_id: UUID,
        tenant_id: UUID,
    ) -> AgentTestArtifact | None:
        stmt = select(AgentTestArtifact).where(
            AgentTestArtifact.agent_test_artifact_id == artifact_id,
            AgentTestArtifact.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_artifacts_for_run(
        self,
        *,
        run_id: UUID,
        tenant_id: UUID,
        limit: int = 10,
    ) -> list[AgentTestArtifact]:
        stmt = (
            select(AgentTestArtifact)
            .where(
                AgentTestArtifact.agent_test_run_id == run_id,
                AgentTestArtifact.tenant_id == tenant_id,
            )
            .order_by(AgentTestArtifact.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())
