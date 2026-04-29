from __future__ import annotations

import json
import re
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|password|secret|token|refresh[_-]?token)\b"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)sk-[a-z0-9]{16,}"),
)
ALLOWED_ENTRYPOINT_TYPES = {"approved_tool_ref", "approved_mcp_ref"}
ALLOWED_SIDE_EFFECTS = {
    "read_only",
    "idempotent_write",
    "non_idempotent_write",
    "external_notification",
}
ALLOWED_CREDENTIAL_KINDS = {"secret_reference", "delegated_credential"}
ALLOWED_PERMISSION_TYPES = {
    "tool_access",
    "network_access",
    "credential_access",
    "tenant_data_access",
}
ALLOWED_FIXTURE_KINDS = {"static_input", "policy_preview", "safe_probe"}


class SkillManifestError(ValueError):
    """Raised when declarative skill manifest content is unsafe or malformed."""


class ManifestEntrypoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["approved_tool_ref", "approved_mcp_ref"]
    approved_integration_ref: str = Field(min_length=1, max_length=255)


class ToolDeclaration(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_id: str = Field(min_length=1, max_length=128)
    approved_integration_ref: str = Field(min_length=1, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    action_categories: tuple[str, ...] = Field(default_factory=tuple)
    input_contract_ref: str | None = None
    output_contract_ref: str | None = None
    side_effect_profile: str = "read_only"
    safe_usage: str = Field(min_length=1, max_length=2000)

    @field_validator("side_effect_profile")
    @classmethod
    def validate_side_effect_profile(cls, value: str) -> str:
        if value not in ALLOWED_SIDE_EFFECTS:
            raise ValueError("unknown side effect profile")
        return value


class NetworkRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_id: str
    action_category: str
    allowed_schemes: tuple[str, ...] = ("https",)
    allowed_domain_patterns: tuple[str, ...] = Field(default_factory=tuple)
    allowed_ports: tuple[int, ...] = (443,)
    required: bool = True
    safe_description: str = ""

    @field_validator("allowed_domain_patterns")
    @classmethod
    def normalize_domains(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(domain.lower().strip() for domain in value if domain)
        for domain in normalized:
            if "@" in domain or "://" in domain:
                raise ValueError(
                    "domain patterns cannot include schemes or credentials"
                )
            if domain.startswith("*.") and domain.count("*") > 1:
                raise ValueError("wildcard domains must be bounded")
        return normalized


class CredentialRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)

    requirement_key: str
    credential_kind: Literal["secret_reference", "delegated_credential"]
    tool_id: str
    action_category: str
    required: bool = True
    allowed_secret_reference_scopes: tuple[str, ...] = Field(default_factory=tuple)
    delegated_credential_scopes: tuple[str, ...] = Field(default_factory=tuple)
    rotation_policy: dict[str, Any] = Field(default_factory=dict)
    safe_description: str = ""


class RuntimePermission(BaseModel):
    model_config = ConfigDict(frozen=True)

    permission_key: str
    permission_type: Literal[
        "tool_access",
        "network_access",
        "credential_access",
        "tenant_data_access",
    ]
    tool_id: str
    action_category: str
    data_scope: str | None = None
    side_effect_level: str = "read_only"
    required: bool = True
    safe_description: str = ""


class TestFixture(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture_key: str
    tool_id: str
    action_category: str
    fixture_kind: Literal["static_input", "policy_preview", "safe_probe"]
    safe_input_summary: str
    fixture_artifact_ref: str | None = None
    fixture_digest: str | None = None
    requires_credentials: bool = False
    expected_outcome: str = "passed"
    timeout_seconds: int = Field(default=30, ge=1, le=300)


class SafeDocumentation(BaseModel):
    model_config = ConfigDict(frozen=True)

    summary: str = Field(min_length=1, max_length=4000)
    artifact_ref: str | None = None
    documentation_digest: str | None = None
    redaction_classification: str = "safe"
    support_contacts: tuple[str, ...] = Field(default_factory=tuple)
    operator_notes: str | None = None


class SkillManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{1,126}[a-z0-9]$")
    semantic_version: str
    description: str = Field(min_length=1, max_length=4000)
    entrypoint: ManifestEntrypoint
    tools: tuple[ToolDeclaration, ...]
    action_categories: tuple[str, ...]
    network_requirements: tuple[NetworkRequirement, ...] = Field(default_factory=tuple)
    credential_requirements: tuple[CredentialRequirement, ...] = Field(
        default_factory=tuple
    )
    runtime_permissions: tuple[RuntimePermission, ...] = Field(default_factory=tuple)
    test_fixtures: tuple[TestFixture, ...] = Field(default_factory=tuple)
    compatibility: dict[str, Any] = Field(default_factory=dict)
    safe_documentation: SafeDocumentation
    artifact_digests: dict[str, str] = Field(default_factory=dict)
    maintainers: tuple[str, ...] = Field(default_factory=tuple)
    support: dict[str, Any] = Field(default_factory=dict)
    deprecation: dict[str, Any] = Field(default_factory=dict)

    @field_validator("semantic_version")
    @classmethod
    def validate_semver(cls, value: str) -> str:
        if not SEMVER_PATTERN.match(value):
            raise ValueError("semantic_version must be valid SemVer")
        return value

    @model_validator(mode="after")
    def validate_manifest_consistency(self) -> SkillManifest:
        tool_ids = [tool.tool_id for tool in self.tools]
        if len(tool_ids) != len(set(tool_ids)):
            raise ValueError("tool_id values must be unique")
        declared_tools = set(tool_ids)
        for category in self.action_categories:
            if not category:
                raise ValueError("action categories cannot be empty")
        referenced_tool_ids = (
            [item.tool_id for item in self.network_requirements]
            + [item.tool_id for item in self.credential_requirements]
            + [item.tool_id for item in self.runtime_permissions]
            + [item.tool_id for item in self.test_fixtures]
        )
        for item_tool_id in referenced_tool_ids:
            if item_tool_id not in declared_tools:
                raise ValueError(f"{item_tool_id} is not declared in tools")
        unsafe_paths = find_secret_material(self.model_dump(mode="json"))
        if unsafe_paths:
            raise SkillManifestError(
                "manifest contains secret-like material at "
                + ", ".join(sorted(unsafe_paths))
            )
        return self


def canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def canonical_manifest_digest(manifest: SkillManifest | dict[str, Any]) -> str:
    payload = (
        manifest.model_dump(mode="json")
        if isinstance(manifest, SkillManifest)
        else manifest
    )
    return "sha256:" + sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_semver(value: str) -> bool:
    return bool(SEMVER_PATTERN.match(value))


def find_secret_material(payload: Any, *, path: str = "$") -> set[str]:
    findings: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_path = f"{path}.{key}"
            if any(pattern.search(str(key)) for pattern in SECRET_PATTERNS):
                findings.add(key_path)
            findings.update(find_secret_material(value, path=key_path))
        return findings
    if isinstance(payload, list | tuple):
        for index, value in enumerate(payload):
            findings.update(find_secret_material(value, path=f"{path}[{index}]"))
        return findings
    if isinstance(payload, str) and any(
        pattern.search(payload) for pattern in SECRET_PATTERNS
    ):
        findings.add(path)
    return findings
