from __future__ import annotations

from sqlalchemy import text


async def test_session_scope_commits(session) -> None:
    result = await session.execute(text("SELECT version_num FROM alembic_version"))
    assert result.scalar_one() == "0005_immutable_memory"
