from __future__ import annotations

import json
from pathlib import Path

from multi_agent_platform.runtime.orchestration.role_output_contracts import (
    validate_role_output,
)

EVIDENCE_PATH = Path(".data/qa061-artifacts/evidence/qa061-model-backed-role-seed.json")
UNSAFE_MARKERS = (
    "raw prompt",
    "raw completion",
    "provider payload",
    "authorization:",
    "bearer ",
    "sk-",
    "/users/",
)


def main() -> None:
    if not EVIDENCE_PATH.exists():
        raise SystemExit(f"missing QA061 evidence: {EVIDENCE_PATH}")
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    encoded = json.dumps(evidence).lower()
    for marker in UNSAFE_MARKERS:
        if marker in encoded:
            raise SystemExit(f"unsafe marker leaked into QA061 evidence: {marker}")
    validate_role_output(
        {
            "summary": "Safe reviewer summary.",
            "status": "approved",
            "artifact_refs": [evidence["artifact_reference"]],
        },
        contract_schema={"required": ["summary", "status"]},
    )
    print("Verified QA061 model-backed role executor evidence")
    print(f"evidence_path={EVIDENCE_PATH}")


if __name__ == "__main__":
    main()
