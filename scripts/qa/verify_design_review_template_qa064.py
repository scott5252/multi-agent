from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}
EVIDENCE_PATH = Path(".data/qa064-artifacts/evidence/qa064-template-verify.json")


def main() -> int:
    acme = _get_json(
        f"/admin/app/design-reviews/bootstrap.json?tenant_id={ACME_TENANT_ID}",
        ACME_HEADERS,
    )
    globex = _get_json(
        f"/admin/app/design-reviews/bootstrap.json?tenant_id={GLOBEX_TENANT_ID}",
        GLOBEX_HEADERS,
    )
    denied_status = _post_denied_status()
    setup = acme["template_setup"]
    if setup["status"] != "ready":
        raise RuntimeError("expected QA064 council template to be ready")
    if setup["required_evidence_status"] != "passing":
        raise RuntimeError("expected QA064 required evidence to pass")
    if setup["publish_gate_status"] != "ready":
        raise RuntimeError("expected QA064 publish gate to be ready")
    if "deterministic" not in setup["evidence_modes"]:
        raise RuntimeError("expected deterministic evidence mode")
    if "model backed safe" not in setup["evidence_modes"]:
        raise RuntimeError("expected model-backed safe evidence mode")
    if acme["sessions"]:
        raise RuntimeError("expected template QA to leave Acme sessions empty")
    if globex["template_setup"]["status"] != "not_installed":
        raise RuntimeError("expected Globex template to remain uninstalled")
    if denied_status != 403:
        raise RuntimeError("expected cross-tenant template denial")
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "qa_id": "qa064",
                "acme_template_status": setup["status"],
                "acme_session_count": len(acme["sessions"]),
                "globex_template_status": globex["template_setup"]["status"],
                "cross_tenant_denial_status": denied_status,
                "workflow_draft_id": setup["workflow_draft_id"],
                "latest_run_id": setup["latest_run_id"],
                "evidence_modes": setup["evidence_modes"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Verified QA064 design review template evidence")
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


def _post_denied_status() -> int:
    request = urllib.request.Request(
        f"{BASE_URL}/admin/design-reviews/templates/council/install",
        data=json.dumps(
            {
                "tenant_id": ACME_TENANT_ID,
                "idempotency_key": "qa064-cross-tenant-denied",
            }
        ).encode("utf-8"),
        headers={**GLOBEX_HEADERS, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10):
            return 200
    except urllib.error.HTTPError as exc:
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main())
