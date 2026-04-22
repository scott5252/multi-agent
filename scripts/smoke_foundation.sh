#!/usr/bin/env bash
set -euo pipefail

export base_url="${BASE_URL:-http://127.0.0.1:8000}"

printf 'Smoke testing %s\n' "$base_url"
curl --fail --silent "$base_url/health/live" | uv run python -m json.tool
curl --silent "$base_url/health/ready" | uv run python -m json.tool
curl --fail --silent "$base_url/version" | uv run python -m json.tool
curl --fail --silent "$base_url/dependencies" | uv run python -m json.tool
