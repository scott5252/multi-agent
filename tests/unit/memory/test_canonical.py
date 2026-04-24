from __future__ import annotations

import pytest

from multi_agent_platform.memory.canonical import (
    CanonicalJsonError,
    canonical_dumps,
    content_sha256,
    content_size_bytes,
)


def test_canonical_json_is_deterministic_and_counts_bytes() -> None:
    left = {"b": 2, "a": None, "removed": {"$memory_removed": ["legacy"]}}
    right = {"removed": {"$memory_removed": ["legacy"]}, "a": None, "b": 2}

    assert canonical_dumps(left) == canonical_dumps(right)
    assert content_sha256(left) == content_sha256(right)
    assert content_size_bytes(left) == len(canonical_dumps(left).encode("utf-8"))


def test_canonical_json_rejects_unsupported_values() -> None:
    with pytest.raises(CanonicalJsonError):
        canonical_dumps({"bad": b"bytes"})

    with pytest.raises(CanonicalJsonError):
        canonical_dumps({"$memory_removed": "legacy"})
