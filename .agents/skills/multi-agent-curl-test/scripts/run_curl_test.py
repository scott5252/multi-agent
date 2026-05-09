#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000001"
PLATFORM_APPROVER_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000002"
ACME_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000003"
GLOBEX_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000004"
AUDITOR_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000005"
SEEDED_MEMBER_PRINCIPAL_ID = "00000000-0000-0000-0000-000000000006"
SEEDED_MEMBERSHIP_ID = "33333333-0209-0209-0209-333333333333"
SAVED_FILTER_ID = "44444444-0214-0214-0214-444444444444"
BREAKER_ID = "22222222-1515-1515-1515-222222222222"
DEAD_LETTER_ID = "33333333-1515-1515-1515-333333333333"


@dataclass(frozen=True)
class CurlStep:
    label: str
    code: str
    expected_status_groups: tuple[tuple[str, ...], ...]


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root(args.repo_root)
    run_dir = make_run_dir(repo_root, args.output_dir)
    app_env = build_app_env(args, repo_root)
    base_url = f"http://{args.host}:{args.port}"

    require_command("uv")
    require_command("curl")
    require_command("jq")
    require_command("bash")

    if not args.skip_uv_sync:
        run(["uv", "sync"], cwd=repo_root, env=app_env)

    recreate_database(args)
    run(["uv", "run", "alembic", "upgrade", "head"], cwd=repo_root, env=app_env)
    seed_database(args)

    killed_pids: list[int] = []
    if not args.no_kill_existing_server:
        killed_pids = kill_port_processes(args.port)

    server = start_server(args, repo_root, run_dir, app_env)
    try:
        wait_for_server(base_url, server, run_dir)
        steps = parse_curl_testing(repo_root / "curl_testing.md")
        if not steps:
            raise RuntimeError("No curl steps were found in curl_testing.md")
        generated_script = write_generated_script(
            steps=steps,
            run_dir=run_dir,
            base_url=base_url,
        )
        result = run(
            ["bash", str(generated_script)],
            cwd=repo_root,
            env={**app_env, "RUN_DIR": str(run_dir), "BASE_URL": base_url},
            check=False,
        )
        print_server_restart_note(killed_pids, server.pid)
        return result.returncode
    finally:
        if not args.keep_server_running:
            terminate_process(server)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run curl_testing.md against a fresh multi_agent_curl_test database."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--db-name",
        default=os.getenv("MULTI_AGENT_CURL_TEST_DB", "multi_agent_curl_test"),
    )
    parser.add_argument("--pg-host", default=os.getenv("PGHOST", "127.0.0.1"))
    parser.add_argument(
        "--pg-port",
        type=int,
        default=int(os.getenv("PGPORT", "5432")),
    )
    parser.add_argument("--pg-user", default=os.getenv("PGUSER", "postgres"))
    parser.add_argument("--pg-password", default=os.getenv("PGPASSWORD", "postgres"))
    parser.add_argument(
        "--host",
        default=os.getenv("MULTI_AGENT_CURL_TEST_HOST", "127.0.0.1"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MULTI_AGENT_CURL_TEST_PORT", "8000")),
    )
    parser.add_argument("--skip-uv-sync", action="store_true")
    parser.add_argument("--keep-server-running", action="store_true")
    parser.add_argument("--no-kill-existing-server", action="store_true")
    return parser.parse_args()


def find_repo_root(explicit: Path | None) -> Path:
    candidates = [explicit.resolve()] if explicit is not None else []
    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])
    for candidate in candidates:
        if (
            (candidate / "pyproject.toml").exists()
            and (candidate / "curl_testing.md").exists()
            and (candidate / "system_architecture.md").exists()
        ):
            return candidate
    raise RuntimeError("Could not find repository root containing curl_testing.md")


def make_run_dir(repo_root: Path, output_dir: Path | None) -> Path:
    if output_dir is not None:
        run_dir = output_dir.resolve()
    else:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_dir = repo_root / ".data" / "curl_test_runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required command not found on PATH: {name}")


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(shlex.quote(part) for part in command), flush=True)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result


def app_database_url(args: argparse.Namespace) -> str:
    user = quote(args.pg_user, safe="")
    password = quote(args.pg_password, safe="")
    return f"postgresql+psycopg://{user}:{password}@{args.pg_host}:{args.pg_port}/{args.db_name}"


def psycopg_dsn(args: argparse.Namespace, dbname: str | None = None) -> str:
    user = quote(args.pg_user, safe="")
    password = quote(args.pg_password, safe="")
    db = quote(dbname or args.db_name, safe="")
    return f"postgresql://{user}:{password}@{args.pg_host}:{args.pg_port}/{db}"


def validate_database_name(db_name: str) -> None:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,62}", db_name) is None:
        raise ValueError("Database name must be a safe PostgreSQL identifier")


def recreate_database(args: argparse.Namespace) -> None:
    validate_database_name(args.db_name)
    try:
        import psycopg
        from psycopg import sql
    except ImportError as exc:
        raise RuntimeError(
            "psycopg is required. Run this script with `uv run python` "
            "from the repo root."
        ) from exc

    print(f"Recreating PostgreSQL database {args.db_name!r}", flush=True)
    with psycopg.connect(psycopg_dsn(args, "postgres"), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_terminate_backend(pid) "
                "FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (args.db_name,),
            )
            cur.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(args.db_name)
                )
            )
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(args.db_name))
            )


