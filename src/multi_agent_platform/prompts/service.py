from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
    PromptValidationResult,
    PromptVersion,
    TenantPromptVersionGrant,
)
from multi_agent_platform.db.repositories.prompts import (
    PromptDraftRecord,
    PromptRepository,
)
from multi_agent_platform.prompts.fixture_safety import sanitize_fixture_values
from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.validation import validate_prompt


class PromptPublishError(RuntimeError):
    pass


class PromptService:
    def __init__(self, repository: PromptRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: AsyncSession) -> PromptService:
        return cls(PromptRepository(session))

    async def create_prompt_lineage(
        self,
        *,
        scope_type: str,
        tenant_id: UUID | None,
        slug: str,
        display_name: str,
        purpose: str,
        principal_id: str,
    ) -> PromptDraftRecord:
        return await self.repository.create_lineage_with_draft(
            scope_type=scope_type,
            tenant_id=tenant_id,
            slug=slug,
            display_name=display_name,
            purpose=purpose,
            principal_id=principal_id,
        )

    async def save_draft_revision(
        self,
        *,
        draft: PromptDraft,
        expected_revision_number: int,
        prompt_title: str,
        purpose: str,
        usage_notes: str,
        template_content: str,
        variables: list[PromptVariableDeclaration],
        fixture_values: dict[str, str],
        principal_id: str,
    ) -> PromptDraftRevision:
        sanitized = sanitize_fixture_values(fixture_values)
        fixture_sets: list[dict[str, object]] = [
            {
                "fixture_set_id": "default",
                "label": "Default",
                "values_by_variable": sanitized.values_by_variable,
                "sanitization_summary": {
                    "redaction_categories": list(sanitized.redaction_categories)
                },
            }
        ]
        return await self.repository.save_draft_revision(
            draft=draft,
            expected_revision_number=expected_revision_number,
            prompt_title=prompt_title,
            purpose=purpose,
            usage_notes=usage_notes,
            template_content=template_content,
            variable_declarations=[variable.to_json() for variable in variables],
            fixture_value_sets=fixture_sets,
            safe_summary={"variable_count": len(variables)},
            principal_id=principal_id,
        )

    async def validate_revision(
        self,
        *,
        draft_revision: PromptDraftRevision,
        principal_id: str,
    ) -> PromptValidationResult:
        variables = [
            PromptVariableDeclaration(
                name=str(item["name"]),
                purpose=str(item.get("purpose", item["name"])),
                required=bool(item.get("required", True)),
                allowed_value_category=str(
                    item.get("allowed_value_category", "synthetic")
                ),
                safety_classification=str(
                    item.get("safety_classification", "safe_fixture")
                ),
                sample_guidance=str(item.get("sample_guidance", "")),
                display_order=int(str(item.get("display_order", 0))),
            )
            for item in draft_revision.variable_declarations_json
        ]
        fixture_values: dict[str, str] = {}
        if draft_revision.fixture_value_sets_json:
            first_set = draft_revision.fixture_value_sets_json[0]
            raw_values = first_set.get("values_by_variable", {})
            if isinstance(raw_values, dict):
                fixture_values = {
                    str(key): str(value) for key, value in raw_values.items()
                }
        report = validate_prompt(
            template_content=draft_revision.template_content,
            variables=variables,
            fixture_values=fixture_values,
        )
        return await self.repository.record_validation_result(
            draft_revision=draft_revision,
            status=report.status,
            findings=report.to_json_findings(),
            principal_id=principal_id,
        )

    async def publish(
        self,
        *,
        lineage: PromptLineage,
        draft: PromptDraft,
        draft_revision: PromptDraftRevision,
        validation_result: PromptValidationResult,
        principal_id: str,
        reason: str,
    ) -> PromptVersion:
        if validation_result.status != "passed":
            raise PromptPublishError("prompt validation must pass before publication")
        if (
            validation_result.template_content_sha256
            != draft_revision.template_content_sha256
        ):
            raise PromptPublishError("validation result is stale")
        sequence = await self.repository.next_version_sequence(
            lineage.prompt_lineage_id
        )
        version = PromptVersion(
            prompt_lineage_id=lineage.prompt_lineage_id,
            scope_type=lineage.scope_type,
            tenant_id=lineage.tenant_id,
            version_sequence=sequence,
            display_version=f"v{sequence}",
            published_from_draft_id=draft.prompt_draft_id,
            published_from_revision_id=draft_revision.prompt_draft_revision_id,
            validation_result_id=validation_result.prompt_validation_result_id,
            template_content=draft_revision.template_content,
            template_content_sha256=draft_revision.template_content_sha256,
            variable_declarations_json=draft_revision.variable_declarations_json,
            purpose=draft_revision.purpose,
            usage_notes=draft_revision.usage_notes,
            safe_summary_json=draft_revision.safe_summary_json,
            published_by_principal_id=principal_id,
            publication_reason=reason,
        )
        self.repository.session.add(version)
        await self.repository.session.flush()
        lineage.latest_published_prompt_version_id = version.prompt_version_id
        draft.status = "published_source"
        await self.repository.session.flush()
        return version

    async def retire_version(
        self,
        *,
        version: PromptVersion,
        principal_id: str,
        reason: str,
    ) -> PromptVersion:
        return await self.repository.retire_prompt_version(
            version=version,
            principal_id=principal_id,
            reason=reason,
        )

    async def grant_version_to_tenant(
        self,
        *,
        version: PromptVersion,
        tenant_id: UUID,
        principal_id: str,
        reason: str,
    ) -> TenantPromptVersionGrant:
        if version.scope_type != "platform":
            raise PromptPublishError("only platform prompt versions can be granted")
        return await self.repository.grant_prompt_version(
            prompt_version_id=version.prompt_version_id,
            grantee_tenant_id=tenant_id,
            principal_id=principal_id,
            reason=reason,
        )
