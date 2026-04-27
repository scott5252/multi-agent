from __future__ import annotations

import pytest

pytest_plugins = [
    "tests.fixtures.config",
    "tests.fixtures.db",
    "tests.fixtures.providers",
    "tests.fixtures.reliability",
    "tests.fixtures.runtime_orchestration",
]


@pytest.fixture(autouse=True)
def stable_build_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests independent from developer-local .env build metadata."""
    monkeypatch.setenv("COMMIT_SHA", "dev")
    monkeypatch.setenv("BUILD_TIME", "1970-01-01T00:00:00+00:00")
