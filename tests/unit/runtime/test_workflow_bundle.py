from __future__ import annotations

import json
from hashlib import sha256

from multi_agent_platform.runtime.workflow_bundle import (
    CompiledWorkflowBundle,
    bundle_storage_key,
)
from multi_agent_platform.storage.base import build_artifact_key


def test_compiled_workflow_bundle_canonical_json_and_digest() -> None:
    bundle = CompiledWorkflowBundle(
        workflow_lineage_id="lineage-123",
        source_revision_sha256="sha-1",
        workflow_key="customer-intake",
        workflow_kind="main_workflow",
        document={"name": "Customer Intake", "nodes": [{"key": "triage"}]},
    )

    canonical_json = bundle.canonical_json()

    assert json.loads(canonical_json) == bundle.model_dump(mode="json")
    assert bundle.digest() == sha256(canonical_json).hexdigest()


def test_bundle_storage_key_and_artifact_key_strip_extra_slashes() -> None:
    digest = "abcdef"

    assert bundle_storage_key("workflow-registry/", digest) == (
        "workflow-registry/abcdef.json"
    )
    assert build_artifact_key("/workflow-registry/", "/drafts/", "item.json") == (
        "workflow-registry/drafts/item.json"
    )
