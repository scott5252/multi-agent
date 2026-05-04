from __future__ import annotations

from pathlib import Path

ALLOWED_PROVIDER_TRANSPORT_MODULES = {
    "src/multi_agent_platform/channels/telegram_delivery.py",
    "src/multi_agent_platform/model_providers/openai_adapter.py",
    "src/multi_agent_platform/model_providers/local_adapter.py",
    "src/multi_agent_platform/model_providers/adapters.py",
    "src/multi_agent_platform/model_providers/guardrails.py",
}

PROVIDER_TRANSPORT_PATTERNS = (
    "import httpx",
    "from httpx",
    "httpx.AsyncClient",
    "from openai",
    "import openai",
)


def scan_provider_call_violations(paths: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for root in paths:
        candidates = [root] if root.is_file() else sorted(root.rglob("*.py"))
        for path in candidates:
            normalized = path.as_posix()
            source = path.read_text()
            if normalized in ALLOWED_PROVIDER_TRANSPORT_MODULES:
                continue
            for pattern in PROVIDER_TRANSPORT_PATTERNS:
                if pattern in source:
                    findings.append(
                        {
                            "module_path": normalized,
                            "symbol_or_pattern": pattern,
                            "outcome": "blocked",
                        }
                    )
    return findings
