#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
    PromptValidationResult,
    PromptVersion,
    TenantPromptVersionGrant,
)
from multi_agent_platform.db.models.tenant import Tenant

TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
SLUG = "qa051-governance-prompt"
DISPLAY_NAME = "QA051 Governance Prompt"
TEMPLATE_CONTENT = "Summarize governance evidence using redaction-safe metadata."


def stable_uuid(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"multi-agent-platform/spec051/{name}")


def database_url() -> str:
    url = os.environ.get("DATABASE_URL") or dotenv_value("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required")
    if url.startswith("sqlite+aiosqlite:"):
        return url.replace("sqlite+aiosqlite:", "sqlite:", 1)
    if url.startswith("postgresql+asyncpg:"):
        return url.replace("postgresql+asyncpg:", "postgresql+psycopg:", 1)
    return url


def dotenv_value(key: str) -> str | None:
    env_path = os.getcwd() + "/.env"
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                name, value = stripped.split("=", 1)
                if name == key:
                    return value.strip().strip('"').strip("'")
    except FileNotFoundError:
        return None
    return None


def seed() -> None:
    import_models()
    engine = create_engine(database_url())
    now = datetime.now(UTC)
    template_hash = hashlib.sha256(TEMPLATE_CONTENT.encode("utf-8")).hexdigest()

    with Session(engine) as session:
        tenant = session.get(Tenant, TENANT_ID)
        if tenant is None:
            raise SystemExit(f"Tenant {TENANT_ID} must be seeded before QA051")

        existing = session.scalars(
            select(PromptLineage).where(
                PromptLineage.scope_type == "tenant",
                PromptLineage.tenant_id == TENANT_ID,
                PromptLineage.slug == SLUG,
            )
        ).one_or_none()
        if existing is not None:
            print(
                f"QA051 governance prompt already exists: {existing.prompt_lineage_id}"
            )
            return

        lineage_id = stable_uuid("prompt-lineage")
        draft_id = stable_uuid("prompt-draft")
        revision_id = stable_uuid("prompt-revision-r1")
        validation_id = stable_uuid("prompt-validation-r1")
        version_id = stable_uuid("prompt-version-v1")
        grant_id = stable_uuid("prompt-grant-acme")

        lineage = PromptLineage(
            prompt_lineage_id=lineage_id,
            scope_type="tenant",
            tenant_id=TENANT_ID,
            slug=SLUG,
            display_name=DISPLAY_NAME,
            purpose="QA051 redaction-safe governance prompt evidence.",
            status="active",
            created_by_principal_id="qa051-seed",
        )
        session.add(lineage)
        session.flush()

        draft = PromptDraft(
            prompt_draft_id=draft_id,
            prompt_lineage_id=lineage_id,
            scope_type="tenant",
            tenant_id=TENANT_ID,
            status="active",
            current_revision_number=1,
            created_by_principal_id="qa051-seed",
            last_edited_by_principal_id="qa051-seed",
        )
        session.add(draft)
        session.flush()

        revision = PromptDraftRevision(
            prompt_draft_revision_id=revision_id,
            prompt_draft_id=draft_id,
            revision_number=1,
            prompt_title=DISPLAY_NAME,
            purpose="QA051 redaction-safe governance prompt evidence.",
            usage_notes="Use only safe summaries for QA051 governance validation.",
            template_content=TEMPLATE_CONTENT,
            template_content_sha256=template_hash,
            variable_declarations_json=[{"name": "topic", "kind": "string"}],
            fixture_value_sets_json=[{"fixture_set_id": "safe-summary"}],
            safe_summary_json={
                "summary": "QA051 seeded prompt exposes safe metadata only.",
                "seeded_for": "governance_react_live_data",
            },
            created_by_principal_id="qa051-seed",
            created_at=now,
        )
        session.add(revision)
        session.flush()

        validation = PromptValidationResult(
            prompt_validation_result_id=validation_id,
            prompt_draft_revision_id=revision_id,
            rule_set_version="prompt-runtime-v1",
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
            findings_json=[],
            template_content_sha256=template_hash,
            validated_fixture_set_ids=["safe-summary"],
            executed_by_principal_id="qa051-seed",
            executed_at=now,
        )
        session.add(validation)
        session.flush()

        version = PromptVersion(
            prompt_version_id=version_id,
            prompt_lineage_id=lineage_id,
            scope_type="tenant",
            tenant_id=TENANT_ID,
            version_sequence=1,
            display_version="v1",
            status="active",
            published_from_draft_id=draft_id,
            published_from_revision_id=revision_id,
            validation_result_id=validation_id,
            template_content=TEMPLATE_CONTENT,
            template_content_sha256=template_hash,
            variable_declarations_json=[{"name": "topic", "kind": "string"}],
            purpose="QA051 redaction-safe governance prompt evidence.",
            usage_notes="Use only safe summaries for QA051 governance validation.",
            safe_summary_json={"summary": "QA051 published prompt metadata is safe."},
            published_by_principal_id="qa051-seed",
            published_at=now,
            publication_reason="Seeded through QA051 setup for Playwright mutation.",
        )
        session.add(version)
        session.flush()

        grant = TenantPromptVersionGrant(
            tenant_prompt_version_grant_id=grant_id,
            prompt_version_id=version_id,
            grantee_tenant_id=TENANT_ID,
            status="active",
            granted_by_principal_id="qa051-seed",
            created_at=now,
            reason="Tenant owns this QA051 prompt seed.",
        )
        session.add(grant)

        draft.latest_revision_id = revision_id
        draft.last_validation_result_id = validation_id
        lineage.latest_draft_id = draft_id
        lineage.latest_published_prompt_version_id = version_id
        session.commit()

    print(f"Seeded QA051 governance prompt: {lineage_id}")


if __name__ == "__main__":
    seed()
