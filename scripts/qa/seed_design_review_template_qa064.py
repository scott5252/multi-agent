from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
HEADERS = {
    "Content-Type": "application/json",
    "X-Local-Principal": "tenant-admin-acme",
}
EVIDENCE_PATH = Path(".data/qa064-artifacts/evidence/qa064-template-seed.json")


def main() -> int:
    payload = _post_json(
        "/admin/design-reviews/templates/council/install",
        {
            "tenant_id": ACME_TENANT_ID,
            "idempotency_key": "qa064-template-install",
            "safe_mode": "both",
        },
    )
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "qa_id": "qa064",
                "tenant_id": ACME_TENANT_ID,
                "workflow_draft_id": payload["workflow_draft_id"],
                "workflow_draft_revision_id": payload["workflow_draft_revision_id"],
                "agent_test_suite_id": payload["agent_test_suite_id"],
                "deterministic_run_id": payload["deterministic_run_id"],
                "model_safe_run_id": payload["model_safe_run_id"],
                "required_evidence_status": payload["required_evidence_status"],
                "publish_gate_status": payload["publish_gate_status"],
                "ready_to_publish": payload["ready_to_publish"],
                "evidence_modes": payload["evidence_modes"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA064 design review council template evidence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_draft_id={payload['workflow_draft_id']}")
    print(f"agent_test_suite_id={payload['agent_test_suite_id']}")
    print(f"evidence_path={EVIDENCE_PATH}")
    return 0


def _post_json(path: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers=HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
