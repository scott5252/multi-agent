#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
config_file="$repo_root/.specify/extensions/qa-docs/qa-docs-config.yml"
local_config_file="$repo_root/.specify/extensions/qa-docs/qa-docs-config.local.yml"

read_config_int() {
  local key="$1"
  local env_key="$2"
  local fallback="$3"
  local resolved="$fallback"
  local cfg value

  for cfg in "$config_file" "$local_config_file"; do
    if [[ -f "$cfg" ]]; then
      value="$(sed -n "s/^[[:space:]]*$key:[[:space:]]*//p" "$cfg" | head -1)"
      if [[ "$value" =~ ^[0-9]+$ ]]; then
        resolved="$value"
      fi
    fi
  done

  if [[ -n "${!env_key:-}" ]]; then
    value="${!env_key}"
    if [[ "$value" =~ ^[0-9]+$ ]]; then
      resolved="$value"
    fi
  fi

  printf '%s\n' "$resolved"
}

fail() {
  printf 'QA document validation failed: %s\n' "$1" >&2
  exit 1
}

feature_dir="${1:-}"
if [[ -z "$feature_dir" ]]; then
  prereq="$("$repo_root/.specify/scripts/bash/check-prerequisites.sh" --json --require-tasks --include-tasks 2>/dev/null || true)"
  if [[ -n "$prereq" ]]; then
    feature_dir="$(printf '%s\n' "$prereq" | sed -n 's/.*"FEATURE_DIR"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  fi
fi

if [[ -z "$feature_dir" && -f "$repo_root/.specify/feature.json" ]]; then
  feature_dir="$(sed -n 's/.*"feature_directory"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$repo_root/.specify/feature.json" | head -1)"
fi

[[ -n "$feature_dir" ]] || fail "feature directory could not be resolved"
[[ "$feature_dir" = /* ]] || feature_dir="$repo_root/$feature_dir"
[[ -d "$feature_dir" ]] || fail "feature directory does not exist: $feature_dir"

spec_dir_name="$(basename "$feature_dir")"
spec_num="${spec_dir_name%%-*}"
[[ "$spec_num" =~ ^[0-9]{3}$ ]] || fail "feature directory must start with a three-digit spec number: $spec_dir_name"

qa_id="qa$spec_num"
guide_file="$feature_dir/$qa_id.md"
env_file="$feature_dir/.env.$qa_id"

[[ -s "$guide_file" ]] || fail "missing or empty guide: $guide_file"
[[ -s "$env_file" ]] || fail "missing or empty environment file: $env_file"

min_guide_lines="$(read_config_int "min_guide_lines" "SPECKIT_QA_DOCS_MIN_GUIDE_LINES" 180)"
min_env_lines="$(read_config_int "min_env_lines" "SPECKIT_QA_DOCS_MIN_ENV_LINES" 35)"
min_code_fences="$(read_config_int "min_code_fences" "SPECKIT_QA_DOCS_MIN_CODE_FENCES" 10)"
min_expected_markers="$(read_config_int "min_expected_markers" "SPECKIT_QA_DOCS_MIN_EXPECTED_MARKERS" 12)"

guide_lines="$(wc -l < "$guide_file" | tr -d ' ')"
env_lines="$(wc -l < "$env_file" | tr -d ' ')"
code_fences="$(grep -c '^```' "$guide_file" || true)"
expected_markers="$(grep -c 'Expected:' "$guide_file" || true)"

(( guide_lines >= min_guide_lines )) || fail "$guide_file has $guide_lines lines; expected at least $min_guide_lines"
(( env_lines >= min_env_lines )) || fail "$env_file has $env_lines lines; expected at least $min_env_lines"
(( code_fences >= min_code_fences )) || fail "$guide_file has $code_fences fenced code markers; expected at least $min_code_fences"
(( expected_markers >= min_expected_markers )) || fail "$guide_file has $expected_markers Expected: markers; expected at least $min_expected_markers"

required_headings=(
  "## Goal"
  "## What This Guide Covers"
  "## How To Use This Guide"
  "## Environment"
  "## Environment File Checklist"
  "## Shared QA Variables"
  "## Required Automated Evidence"
  "## Acceptance Evidence Template"
  "## Troubleshooting"
  "## Related Files"
)

for heading in "${required_headings[@]}"; do
  grep -Fq "$heading" "$guide_file" || fail "$guide_file missing required heading: $heading"
done

grep -Fq "$qa_id" "$guide_file" || fail "$guide_file does not reference $qa_id"
grep -Fq ".env.$qa_id" "$guide_file" || fail "$guide_file does not reference .env.$qa_id"
grep -Fq "/tmp/$qa_id-" "$guide_file" || fail "$guide_file does not save evidence under /tmp/$qa_id-*"
grep -Fq "What this proves:" "$guide_file" || fail "$guide_file missing 'What this proves:' reviewer notes"
grep -Fq "uv run ruff check ." "$guide_file" || fail "$guide_file missing Ruff check command"
grep -Fq "uv run ruff format --check ." "$guide_file" || fail "$guide_file missing Ruff format command"
grep -Fq "uv run mypy src" "$guide_file" || fail "$guide_file missing mypy command"
grep -Fq "uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90" "$guide_file" || fail "$guide_file missing full coverage command"

if grep -Eiq 'TODO|TBD|REPLACE_ME|INSERT_|<[^>]+>' "$guide_file"; then
  fail "$guide_file contains placeholder text"
fi

required_env_keys=(
  "APP_ENV="
  "APP_NAME="
  "API_HOST="
  "API_PORT="
  "AUTH_MODE=local_principal"
  "LOCAL_PRINCIPAL_HEADER="
  "LOCAL_PRINCIPAL_COOKIE_NAME="
  "LOCAL_PRINCIPAL_CATALOG_JSON="
  "DATABASE_URL="
  "RUNTIME_CHECKPOINTER_DATABASE_URL="
  "SECRET_PROVIDER="
  "STATIC_SECRETS_JSON="
  "STORAGE_PROVIDER="
  "FILESYSTEM_STORAGE_ROOT="
)

for key in "${required_env_keys[@]}"; do
  grep -Fq "$key" "$env_file" || fail "$env_file missing required key: $key"
done

grep -Fq "multi_agent_platform_$qa_id" "$env_file" || fail "$env_file must use database multi_agent_platform_$qa_id"
grep -Fq ".data/$qa_id-artifacts" "$env_file" || fail "$env_file must use .data/$qa_id-artifacts storage"
grep -Fq "$qa_id/" "$env_file" || fail "$env_file must use $qa_id secret references"

if grep -Eiq '(sk-[A-Za-z0-9]|AKIA[0-9A-Z]|BEGIN (RSA|OPENSSH|PRIVATE) KEY|prod\.|production)' "$env_file"; then
  fail "$env_file appears to contain a real credential or production reference"
fi

printf 'QA document validation passed for %s\n' "$feature_dir"
printf 'Guide: %s\n' "$guide_file"
printf 'Environment: %s\n' "$env_file"
