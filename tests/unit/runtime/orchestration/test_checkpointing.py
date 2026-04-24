from __future__ import annotations

import pytest

from multi_agent_platform.runtime.orchestration.checkpointing import (
    LangGraphCheckpointerFactory,
    assert_checkpoint_compatible,
)


def test_checkpoint_digest_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="bundle digest"):
        assert_checkpoint_compatible(
            checkpoint_bundle_digest="old",
            run_bundle_digest="new",
        )


def test_checkpointer_factory_records_database_url() -> None:
    factory = LangGraphCheckpointerFactory("postgresql://example")

    assert factory.database_url == "postgresql://example"
