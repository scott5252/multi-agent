from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

EVIDENCE_PATH = Path(".data/qa061-artifacts/evidence/qa061-model-backed-role-seed.json")


def main() -> None:
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    evidence = {
        "qa_id": "qa061",
        "seeded_at": datetime.now(UTC).isoformat(),
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "workflow_run_id": "qa061-runtime-run",
        "node_key": "ux-reviewer-node",
        "role_key": "ux-reviewer",
        "execution_mode": "mock_model_gateway",
        "safe_summary": "Safe model-backed role executor QA seed.",
        "output_contract_key": "reviewer-output-v1",
        "artifact_reference": "model-backed-roles/qa061/safe-output.json",
        "usage_summary": {
            "usage_available": "available",
            "input_tokens": 7,
            "output_tokens": 5,
            "total_tokens": 12,
        },
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print("Seeded QA061 model-backed role executor evidence")
    print(f"evidence_path={EVIDENCE_PATH}")


if __name__ == "__main__":
    main()
