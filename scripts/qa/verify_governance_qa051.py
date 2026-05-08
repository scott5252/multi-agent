#!/usr/bin/env python3
from __future__ import annotations

import os
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
)

TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
SLUG = "qa051-governance-prompt"


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


def verify() -> None:
    import_models()
    engine = create_engine(database_url())
    with Session(engine) as session:
        lineage = session.scalars(
            select(PromptLineage).where(
                PromptLineage.scope_type == "tenant",
                PromptLineage.tenant_id == TENANT_ID,
                PromptLineage.slug == SLUG,
            )
        ).one_or_none()
        if lineage is None:
            raise SystemExit("QA051 governance prompt lineage was not found")

        draft = session.scalars(
            select(PromptDraft).where(
                PromptDraft.prompt_lineage_id == lineage.prompt_lineage_id,
                PromptDraft.status == "active",
            )
        ).one_or_none()
        if draft is None:
            raise SystemExit("QA051 governance prompt draft was not found")
        if draft.current_revision_number < 2:
            raise SystemExit(
                "QA051 Playwright save did not advance the prompt draft revision"
            )

        saved_revision = session.scalars(
            select(PromptDraftRevision)
            .where(
                PromptDraftRevision.prompt_draft_id == draft.prompt_draft_id,
                PromptDraftRevision.revision_number == draft.current_revision_number,
            )
            .limit(1)
        ).one_or_none()
        if saved_revision is None:
            raise SystemExit("QA051 saved prompt revision was not found")
        if saved_revision.safe_summary_json.get("saved_via") != (
            "governance_react_live_data"
        ):
            raise SystemExit("QA051 saved prompt revision lacks live-data marker")

        revision_count = session.scalar(
            select(func.count())
            .select_from(PromptDraftRevision)
            .where(PromptDraftRevision.prompt_draft_id == draft.prompt_draft_id)
        )

    print(
        "QA051 governance prompt save verified: "
        f"lineage={lineage.prompt_lineage_id} "
        f"draft_revision={draft.current_revision_number} "
        f"revision_count={revision_count}"
    )


if __name__ == "__main__":
    verify()
