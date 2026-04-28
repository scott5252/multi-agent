from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from urllib.parse import parse_qsl, urlsplit

from multi_agent_platform.model_providers.models import ErrorCategory


class AllowlistError(ValueError):
    def __init__(self, message: str, *, category: ErrorCategory) -> None:
        super().__init__(message)
        self.category = category


@dataclass(frozen=True, slots=True)
class LocalEndpointAllowlist:
    schemes: tuple[str, ...]
    hosts: tuple[str, ...]
    ports: tuple[int, ...]
    cidrs: tuple[str, ...] = ()


def validate_local_endpoint(
    base_url: str,
    allowlist: LocalEndpointAllowlist,
) -> str:
    parsed = urlsplit(base_url)
    if parsed.scheme not in allowlist.schemes:
        raise AllowlistError(
            "local provider scheme is not allowlisted",
            category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
        )
    if parsed.username or parsed.password:
        raise AllowlistError(
            "local provider URL cannot include userinfo",
            category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
        )
    if not parsed.hostname:
        raise AllowlistError(
            "local provider host is required",
            category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
        )
    if parsed.port is not None and parsed.port not in allowlist.ports:
        raise AllowlistError(
            "local provider port is not allowlisted",
            category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
        )
    if parsed.hostname not in allowlist.hosts and not _cidr_allows(
        parsed.hostname, allowlist.cidrs
    ):
        raise AllowlistError(
            "local provider host is not allowlisted",
            category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
        )
    for key, _value in parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if any(marker in lowered for marker in ("secret", "token", "key", "auth")):
            raise AllowlistError(
                "local provider URL cannot include secret-like query parameters",
                category=ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
            )
    return base_url.rstrip("/")


def _cidr_allows(hostname: str, cidrs: tuple[str, ...]) -> bool:
    try:
        address = ip_address(hostname)
    except ValueError:
        return False
    return any(address in ip_network(cidr, strict=False) for cidr in cidrs)