def build_app_env(args: argparse.Namespace, repo_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    storage_root = repo_root / ".data" / "curl_test_artifacts"
    env.update(
        {
            "APP_ENV": "local",
            "AUTH_MODE": "local_principal",
            "DATABASE_URL": app_database_url(args),
            "FILESYSTEM_STORAGE_ROOT": str(storage_root),
            "STORAGE_PROVIDER": "filesystem",
            "SECRET_PROVIDER": "static",
            "STATIC_SECRETS_JSON": json.dumps(
                {
                    "telegram/bot-token": "curl-test-telegram-token",
                    "openai/curl-test": "curl-test-openai-token",
                    "example/api-key": "fixture-secret",
                }
            ),
            "TELEGRAM_WEBHOOK_SECRET": "local-dev-secret",
            "TELEGRAM_PROVIDER_TOKEN_REF": "telegram/bot-token",
            "LOCAL_PRINCIPAL_CATALOG_JSON": json.dumps(local_principal_catalog()),
            "APP_VERSION": "0.1.0",
            "COMMIT_SHA": "curl-test",
            "BUILD_TIME": "2026-05-04T00:00:00+00:00",
        }
    )
    return env


def local_principal_catalog() -> dict[str, dict[str, object]]:
    platform_permissions = sorted(
        {
            "platform:admin",
            "tenant:read",
            "tenant:admin",
            "admin:role-grants:write",
            "admin:support-overrides:write",
            "admin:support-overrides:approve",
            "membership-admin:read",
            "membership-admin:invite",
            "membership-admin:write",
            "membership-admin:grants",
            "membership-admin:audit",
            "skill-registry:publish",
            "skill-registry:quarantine",
            "skill-registry:audit",
            "skill-execution:read",
            "agent-tests:manage",
            "agent-tests:run",
            "agent-tests:read",
            "agent-tests:gate",
            "usage:read",
            "usage:export",
            "telegram-config:read",
            "telegram-config:write",
            "telegram-config:tokens",
            "telegram-config:diagnostics",
            "briefing-preferences:read",
            "briefing-preferences:write",
            "briefing-preferences:export",
            "briefing-preferences:resolve",
            "operations:read",
            "operations:logs",
            "operations:export",
        }
    )
    tenant_permissions = sorted(
        {
            "tenant:read",
            "tenant:admin",
            "membership-admin:read",
            "membership-admin:invite",
            "membership-admin:write",
            "membership-admin:grants",
            "membership-admin:audit",
            "skill-registry:install",
            "skill-registry:bind",
            "skill-registry:audit",
            "skill-execution:read",
            "agent-tests:manage",
            "agent-tests:run",
            "agent-tests:read",
            "agent-tests:gate",
            "usage:read",
            "usage:export",
            "telegram-config:read",
            "telegram-config:write",
            "telegram-config:tokens",
            "telegram-config:diagnostics",
            "briefing-preferences:read",
            "briefing-preferences:write",
            "briefing-preferences:export",
            "briefing-preferences:resolve",
        }
    )
    return {
        "platform-admin": {
            "catalog_key": "platform-admin",
            "display_name": "Platform Admin",
            "role_codes": ["platform_admin"],
            "permission_codes": platform_permissions,
        },
        "platform-approver": {
            "catalog_key": "platform-approver",
            "display_name": "Platform Approver",
            "role_codes": ["platform_admin"],
            "permission_codes": platform_permissions,
        },
        "tenant-admin-acme": {
            "catalog_key": "tenant-admin-acme",
            "display_name": "Acme Tenant Admin",
            "tenant_id": ACME_TENANT_ID,
            "org_id": "org-acme",
            "role_codes": ["tenant_user", "tenant_admin"],
            "permission_codes": tenant_permissions,
        },
        "tenant-admin-globex": {
            "catalog_key": "tenant-admin-globex",
            "display_name": "Globex Tenant Admin",
            "tenant_id": GLOBEX_TENANT_ID,
            "org_id": "org-globex",
            "role_codes": ["tenant_user", "tenant_admin"],
            "permission_codes": tenant_permissions,
        },
        "auditor": {
            "catalog_key": "auditor",
            "display_name": "Operations Auditor",
            "role_codes": ["auditor"],
            "permission_codes": [
                "operations:read",
                "operations:logs",
                "operations:export",
            ],
        },
    }


def seed_database(args: argparse.Namespace) -> None:
    try:
        import psycopg
        from psycopg.types.json import Json
    except ImportError as exc:
        raise RuntimeError(
            "psycopg is required. Run this script with `uv run python` "
            "from the repo root."
        ) from exc

    print("Seeding tenants, local principals, and curl placeholders", flush=True)
    with psycopg.connect(psycopg_dsn(args)) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tenants (
                    tenant_id, slug, display_name, status, created_at, updated_at
                )
                VALUES
                    (
                        %s, 'acme', 'Acme', 'active',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ),
                    (
                        %s, 'globex', 'Globex', 'active',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                ON CONFLICT (tenant_id) DO UPDATE
                SET slug = EXCLUDED.slug,
                    display_name = EXCLUDED.display_name,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (ACME_TENANT_ID, GLOBEX_TENANT_ID),
            )
            for principal_id, subject, display_name, email in (
                (PLATFORM_PRINCIPAL_ID, "platform-admin", "Platform Admin", None),
                (
                    PLATFORM_APPROVER_PRINCIPAL_ID,
                    "platform-approver",
                    "Platform Approver",
                    None,
                ),
                (ACME_PRINCIPAL_ID, "tenant-admin-acme", "Acme Tenant Admin", None),
                (
                    GLOBEX_PRINCIPAL_ID,
                    "tenant-admin-globex",
                    "Globex Tenant Admin",
                    None,
                ),
                (AUDITOR_PRINCIPAL_ID, "auditor", "Operations Auditor", None),
                (
                    SEEDED_MEMBER_PRINCIPAL_ID,
                    "curl-seeded-member",
                    "Curl Seeded Member",
                    "seeded-member@example.com",
                ),
            ):
                cur.execute(
                    """
                    INSERT INTO principal_identities (
                        principal_identity_id,
                        auth_provider,
                        external_subject,
                        display_name,
                        email,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, 'LOCAL_PRINCIPAL', %s, %s, %s, 'ACTIVE',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (external_subject) DO UPDATE
                    SET display_name = EXCLUDED.display_name,
                        email = EXCLUDED.email,
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (principal_id, subject, display_name, email),
                )
            cur.execute(
                """
                INSERT INTO tenant_memberships (
                    tenant_membership_id,
                    tenant_id,
                    principal_identity_id,
                    invitation_id,
                    status,
                    revision_token,
                    membership_source,
                    created_by_principal_id,
                    updated_by_principal_id,
                    suspended_at,
                    removed_at,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s, %s, %s, NULL, 'active', 'curl-seeded-membership',
                    'admin_assignment', 'platform-admin', 'platform-admin',
                    NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (tenant_id, principal_identity_id) DO UPDATE
                SET status = EXCLUDED.status,
                    revision_token = EXCLUDED.revision_token,
                    updated_by_principal_id = EXCLUDED.updated_by_principal_id,
                    suspended_at = NULL,
                    removed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (SEEDED_MEMBERSHIP_ID, ACME_TENANT_ID, SEEDED_MEMBER_PRINCIPAL_ID),
            )
            cur.execute(
                """
                INSERT INTO admin_saved_filters (
                    admin_saved_filter_id,
                    principal_identity_id,
                    principal_id,
                    admin_area,
                    filter_key,
                    scope_type,
                    tenant_id,
                    display_name,
                    criteria,
                    safe_summary,
                    criteria_schema_version,
                    last_restored_at,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s, %s, 'tenant-admin-acme', 'workflows', 'curl-workflows',
                    'tenant', %s, 'Curl workflow draft filter',
                    %s, %s, '2026-04-27', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (admin_saved_filter_id) DO UPDATE
                SET criteria = EXCLUDED.criteria,
                    safe_summary = EXCLUDED.safe_summary,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    SAVED_FILTER_ID,
                    ACME_PRINCIPAL_ID,
                    ACME_TENANT_ID,
                    Json({"status": "draft"}),
                    Json({"status": "draft"}),
                ),
            )
        conn.commit()


def kill_port_processes(port: int) -> list[int]:
    lsof = shutil.which("lsof")
    if lsof is None:
        print("lsof not found; skipping existing-server shutdown check", flush=True)
        return []
    result = subprocess.run(
        [lsof, "-ti", f"tcp:{port}"],
        text=True,
        capture_output=True,
        check=False,
    )
    pids = sorted(
        {int(line) for line in result.stdout.splitlines() if line.strip().isdigit()}
    )
    if not pids:
        return []
    print(f"Stopping existing process(es) on port {port}: {pids}", flush=True)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    deadline = time.time() + 10
    while time.time() < deadline:
        alive = [pid for pid in pids if process_alive(pid)]
        if not alive:
            return pids
        time.sleep(0.25)
    for pid in pids:
        if process_alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    return pids


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def start_server(
    args: argparse.Namespace,
    repo_root: Path,
    run_dir: Path,
    app_env: dict[str, str],
) -> subprocess.Popen[str]:
    log_path = run_dir / "server.log"
    log_file = log_path.open("w", encoding="utf-8")
    command = [
        "uv",
        "run",
        "uvicorn",
        "multi_agent_platform.api.main:app",
        "--host",
        args.host,
        "--port",
        str(args.port),
    ]
    print("$ " + " ".join(shlex.quote(part) for part in command), flush=True)
    return subprocess.Popen(
        command,
        cwd=repo_root,
        env=app_env,
        text=True,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )


def wait_for_server(
    base_url: str,
    server: subprocess.Popen[str],
    run_dir: Path,
) -> None:
    deadline = time.time() + 60
    url = f"{base_url}/health/live"
    while time.time() < deadline:
        if server.poll() is not None:
            log_tail = tail(run_dir / "server.log", 80)
            raise RuntimeError(
                f"uvicorn exited before becoming ready. Server log tail:\n{log_tail}"
            )
        try:
            with urlopen(url, timeout=1.0) as response:
                if response.status == 200:
                    print(f"Server ready at {base_url}", flush=True)
                    return
        except URLError:
            time.sleep(0.5)
        except TimeoutError:
            time.sleep(0.5)
    log_tail = tail(run_dir / "server.log", 80)
    raise RuntimeError(f"Timed out waiting for {url}. Server log tail:\n{log_tail}")


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def parse_curl_testing(path: Path) -> list[CurlStep]:
    text = path.read_text(encoding="utf-8")
    heading_pattern = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    headings = list(heading_pattern.finditer(text))
    steps: list[CurlStep] = []
    for index, match in enumerate(headings):
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[start:end]
        code_blocks = re.findall(r"```bash\n(.*?)```", body, flags=re.DOTALL)
        curl_blocks = [
            block.strip()
            for block in code_blocks
            if re.search(r"(^|\n)\s*(export\s+\w+=.*)?curl\b|(^|\n).*[$(]curl\b", block)
            or " curl " in block
        ]
        if not curl_blocks:
            continue
        expected = parse_expected_status_groups(body)
        steps.append(
            CurlStep(
                label=match.group(1).strip(),
                code="\n\n".join(curl_blocks),
                expected_status_groups=expected,
            )
        )
    return steps


def parse_expected_status_groups(body: str) -> tuple[tuple[str, ...], ...]:
    groups: list[tuple[str, ...]] = []
    for line in body.splitlines():
        if "Expected" not in line:
            continue
        codes = tuple(re.findall(r"`([0-9]{3})`", line))
        if codes:
            groups.append(codes)
    return tuple(groups)


def write_generated_script(
    *,
    steps: Iterable[CurlStep],
    run_dir: Path,
    base_url: str,
) -> Path:
    script_path = run_dir / "generated_curl_walkthrough.sh"
    lines = [bash_preamble(base_url)]
    for step in steps:
        expected = ";".join(",".join(group) for group in step.expected_status_groups)
        lines.append("")
        lines.append(f"start_step {shlex.quote(step.label)} {shlex.quote(expected)}")
        lines.append(step.code)
        if step.label == "4.1 POST /runtime/runs":
            lines.append("seed_runtime_audit_fixture")
        lines.append("end_step")
    lines.append("")
    lines.append("print_summary")
    lines.append("")
    script_path.write_text("\n".join(lines), encoding="utf-8")
    script_path.chmod(0o755)
    return script_path


def bash_preamble(base_url: str) -> str:
    return f"""#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s inherit_errexit 2>/dev/null || true

export BASE_URL="${{BASE_URL:-{base_url}}}"
export ACME_TENANT_ID="${{ACME_TENANT_ID:-{ACME_TENANT_ID}}}"
export GLOBEX_TENANT_ID="${{GLOBEX_TENANT_ID:-{GLOBEX_TENANT_ID}}}"
export PLATFORM_HEADER="${{PLATFORM_HEADER:-X-Local-Principal: platform-admin}}"
: "${{PLATFORM_APPROVER_HEADER:=X-Local-Principal: platform-approver}}"
export PLATFORM_APPROVER_HEADER
export ACME_HEADER="${{ACME_HEADER:-X-Local-Principal: tenant-admin-acme}}"
export GLOBEX_HEADER="${{GLOBEX_HEADER:-X-Local-Principal: tenant-admin-globex}}"
export AUDITOR_HEADER="${{AUDITOR_HEADER:-X-Local-Principal: auditor}}"
export JSON_HEADER="${{JSON_HEADER:-Content-Type: application/json}}"
export TELEGRAM_SECRET="${{TELEGRAM_SECRET:-local-dev-secret}}"
export TENANT_MEMBERSHIP_ID="${{TENANT_MEMBERSHIP_ID:-{SEEDED_MEMBERSHIP_ID}}}"
export FILTER_ID="${{FILTER_ID:-{SAVED_FILTER_ID}}}"
export BREAKER_ID="${{BREAKER_ID:-{BREAKER_ID}}}"
export DEAD_LETTER_ID="${{DEAD_LETTER_ID:-{DEAD_LETTER_ID}}}"

STATUS_FILE="$RUN_DIR/statuses.current"
OUTPUTS_FILE="$RUN_DIR/outputs.current"
SUCCEEDED_FILE="$RUN_DIR/succeeded.tsv"
FAILED_FILE="$RUN_DIR/failed.tsv"
: > "$SUCCEEDED_FILE"
: > "$FAILED_FILE"
CURRENT_STEP=""
EXPECTED_STATUS_GROUPS=""
CURL_SEQ=0

handle_error() {{
  local rc="$1"
  local line="$2"
  if [ -n "$CURRENT_STEP" ]; then
    record_failure "command exited with status $rc at generated line $line"
  fi
  exit "$rc"
}}
trap 'handle_error "$?" "$LINENO"' ERR

start_step() {{
  CURRENT_STEP="$1"
  EXPECTED_STATUS_GROUPS="$2"
  : > "$STATUS_FILE"
  : > "$OUTPUTS_FILE"
  echo
  echo "==> $CURRENT_STEP"
}}

curl() {{
  CURL_SEQ=$((CURL_SEQ + 1))
  local output_file="$RUN_DIR/curl-${{CURL_SEQ}}.out"
  local err_file="$RUN_DIR/curl-${{CURL_SEQ}}.err"
  local is_sse=0
  local arg
  for arg in "$@"; do
    case "$arg" in
      *"/events"*|-N) is_sse=1 ;;
    esac
  done
  local max_time="${{CURL_MAX_TIME:-30}}"
  if [ "$is_sse" = "1" ]; then
    max_time="${{CURL_SSE_MAX_TIME:-5}}"
  fi
  printf "%s\\t%s\\n" "$output_file" "$is_sse" >> "$OUTPUTS_FILE"
  set +e
  command curl --max-time "$max_time" "$@" \\
    --write-out "%{{stderr}}__CURL_STATUS__:%{{http_code}}\\n" \\
    2> >(awk -v f="$STATUS_FILE" -v e="$err_file" '
      /__CURL_STATUS__:/ {{ sub(/^.*__CURL_STATUS__:/, ""); print $0 >> f; next }}
      {{ print > "/dev/stderr"; print >> e }}
    ') | tee "$output_file"
  local rc="${{PIPESTATUS[0]}}"
  set -e
  if [ "$rc" -eq 28 ] && [ "$is_sse" = "1" ]; then
    return 0
  fi
  return "$rc"
}}

status_in_group() {{
  local status="$1"
  local group="$2"
  local allowed
  IFS=',' read -ra allowed <<< "$group"
  local item
  for item in "${{allowed[@]}}"; do
    if [ "$status" = "$item" ]; then
      return 0
    fi
  done
  return 1
}}

status_is_success() {{
  local status="$1"
  case "$status" in
    2??|3??) return 0 ;;
    *) return 1 ;;
  esac
}}

validate_statuses() {{
  local statuses=()
  local expected=()
  local line
  while IFS= read -r line; do
    [ -n "$line" ] && statuses+=("$line")
  done < "$STATUS_FILE"
  if [ -n "$EXPECTED_STATUS_GROUPS" ]; then
    IFS=';' read -ra expected <<< "$EXPECTED_STATUS_GROUPS"
  fi

  local actual_count="${{#statuses[@]}}"
  local expected_count="${{#expected[@]}}"
  if [ "$actual_count" -eq 0 ]; then
    record_failure "no curl status was captured"
  fi

  local offset=0
  if [ "$expected_count" -eq 0 ]; then
    offset="$actual_count"
  elif [ "$actual_count" -eq "$expected_count" ]; then
    offset=0
  elif [ "$actual_count" -gt "$expected_count" ]; then
    offset=$((actual_count - expected_count))
  else
    record_failure \\
      "expected $expected_count HTTP status value(s), captured $actual_count"
  fi

  local i=0
  while [ "$i" -lt "$offset" ]; do
    if ! status_is_success "${{statuses[$i]}}"; then
      record_failure \\
        "setup curl returned HTTP ${{statuses[$i]}} before expected-status checks"
    fi
    i=$((i + 1))
  done

  if [ "$expected_count" -gt 0 ]; then
    i=0
    while [ "$i" -lt "$expected_count" ]; do
      local actual_index=$((offset + i))
      if ! status_in_group "${{statuses[$actual_index]}}" "${{expected[$i]}}"; then
        record_failure \\
          "expected HTTP ${{expected[$i]}}, got ${{statuses[$actual_index]}}"
      fi
      i=$((i + 1))
    done
  fi
}}

validate_json_outputs() {{
  local output_file
  local is_sse
  while IFS=$'\\t' read -r output_file is_sse; do
    [ -z "${{output_file:-}}" ] && continue
    [ "$is_sse" = "1" ] && continue
    [ ! -s "$output_file" ] && continue
    if head -c 5 "$output_file" | grep -q '^HTTP/'; then
      continue
    fi
    local first
    first="$(python3 - "$output_file" <<'PY'
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").lstrip()
print(data[:1])
PY
)"
    if [ "$first" = "{{" ] || [ "$first" = "[" ]; then
      python3 -m json.tool "$output_file" >/dev/null || \\
        record_failure "invalid JSON output in $output_file"
    fi
  done < "$OUTPUTS_FILE"
}}

