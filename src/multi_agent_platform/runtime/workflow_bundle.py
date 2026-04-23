from __future__ import annotations

import json
from hashlib import sha256

from pydantic import BaseModel, Field

from multi_agent_platform.storage.base import build_artifact_key


class CompiledWorkflowBundle(BaseModel):
    workflow_lineage_id: str
    source_revision_sha256: str
    workflow_key: str
    workflow_kind: str
    version_sequence: int = 0
    display_version: str = ""
    compiler_version: str = ""
    dependencies: dict[str, object] = Field(default_factory=dict)
    run_version_blueprint: dict[str, object] = Field(default_factory=dict)
    document: dict[str, object]

    def canonical_json(self) -> bytes:
        return json.dumps(
            self.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def digest(self) -> str:
        return sha256(self.canonical_json()).hexdigest()


def bundle_storage_key(prefix: str, digest: str) -> str:
    return build_artifact_key(prefix, f"{digest}.json")
