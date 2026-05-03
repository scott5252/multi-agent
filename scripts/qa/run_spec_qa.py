#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autopilot_config import JsonObject, load_config, repo_root_from


@dataclass
class ManagedProcess:
    process_id: str
    process: subprocess.Popen[str]
    log_handle: Any | None


def as_command(value: Any) -> str | list[str]:
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise SystemExit("command must be a string or a list of strings")


def command_display(command: str | list[str]) -> str:
    if isinstance(command, str):
        return command
    return " ".join(shlex.quote(part) for part in command)


def run_command(
    command_spec: JsonObject,
    *,
    cwd: Path,
    base_env: dict[str, str],
    dry_run: bool,
) -> None:
    command_id = str(command_spec.get("id", "unnamed-command"))
    command = as_command(command_spec.get("command"))
    expected_exit_code = int(command_spec.get("expect_exit_code", 0))
    timeout_seconds = int(command_spec.get("timeout_seconds", 120))
    expect_contains = command_spec.get("expect_contains", [])
    expect_not_contains = command_spec.get("expect_not_contains", [])

    if isinstance(expect_contains, str):
        expect_contains = [expect_contains]
    if isinstance(expect_not_contains, str):
        expect_not_contains = [expect_not_contains]

    env = base_env.copy()
    extra_env = command_spec.get("env", {})
    if not isinstance(extra_env, dict):
        raise SystemExit(f"{command_id}: env must be an object")
    env.update({str(key): str(value) for key, value in extra_env.items()})

    print(f"==> {command_id}: {command_display(command)}")
    if dry_run:
        return

    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        shell=isinstance(command, str),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )

    output = f"{completed.stdout}{completed.stderr}"
    if completed.returncode != expected_exit_code:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(
            f"{command_id}: expected exit {expected_exit_code}, "
            f"got {completed.returncode}"
        )

    for needle in expect_contains:
        if str(needle) not in output:
            raise SystemExit(f"{command_id}: expected output to contain {needle!r}")

    for needle in expect_not_contains:
        if str(needle) in output:
            raise SystemExit(
                f"{command_id}: output contained forbidden text {needle!r}"
            )


def readiness_ok(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return 200 <= response.status < 500
    except (urllib.error.URLError, TimeoutError):
        return False


def start_processes(
    config: JsonObject,
    *,
    cwd: Path,
    base_env: dict[str, str],
    dry_run: bool,
) -> list[ManagedProcess]:
    processes: list[ManagedProcess] = []
    for process_spec in config.get("processes", []):
        if not isinstance(process_spec, dict):
            raise SystemExit("each process entry must be an object")

        process_id = str(process_spec.get("id", "unnamed-process"))
        command = as_command(process_spec.get("command"))
        print(f"==> start {process_id}: {command_display(command)}")
        if dry_run:
            continue

        env = base_env.copy()
        extra_env = process_spec.get("env", {})
        if not isinstance(extra_env, dict):
            raise SystemExit(f"{process_id}: env must be an object")
        env.update({str(key): str(value) for key, value in extra_env.items()})

        log_handle = None
        stdout: Any = None
        stderr: Any = None
        log_file = process_spec.get("log_file")
        if log_file:
            log_path = Path(str(log_file)).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_handle = log_path.open("w", encoding="utf-8")
            stdout = log_handle
            stderr = subprocess.STDOUT

        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=isinstance(command, str),
            text=True,
            stdout=stdout,
            stderr=stderr,
        )
        processes.append(ManagedProcess(process_id, process, log_handle))

        readiness_url = process_spec.get("readiness_url")
        if readiness_url:
            timeout_seconds = int(process_spec.get("timeout_seconds", 30))
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise SystemExit(
                        f"{process_id}: process exited before readiness check passed"
                    )
                if readiness_ok(str(readiness_url)):
                    print(f"==> {process_id}: readiness passed")
                    break
                time.sleep(1)
            else:
                raise SystemExit(
                    f"{process_id}: readiness did not pass within {timeout_seconds}s"
                )

    return processes


def stop_processes(processes: list[ManagedProcess]) -> None:
    for managed in reversed(processes):
        if managed.process.poll() is None:
            print(f"==> stop {managed.process_id}")
            managed.process.terminate()
            try:
                managed.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                managed.process.kill()
                managed.process.wait(timeout=10)
        if managed.log_handle is not None:
            managed.log_handle.close()


def config_command_list(config: JsonObject, key: str) -> list[JsonObject]:
    values = config.get(key, [])
    if not isinstance(values, list):
        raise SystemExit(f"{key} must be a list")
    return values


def command_sections(config: JsonObject, include_quality: bool) -> list[JsonObject]:
    selected: list[JsonObject] = []
    selected.extend(config_command_list(config, "commands"))
    selected.extend(config_command_list(config, "extra_commands"))
    if include_quality:
        selected.extend(config_command_list(config, "quality_commands"))
        selected.extend(config_command_list(config, "extra_quality_commands"))
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Spec Kit API/curl and quality checks from validation config."
    )
    parser.add_argument("validation_file", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Run setup/API commands but skip quality_commands.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation_file = args.validation_file.resolve()
    if not validation_file.exists():
        raise SystemExit(f"validation file not found: {validation_file}")

    repo_root = (
        args.repo_root.resolve() if args.repo_root else repo_root_from(validation_file)
    )
    config = load_config(validation_file)
    env = os.environ.copy()
    env["SPECKIT_VALIDATION_FILE"] = str(validation_file)

    processes: list[ManagedProcess] = []
    try:
        for command_spec in config_command_list(config, "setup_commands"):
            if not isinstance(command_spec, dict):
                raise SystemExit("each setup command entry must be an object")
            run_command(
                command_spec,
                cwd=repo_root,
                base_env=env,
                dry_run=args.dry_run,
            )

        processes = start_processes(
            config,
            cwd=repo_root,
            base_env=env,
            dry_run=args.dry_run,
        )
        for command_spec in command_sections(
            config, include_quality=not args.skip_quality
        ):
            if not isinstance(command_spec, dict):
                raise SystemExit("each command entry must be an object")
            run_command(
                command_spec,
                cwd=repo_root,
                base_env=env,
                dry_run=args.dry_run,
            )
    finally:
        stop_processes(processes)

    print("Spec QA validation completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