joined_statuses() {{
  paste -sd ',' "$STATUS_FILE" 2>/dev/null || true
}}

end_step() {{
  validate_statuses
  validate_json_outputs
  printf "%s\\t%s\\n" "$CURRENT_STEP" "$(joined_statuses)" >> "$SUCCEEDED_FILE"
  CURRENT_STEP=""
  EXPECTED_STATUS_GROUPS=""
}}

record_failure() {{
  trap - ERR
  set +e
  local reason="$1"
  printf "%s\\t%s\\t%s\\n" \\
    "$CURRENT_STEP" "$reason" "$(joined_statuses)" >> "$FAILED_FILE"
  print_summary
  local last_output
  last_output="$(tail -n 1 "$OUTPUTS_FILE" | awk -F '\\t' '{{print $1}}')"
  if [ -n "$last_output" ] && [ -f "$last_output" ]; then
    echo
    echo "Last captured output:"
    tail -n 80 "$last_output"
  fi
  exit 1
}}

print_summary() {{
  echo
  echo "=== multi-agent curl test summary ==="
  echo "Base URL: $BASE_URL"
  echo "Run directory: $RUN_DIR"
  echo
  echo "Succeeded commands:"
  if [ -s "$SUCCEEDED_FILE" ]; then
    awk -F '\\t' '{{ printf "  - %s [%s]\\n", $1, $2 }}' "$SUCCEEDED_FILE"
  else
    echo "  (none)"
  fi
  echo
  echo "Failed commands:"
  if [ -s "$FAILED_FILE" ]; then
    awk -F '\\t' '{{ printf "  - %s: %s [%s]\\n", $1, $2, $3 }}' "$FAILED_FILE"
  else
    echo "  (none)"
  fi
}}
""" + runtime_audit_seed_bash()


def runtime_audit_seed_bash() -> str:
    return r'''

seed_runtime_audit_fixture() {
  if [ -z "${RUNTIME_RUN_ID:-}" ]; then
    echo "RUNTIME_RUN_ID is not set; cannot seed audit debugging fixture" >&2
    return 1
  fi
  uv run python - <<'PY'
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Json


def uuid_or_none(value: str | None) -> str | None:
    if not value:
        return None
    return str(UUID(value))


runtime_payload: dict[str, object] = {}
try:
    with open("/tmp/curl-runtime-run.json", encoding="utf-8") as handle:
        runtime_payload = json.load(handle)
except FileNotFoundError:
    runtime_payload = {}

database_url = os.environ["DATABASE_URL"].replace(
    "postgresql+psycopg://", "postgresql://", 1
)
tenant_id = str(UUID(os.environ["ACME_TENANT_ID"]))
workflow_run_id = str(UUID(os.environ["RUNTIME_RUN_ID"]))
workflow_version_bundle_id = uuid_or_none(os.environ.get("WORKFLOW_VERSION_BUNDLE_ID"))
run_bundle_id = uuid_or_none(
    str(runtime_payload.get("run_bundle_id"))
    if runtime_payload.get("run_bundle_id")
    else None
)
run_bundle_id = run_bundle_id or str(uuid4())
bundle_digest = str(runtime_payload.get("bundle_digest") or "sha256:curl-runtime")
now = datetime.now(UTC)
coordinator_step_id = "77777777-b001-4b01-8001-777777777777"
specialist_step_id = "77777777-b002-4b01-8001-777777777777"
approval_step_id = "77777777-b003-4b01-8001-777777777777"
done_step_id = "77777777-b004-4b01-8001-777777777777"
workflow_document = {
    "workflow_key": "curl-triage-flow",
    "display_name": "Curl Triage Flow",
    "workflow_kind": "main_workflow",
    "entry_node_key": "coordinator",
    "roles": [
        {
            "role_key": "coordinator",
            "display_name": "Coordinator",
            "role_kind": "agent",
            "purpose": "Coordinate curl runtime work.",
            "input_contract_key": "request",
            "output_contract_key": "brief",
            "graph_node_keys": ["coordinator"],
        },
        {
            "role_key": "specialist",
            "display_name": "Specialist",
            "role_kind": "subagent",
            "purpose": "Review curl runtime context.",
            "input_contract_key": "brief",
            "output_contract_key": "result",
            "graph_node_keys": ["specialist"],
        },
    ],
    "contracts": [
        {"contract_key": "request", "json_schema": {"type": "object"}},
        {"contract_key": "brief", "json_schema": {"type": "object"}},
        {"contract_key": "result", "json_schema": {"type": "object"}},
    ],
    "nodes": [
        {
            "node_key": "coordinator",
            "node_type": "role",
            "display_name": "Coordinator",
            "role_key": "coordinator",
        },
        {
            "node_key": "specialist",
            "node_type": "role",
            "display_name": "Specialist",
            "role_key": "specialist",
        },
        {
            "node_key": "approval",
            "node_type": "approval",
            "display_name": "Approval",
            "approval_gate_key": "manager",
        },
        {"node_key": "done", "node_type": "terminal", "display_name": "Done"},
    ],
    "edges": [
        {
            "edge_key": "edge-coordinator-specialist",
            "source_node_key": "coordinator",
            "target_node_key": "specialist",
            "contract_key": "brief",
        },
        {
            "edge_key": "edge-specialist-approval",
            "source_node_key": "specialist",
            "target_node_key": "approval",
            "contract_key": "result",
        },
        {
            "edge_key": "edge-approval-done",
            "source_node_key": "approval",
            "target_node_key": "done",
        },
    ],
    "approval_gates": [
        {
            "approval_gate_key": "manager",
            "display_name": "Manager approval",
            "approver_scope": "tenant_admin",
            "resume_behavior": "resume_origin",
        }
    ],
}

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO runtime_execution_bundles (
                run_bundle_id,
                tenant_id,
                workflow_run_id,
                published_workflow_version_id,
                bundle_digest,
                workflow_version,
                subworkflow_versions,
                contract_versions,
                prompt_versions,
                model_config_versions,
                tool_policy_versions,
                retry_policy,
                checkpoint_policy,
                approval_timeout_policy,
                child_cancellation_policy,
                compiled_graph_ref,
                created_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, '{}', '{}', '{}', '{}', '{}',
                '{}', '{}', '{}', 'cascade_cancel', NULL, %s
            )
            ON CONFLICT (run_bundle_id)
            DO UPDATE SET
                workflow_version = EXCLUDED.workflow_version,
                bundle_digest = EXCLUDED.bundle_digest
            """,
            (
                run_bundle_id,
                tenant_id,
                workflow_run_id,
                workflow_version_bundle_id,
                bundle_digest,
                Json(
                    {
                        "document": workflow_document,
                        "workflow_key": "curl-triage-flow",
                        "workflow_lineage_id": os.environ.get("WORKFLOW_LINEAGE_ID"),
                    }
                ),
                now,
            ),
        )
        cur.execute(
            """
            INSERT INTO runtime_workflow_runs (
                workflow_run_id,
                tenant_id,
                scope_type,
                initiating_principal_id,
                run_bundle_id,
                status,
                current_step_id,
                current_checkpoint_id,
                pause_reason,
                terminal_reason,
                idempotency_key,
                trace_id,
                started_at,
                finished_at,
                created_at,
                updated_at
            )
            VALUES (
                %s, %s, 'tenant', 'tenant-admin-acme', %s, 'RUNNING',
                %s, NULL, NULL, NULL, 'runtime-curl-001',
                'trace-runtime-curl', %s, NULL, %s, %s
            )
            ON CONFLICT (workflow_run_id)
            DO UPDATE SET
                run_bundle_id = EXCLUDED.run_bundle_id,
                status = EXCLUDED.status,
                current_step_id = EXCLUDED.current_step_id,
                updated_at = EXCLUDED.updated_at
            """,
            (
                workflow_run_id,
                tenant_id,
                run_bundle_id,
                specialist_step_id,
                now,
                now,
                now,
            ),
        )
        for step_id, step_key, step_type, status, attempt, output_ref, error_ref in (
            (
                coordinator_step_id,
                "coordinator",
                "role",
                "SUCCEEDED",
                1,
                {"safe_summary": "Coordinator produced safe runtime evidence."},
                None,
            ),
            (
                specialist_step_id,
                "specialist",
                "role",
                "RETRY_SCHEDULED",
                1,
                None,
                {"safe_summary": "Specialist retry was summarized safely."},
            ),
            (
                approval_step_id,
                "approval",
                "approval",
                "PAUSED",
                1,
                None,
                None,
            ),
            (done_step_id, "done", "terminal", "PENDING", 1, None, None),
        ):
            cur.execute(
                """
                INSERT INTO runtime_run_steps (
                    run_step_id,
                    workflow_run_id,
                    tenant_id,
                    step_key,
                    step_type,
                    status,
                    attempt,
                    max_attempts,
                    next_retry_at,
                    input_ref,
                    output_ref,
                    error_ref,
                    checkpoint_before_id,
                    checkpoint_after_id,
                    finished_at,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, 3, NULL, %s, %s, %s,
                    NULL, NULL, %s, %s, %s
                )
                ON CONFLICT (workflow_run_id, step_key, attempt)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    input_ref = EXCLUDED.input_ref,
                    output_ref = EXCLUDED.output_ref,
                    error_ref = EXCLUDED.error_ref,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    step_id,
                    workflow_run_id,
                    tenant_id,
                    step_key,
                    step_type,
                    status,
                    attempt,
                    Json({"safe_summary": f"{step_key} received safe evidence."}),
                    Json(output_ref) if output_ref is not None else None,
                    Json(error_ref) if error_ref is not None else None,
                    now if status == "SUCCEEDED" else None,
                    now,
                    now,
                ),
            )
        for event_id, step_id, event_type, severity, summary in (
            (
                "77777777-c001-4b01-8001-777777777777",
                coordinator_step_id,
                "coordinator_completed",
                "info",
                "Coordinator completed with safe evidence.",
            ),
            (
                "77777777-c002-4b01-8001-777777777777",
                specialist_step_id,
                "specialist_retry_scheduled",
                "warning",
                "Specialist retry was scheduled safely.",
            ),
            (
                "77777777-c003-4b01-8001-777777777777",
                approval_step_id,
                "approval_paused",
                "warning",
                "Approval is paused for manager review.",
            ),
        ):
            cur.execute(
                """
                INSERT INTO runtime_timeline_events (
                    runtime_timeline_event_id,
                    tenant_id,
                    workflow_run_id,
                    run_step_id,
                    event_type,
                    severity,
                    payload,
                    trace_id,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'trace-runtime-curl', %s)
                ON CONFLICT (runtime_timeline_event_id)
                DO UPDATE SET
                    severity = EXCLUDED.severity,
                    payload = EXCLUDED.payload
                """,
                (
                    event_id,
                    tenant_id,
                    workflow_run_id,
                    step_id,
                    event_type,
                    severity,
                    Json({"safe_summary": summary}),
                    now,
                ),
            )
        cur.execute(
            """
            INSERT INTO runtime_handoff_envelopes (
                handoff_envelope_id,
                tenant_id,
                workflow_run_id,
                sender_step_id,
                receiver_step_key,
                contract_id,
                contract_version,
                contract_digest,
                status,
                payload_hash,
                payload_ref,
                validation_errors,
                created_at,
                validated_at,
                consumed_at
            )
            VALUES (
                %s, %s, %s, %s, 'specialist', 'brief', '1.0.0',
                %s, 'VALID', %s, %s, '[]', %s, %s, NULL
            )
            ON CONFLICT (handoff_envelope_id)
            DO UPDATE SET status = EXCLUDED.status, payload_ref = EXCLUDED.payload_ref
            """,
            (
                "77777777-d001-4b01-8001-777777777777",
                tenant_id,
                workflow_run_id,
                coordinator_step_id,
                "a" * 64,
                "b" * 64,
                Json({"safe_summary": "Coordinator sent safe context to Specialist."}),
                now,
                now,
            ),
        )
        cur.execute(
            """
            INSERT INTO runtime_side_effect_intents (
                side_effect_intent_id,
                tenant_id,
                workflow_run_id,
                run_step_id,
                intent_kind,
                idempotency_key,
                status,
                tool_policy_ref,
                delegated_credential_ref,
                request_ref,
                result_ref,
                error_ref,
                compensation_hook_ref,
                executed_at,
                created_at,
                updated_at
            )
            VALUES (
                %s, %s, %s, %s, 'read_only_lookup', 'curl-runtime-tool',
                'APPLIED', 'tool-policy:safe-lookup', NULL, NULL, %s, NULL,
                NULL, %s, %s, %s
            )
            ON CONFLICT (tenant_id, workflow_run_id, run_step_id, idempotency_key)
            DO UPDATE SET status = EXCLUDED.status, result_ref = EXCLUDED.result_ref
            """,
            (
                "77777777-e001-4b01-8001-777777777777",
                tenant_id,
                workflow_run_id,
                coordinator_step_id,
                Json({"safe_summary": "Read only lookup produced safe evidence."}),
                now,
                now,
                now,
            ),
        )
        cur.execute(
            """
            INSERT INTO runtime_approval_gates (
                approval_gate_id,
                tenant_id,
                workflow_run_id,
                run_step_id,
                status,
                approval_key,
                requested_action,
                approver_policy,
                timeout_behavior,
                decision_id,
                created_at,
                decided_at,
                expires_at
            )
            VALUES (
                %s, %s, %s, %s, 'PENDING', 'manager', %s, '{}', '{}',
                NULL, %s, NULL, NULL
            )
            ON CONFLICT (approval_gate_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                requested_action = EXCLUDED.requested_action
            """,
            (
                "77777777-f001-4b01-8001-777777777777",
                tenant_id,
                workflow_run_id,
                approval_step_id,
                Json({"safe_summary": "Manager approval is pending."}),
                now,
            ),
        )
        for interaction in (
            {
                "interaction_evidence_id": "77777777-a101-4b01-8001-777777777777",
                "source_node_key": "coordinator",
                "target_node_key": "specialist",
                "source_run_step_id": coordinator_step_id,
                "target_run_step_id": specialist_step_id,
                "interaction_kind": "HANDOFF",
                "status": "SENT",
                "sequence": 1,
                "safe_summary": "Coordinator sent safe context to Specialist.",
                "idempotency_key": "curl-runtime:handoff:coordinator-specialist:1",
            },
            {
                "interaction_evidence_id": "77777777-a102-4b01-8001-777777777777",
                "source_node_key": "specialist",
                "target_node_key": "approval",
                "source_run_step_id": specialist_step_id,
                "target_run_step_id": approval_step_id,
                "interaction_kind": "RESULT_RETURN",
                "status": "COMPLETED",
                "sequence": 2,
                "safe_summary": "Specialist returned safe review evidence.",
                "idempotency_key": "curl-runtime:result:specialist-approval:1",
            },
            {
                "interaction_evidence_id": "77777777-a103-4b01-8001-777777777777",
                "source_node_key": "approval",
                "target_node_key": None,
                "source_run_step_id": approval_step_id,
                "target_run_step_id": None,
                "interaction_kind": "APPROVAL_PAUSE",
                "status": "PAUSED",
                "sequence": 3,
                "safe_summary": "Manager approval paused the run safely.",
                "idempotency_key": "curl-runtime:approval-pause:manager:1",
            },
        ):
            cur.execute(
                """
                INSERT INTO runtime_interaction_evidence (
                    interaction_evidence_id,
                    tenant_id,
                    workflow_run_id,
                    source_node_key,
                    target_node_key,
                    source_run_step_id,
                    target_run_step_id,
                    timeline_event_id,
                    interaction_kind,
                    status,
                    sequence,
                    safe_summary,
                    classification,
                    payload_digest,
                    artifact_refs,
                    provenance,
                    idempotency_key,
                    occurred_at,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, %s, %s,
                    'safe-summary', %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (
                    tenant_id, workflow_run_id, idempotency_key
                )
                DO UPDATE SET
                    source_node_key = EXCLUDED.source_node_key,
                    target_node_key = EXCLUDED.target_node_key,
                    source_run_step_id = EXCLUDED.source_run_step_id,
                    target_run_step_id = EXCLUDED.target_run_step_id,
                    interaction_kind = EXCLUDED.interaction_kind,
                    status = EXCLUDED.status,
                    sequence = EXCLUDED.sequence,
                    safe_summary = EXCLUDED.safe_summary,
                    payload_digest = EXCLUDED.payload_digest,
                    artifact_refs = EXCLUDED.artifact_refs,
                    provenance = EXCLUDED.provenance,
                    occurred_at = EXCLUDED.occurred_at
                """,
                (
                    interaction["interaction_evidence_id"],
                    tenant_id,
                    workflow_run_id,
                    interaction["source_node_key"],
                    interaction["target_node_key"],
                    interaction["source_run_step_id"],
                    interaction["target_run_step_id"],
                    interaction["interaction_kind"],
                    interaction["status"],
                    interaction["sequence"],
                    interaction["safe_summary"],
                    "a" * 64,
                    Json([{"artifact_ref": "curl-runtime-safe-summary"}]),
                    Json({"source": "curl-runtime-audit-seed"}),
                    interaction["idempotency_key"],
                    now,
                    now,
                ),
            )
        cur.execute(
            """
            INSERT INTO audit_timeline_events (
                timeline_event_id,
                tenant_id,
                workflow_run_id,
                parent_run_id,
                run_step_id,
                sequence,
                event_category,
                run_status_after,
                origin_type,
                origin_ref,
                actor_principal_id,
                trace_id,
                correlation_id,
                source_event_id,
                occurred_at,
                recorded_at,
                criticality,
                safe_summary,
                safe_details,
                classification_version,
                supersedes_event_id
            )
            VALUES (
                %s, %s, %s, NULL, NULL, 1, 'started', 'running',
                'system', 'curl-test-seed', 'tenant-admin-acme',
                'trace-runtime-curl', NULL, 'curl-runtime-audit:started',
                %s, %s, 'runtime_required', 'Run moved to running',
                %s, 'audit-debugging-v1', NULL
            )
            ON CONFLICT (
                tenant_id, workflow_run_id, event_category, source_event_id
            )
            DO UPDATE SET
                sequence = EXCLUDED.sequence,
                run_status_after = EXCLUDED.run_status_after,
                trace_id = EXCLUDED.trace_id,
                recorded_at = EXCLUDED.recorded_at,
                safe_summary = EXCLUDED.safe_summary,
                safe_details = EXCLUDED.safe_details
            RETURNING timeline_event_id
            """,
            (
                str(uuid4()),
                tenant_id,
                workflow_run_id,
                now,
                now,
                Json({"status": "running", "source": "curl-runtime-audit-seed"}),
            ),
        )
        timeline_event_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO audit_version_bundle_snapshots (
                version_bundle_snapshot_id,
                tenant_id,
                workflow_run_id,
                workflow_lineage_id,
                workflow_version_bundle_id,
                execution_bundle_id,
                bundle_digest,
                workflow_version,
                contract_version_refs,
                prompt_version_refs,
                model_config_version_refs,
                tool_policy_version_refs,
                activation_state_at_acceptance,
                accepted_at,
                migration_record_refs,
                safe_summary
            )
            VALUES (
                %s, %s, %s, NULL, %s, %s, %s, %s, %s, %s, %s, %s,
                'active', %s, %s, %s
            )
            ON CONFLICT (tenant_id, workflow_run_id)
            DO UPDATE SET
                workflow_version_bundle_id = EXCLUDED.workflow_version_bundle_id,
                execution_bundle_id = EXCLUDED.execution_bundle_id,
                bundle_digest = EXCLUDED.bundle_digest,
                workflow_version = EXCLUDED.workflow_version,
                safe_summary = EXCLUDED.safe_summary
            """,
            (
                str(uuid4()),
                tenant_id,
                workflow_run_id,
                workflow_version_bundle_id,
                run_bundle_id,
                bundle_digest,
                Json(
                    {
                        "workflow_key": "curl-triage-flow",
                        "workflow_version_bundle_id": workflow_version_bundle_id,
                    }
                ),
                Json({}),
                Json({}),
                Json({}),
                Json({}),
                now,
                Json([]),
                Json(
                    {
                        "redaction_applied": True,
                        "timeline_event_id": str(timeline_event_id),
                    }
                ),
            ),
        )
    conn.commit()
PY
}
'''


def tail(path: Path, lines: int) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:])


def print_server_restart_note(killed_pids: list[int], server_pid: int) -> None:
    if killed_pids:
        print(f"Restarted server: stopped {killed_pids}, started pid {server_pid}")
    else:
        print(f"Started server pid {server_pid}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130) from None
