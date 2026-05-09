from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    created = _request_json(
        "POST",
        "/admin/design-reviews/sessions",
        principal="tenant-admin-acme",
        payload={
            "tenant_id": ACME_TENANT_ID,
            "request_summary": "QA060 API scenario review.",
            "quorum_policy_key": "four_of_five_no_blockers",
            "idempotency_key": "qa060-api-create",
        },
        expected_status=201,
        output_path=Path("/tmp/qa060-create.json"),
    )
    session_id = str(created["design_review_session_id"])
    replay = _request_json(
        "POST",
        "/admin/design-reviews/sessions",
        principal="tenant-admin-acme",
        payload={
            "tenant_id": ACME_TENANT_ID,
            "request_summary": "QA060 API scenario replay.",
            "quorum_policy_key": "four_of_five_no_blockers",
            "idempotency_key": "qa060-api-create",
        },
        expected_status=200,
        output_path=Path("/tmp/qa060-replay.json"),
    )
    if (
        replay["design_review_session_id"] != session_id
        or replay["replayed"] is not True
    ):
        raise RuntimeError("create-session replay did not return the original session")

    _request_json(
        "GET",
        f"/admin/design-reviews/sessions?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-list.json"),
    )
    detail = _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-detail.json"),
    )
    if not detail["revisions"]:
        raise RuntimeError("session detail did not include revision metadata")
    _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}/revisions?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-revisions.json"),
    )
    _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}/rounds?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-rounds.json"),
    )
    manual = _request_json(
        "POST",
        f"/admin/design-reviews/sessions/{session_id}/manual-decisions",
        principal="tenant-admin-acme",
        payload={
            "tenant_id": ACME_TENANT_ID,
            "decision_type": "revise",
            "safe_rationale": "QA060 API asks for clearer design notes.",
            "idempotency_key": "qa060-api-manual",
        },
        expected_status=201,
        output_path=Path("/tmp/qa060-manual-decision.json"),
    )
    if manual["decision_type"] != "revise":
        raise RuntimeError("manual decision response used the wrong decision type")
    _request_json(
        "POST",
        f"/admin/design-reviews/sessions/{session_id}/manual-decisions",
        principal="tenant-admin-acme",
        payload={
            "tenant_id": ACME_TENANT_ID,
            "decision_type": "revise",
            "safe_rationale": "QA060 API asks for clearer design notes.",
            "idempotency_key": "qa060-api-manual",
        },
        expected_status=200,
        output_path=Path("/tmp/qa060-manual-replay.json"),
    )
    _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}/manual-decisions?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-manual-list.json"),
    )
    _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}/handoff?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-handoff.json"),
    )
    globex_empty = _request_json(
        "GET",
        f"/admin/design-reviews/sessions?tenant_id={GLOBEX_TENANT_ID}",
        principal="tenant-admin-globex",
        expected_status=200,
        output_path=Path("/tmp/qa060-globex-empty.json"),
    )
    if globex_empty["state"]["kind"] != "empty":
        raise RuntimeError("Globex did not return a truthful empty state")
    _request_json(
        "GET",
        f"/admin/design-reviews/sessions/{session_id}?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-globex",
        expected_status=403,
        output_path=Path("/tmp/qa060-cross-tenant.json"),
    )

    round_id = _seed_output_value("design_review_round_id")
    _request_json(
        "GET",
        f"/admin/design-reviews/rounds/{round_id}?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-round-detail.json"),
    )
    _request_json(
        "GET",
        f"/admin/design-reviews/rounds/{round_id}/quorum-decision?tenant_id={ACME_TENANT_ID}",
        principal="tenant-admin-acme",
        expected_status=200,
        output_path=Path("/tmp/qa060-quorum.json"),
    )

    print("Exercised QA060 design review API routes")
    print(f"design_review_session_id={session_id}")
    print(f"seeded_round_id={round_id}")
    return 0


def _request_json(
    method: str,
    path: str,
    *,
    principal: str,
    expected_status: int,
    payload: dict[str, Any] | None = None,
    output_path: Path,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        method=method,
        headers={
            "Content-Type": "application/json",
            "X-Local-Principal": principal,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8")
    output_path.write_text(raw, encoding="utf-8")
    if status != expected_status:
        raise RuntimeError(f"{method} {path} expected {expected_status}, got {status}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{method} {path} did not return JSON") from exc
    serialized = json.dumps(data)
    for forbidden in ("Authorization:", "BEGIN PRIVATE KEY", "sk-"):
        if forbidden in serialized:
            raise RuntimeError(f"{method} {path} returned unsafe content")
    return data


def _seed_output_value(key: str) -> str:
    seed_output = Path("/tmp/qa060-seed.txt")
    if not seed_output.exists():
        raise RuntimeError("/tmp/qa060-seed.txt is required")
    prefix = f"{key}="
    for line in seed_output.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix)
    raise RuntimeError(f"{key} was not found in /tmp/qa060-seed.txt")


if __name__ == "__main__":
    raise SystemExit(main())
