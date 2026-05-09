from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}
EVIDENCE_PATH = Path(".data/qa063-artifacts/evidence/qa063-workspace-verify.json")


def main() -> int:
    acme = _get_json(
        f"/admin/app/design-reviews/bootstrap.json?tenant_id={ACME_TENANT_ID}",
        ACME_HEADERS,
    )
    globex = _get_json(
        f"/admin/app/design-reviews/bootstrap.json?tenant_id={GLOBEX_TENANT_ID}",
        GLOBEX_HEADERS,
    )
    sessions = acme["sessions"]
    selected = acme["selected_session"]
    if not sessions:
        raise RuntimeError("expected QA063 Acme workspace sessions")
    if selected is None:
        raise RuntimeError("expected QA063 selected session detail")
    if selected["handoff"]["state"]["kind"] != "ready":
        raise RuntimeError("expected QA063 handoff state to be ready")
    if not selected["rounds"]:
        raise RuntimeError("expected QA063 round details")
    latest_round = selected["rounds"][-1]
    if latest_round["quorum_decision"]["status"] != "passed":
        raise RuntimeError("expected QA063 quorum decision to pass")
    if len(latest_round["verdicts"]) < 5:
        raise RuntimeError("expected QA063 reviewer verdict summaries")
    if globex["sessions"]:
        raise RuntimeError("expected Globex workspace to be empty")
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "qa_id": "qa063",
                "acme_session_count": len(sessions),
                "globex_session_count": len(globex["sessions"]),
                "selected_session_id": selected["session"]["design_review_session_id"],
                "round_count": len(selected["rounds"]),
                "verdict_count": len(latest_round["verdicts"]),
                "handoff_state": selected["handoff"]["state"]["kind"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Verified QA063 design review workspace live data")
    print(f"evidence_path={EVIDENCE_PATH}")
    return 0


def _get_json(path: str, headers: dict[str, str]) -> dict[str, object]:
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={**headers, "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
