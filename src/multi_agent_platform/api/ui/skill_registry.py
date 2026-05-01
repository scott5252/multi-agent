from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Self
from uuid import uuid4

from multi_agent_platform.admin.skill_registry.service import (
    SkillInstallationRecord,
    SkillPackageRecord,
    SkillPackageVersionRecord,
)


@dataclass(frozen=True, slots=True)
class SkillRegistryPageModel:
    title: str
    scope_label: str
    packages: tuple[dict[str, object], ...] = ()
    versions: tuple[dict[str, object], ...] = ()
    installations: tuple[dict[str, object], ...] = ()
    audit_events: tuple[dict[str, object], ...] = ()
    findings: tuple[dict[str, object], ...] = ()
    redaction_notice: str = (
        "Raw package payloads, secrets, credential values, provider tokens, "
        "unsafe docs, and cross-tenant data are omitted."
    )
    actions: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class BrowserFormError:
    field: str
    message: str


@dataclass(frozen=True, slots=True)
class RedactionSafePageContext:
    redaction_notice: str = (
        "Raw package payloads, secrets, credential values, provider tokens, "
        "unsafe docs, unsafe fixtures, raw validation input, raw smoke-test logs, "
        "and cross-tenant data are omitted."
    )
    tenant_scope_label: str = "platform"
    denial_state: str | None = None
    empty_state: str | None = None
    safe_summaries: tuple[dict[str, object], ...] = ()
    redacted_fields: tuple[str, ...] = (
        "raw_package_payload",
        "raw_manifest_input",
        "raw_credential_value",
        "provider_token",
        "raw_smoke_log",
    )


@dataclass(frozen=True, slots=True)
class RevisionConflictView:
    resource_type: str
    resource_id: str
    submitted_revision: str | None
    current_revision: str | None
    reload_url: str
    retry_url: str
    audit_record_id: str | None = None
    safe_message: str = (
        "This item changed after the form loaded. No stale browser action was "
        "applied; reload the latest state and retry."
    )


@dataclass(frozen=True, slots=True)
class SkillPackageCreateForm:
    slug: str
    display_name: str
    description: str
    steward_principal_id: str
    lifecycle_intent: str
    safe_documentation_summary: str
    idempotency_key: str
    errors: tuple[BrowserFormError, ...] = ()

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any], *, default_owner: str) -> Self:
        slug = _string(form, "slug").lower()
        display_name = _string(form, "display_name")
        owner = _string(form, "owner_principal_id") or _string(
            form, "steward_principal_id"
        )
        errors: list[BrowserFormError] = []
        if not slug:
            errors.append(BrowserFormError("slug", "Slug is required."))
        if slug and not slug.replace("-", "").replace("_", "").isalnum():
            errors.append(
                BrowserFormError(
                    "slug",
                    "Slug may contain letters, numbers, hyphens, or underscores.",
                )
            )
        if not display_name:
            errors.append(BrowserFormError("display_name", "Display name is required."))
        return cls(
            slug=slug,
            display_name=display_name,
            description=_string(form, "description"),
            steward_principal_id=owner or default_owner,
            lifecycle_intent=_string(form, "lifecycle_intent") or "publishable",
            safe_documentation_summary=_string(form, "safe_documentation_summary"),
            idempotency_key=_idempotency_key(form),
            errors=tuple(errors),
        )


@dataclass(frozen=True, slots=True)
class ManifestCandidateForm:
    manifest_payload: dict[str, object]
    artifact_digest: str
    approved_integration_refs: set[str]
    candidate_revision: str | None
    input_source: str
    validation_reason: str
    idempotency_key: str
    errors: tuple[BrowserFormError, ...] = ()

    @classmethod
    def from_mapping(
        cls,
        form: Mapping[str, Any],
        *,
        uploaded_manifest_text: str | None = None,
    ) -> Self:
        text = (
            uploaded_manifest_text
            if uploaded_manifest_text is not None
            else _string(form, "manifest") or _string(form, "manifest_text")
        )
        source = "upload" if uploaded_manifest_text is not None else "paste"
        payload, errors = parse_manifest_text(text)
        artifact_digest = _string(form, "artifact_digest")
        if not artifact_digest:
            errors.append(
                BrowserFormError("artifact_digest", "Artifact digest is required.")
            )
        return cls(
            manifest_payload=payload,
            artifact_digest=artifact_digest,
            approved_integration_refs=_split_values(
                _string(form, "approved_integration_refs")
            ),
            candidate_revision=_string(form, "revision_token")
            or _string(form, "candidate_revision")
            or None,
            input_source=source,
            validation_reason=_string(form, "validation_reason"),
            idempotency_key=_idempotency_key(form),
            errors=tuple(errors),
        )


@dataclass(frozen=True, slots=True)
class TenantGrantForm:
    selected_tenant_ids: set[str]
    grant_reason: str
    grant_revision: str | None
    idempotency_key: str
    errors: tuple[BrowserFormError, ...] = ()

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any]) -> Self:
        tenants = _split_values(
            _string(form, "tenant_ids") or _string(form, "selected_tenant_ids")
        )
        errors = (
            ()
            if tenants
            else (BrowserFormError("tenant_ids", "Select at least one tenant."),)
        )
        return cls(
            selected_tenant_ids=tenants,
            grant_reason=_string(form, "grant_reason"),
            grant_revision=_string(form, "grant_revision") or None,
            idempotency_key=_idempotency_key(form),
            errors=errors,
        )


@dataclass(frozen=True, slots=True)
class InstallSkillForm:
    tenant_id: str
    slug: str
    semantic_version: str
    previous_installation_id: str | None
    idempotency_key: str
    errors: tuple[BrowserFormError, ...] = ()

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any]) -> Self:
        errors: list[BrowserFormError] = []
        for field_name in ("tenant_id", "slug", "semantic_version"):
            if not _string(form, field_name):
                errors.append(BrowserFormError(field_name, "This field is required."))
        return cls(
            tenant_id=_string(form, "tenant_id"),
            slug=_string(form, "slug"),
            semantic_version=_string(form, "semantic_version"),
            previous_installation_id=_string(form, "previous_installation_id") or None,
            idempotency_key=_idempotency_key(form),
            errors=tuple(errors),
        )


@dataclass(frozen=True, slots=True)
class CredentialReferenceConfigForm:
    revision_token: str
    requirement_key: str
    credential_kind: str
    selected_reference_id: str | None
    delegated_metadata_fields: dict[str, object]
    idempotency_key: str
    errors: tuple[BrowserFormError, ...] = ()

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any]) -> Self:
        credential_kind = _string(form, "credential_kind") or "delegated_credential"
        reference_id = _string(form, "reference_id") or _string(
            form, "selected_reference_id"
        )
        metadata = {
            "scope": _string(form, "delegated_scope"),
            "delegated_account": _string(form, "delegated_account"),
        }
        errors: list[BrowserFormError] = []
        if not _string(form, "revision_token"):
            errors.append(
                BrowserFormError("revision_token", "Revision token is required.")
            )
        if not _string(form, "requirement_key"):
            errors.append(
                BrowserFormError("requirement_key", "Requirement key is required.")
            )
        if credential_kind not in {"secret_reference", "delegated_credential"}:
            errors.append(
                BrowserFormError("credential_kind", "Credential kind is not supported.")
            )
        return cls(
            revision_token=_string(form, "revision_token"),
            requirement_key=_string(form, "requirement_key"),
            credential_kind=credential_kind,
            selected_reference_id=reference_id or None,
            delegated_metadata_fields={
                key: value for key, value in metadata.items() if value
            },
            idempotency_key=_idempotency_key(form),
            errors=tuple(errors),
        )


@dataclass(frozen=True, slots=True)
class SmokeTestActionForm:
    revision_token: str
    fixture_keys: set[str]
    action_reason: str
    idempotency_key: str

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any]) -> Self:
        return cls(
            revision_token=_string(form, "revision_token"),
            fixture_keys=_split_values(_string(form, "fixture_keys")),
            action_reason=_string(form, "action_reason"),
            idempotency_key=_idempotency_key(form),
        )


@dataclass(frozen=True, slots=True)
class BindingEligibilityPreviewForm:
    revision_token: str
    selected_context_type: str
    selected_context_id: str
    idempotency_key: str

    @classmethod
    def from_mapping(cls, form: Mapping[str, Any]) -> Self:
        return cls(
            revision_token=_string(form, "revision_token"),
            selected_context_type=_string(form, "context_type") or "profile",
            selected_context_id=_string(form, "context_id")
            or _string(form, "binding_context"),
            idempotency_key=_idempotency_key(form),
        )


def build_package_list_page(
    packages: list[SkillPackageRecord],
    *,
    platform_admin: bool,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title="Skill Registry",
        scope_label="platform" if platform_admin else "tenant",
        packages=tuple(
            {
                "slug": package.slug,
                "display_name": package.display_name,
                "lifecycle_state": package.lifecycle_state,
                "latest_published_version": max(package.versions, default=None),
                "version_count": len(package.versions),
            }
            for package in packages
        ),
        actions=("create_package", "publish_version") if platform_admin else (),
    )


def build_package_detail_page(
    package: SkillPackageRecord,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title=f"Skill Package: {package.slug}",
        scope_label="platform",
        packages=(
            {
                "slug": package.slug,
                "display_name": package.display_name,
                "description": package.description,
                "lifecycle_state": package.lifecycle_state,
            },
        ),
        versions=tuple(
            _version_summary(version) for version in package.versions.values()
        ),
        actions=("validate_candidate", "grant_availability", "quarantine"),
    )


def build_version_detail_page(
    version: SkillPackageVersionRecord,
) -> SkillRegistryPageModel:
    findings = tuple(
        {
            "code": finding.code,
            "message": finding.message,
            "severity": finding.severity,
            "blocking": finding.blocking,
        }
        for finding in version.validation_findings
    )
    return SkillRegistryPageModel(
        title=f"{version.slug} {version.semantic_version}",
        scope_label="platform",
        versions=(_version_summary(version),),
        findings=findings,
        actions=("withdraw", "quarantine", "grant_availability"),
    )


def build_installation_list_page(
    installations: list[SkillInstallationRecord],
    *,
    tenant_id: str,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title="Installed Skills",
        scope_label=tenant_id,
        installations=tuple(_installation_summary(item) for item in installations),
        actions=("install", "run_smoke_tests", "promote_readiness"),
    )


def build_installation_detail_page(
    installation: SkillInstallationRecord,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title=f"Installed Skill: {installation.slug}",
        scope_label=installation.tenant_id,
        installations=(_installation_summary(installation),),
        findings=tuple(
            {
                "code": finding.code,
                "message": finding.message,
                "blocking": finding.blocking,
            }
            for finding in (
                installation.readiness.findings if installation.readiness else ()
            )
        ),
        actions=("configure_credentials", "run_smoke_tests", "preview_binding"),
    )


def _version_summary(version: SkillPackageVersionRecord) -> dict[str, object]:
    return {
        "package_version_id": version.package_version_id,
        "slug": version.slug,
        "semantic_version": version.semantic_version,
        "manifest_digest": version.manifest_digest,
        "artifact_digest": version.artifact_digest,
        "validation_status": version.validation_status,
        "lifecycle_state": version.lifecycle_state,
        "tenant_grants": sorted(version.tenant_grants),
        "quarantined": version.quarantined,
        "runtime_blocked": version.runtime_blocked,
    }


def _installation_summary(
    installation: SkillInstallationRecord,
) -> dict[str, object]:
    readiness = installation.readiness
    return {
        "installation_id": installation.installation_id,
        "tenant_id": installation.tenant_id,
        "slug": installation.slug,
        "semantic_version": installation.semantic_version,
        "installation_version": installation.installation_version,
        "manifest_digest": installation.manifest_digest,
        "artifact_digest": installation.artifact_digest,
        "revision_token": installation.revision_token,
        "readiness_state": readiness.readiness_state if readiness else "blocked",
        "credential_status": readiness.credential_status if readiness else "blocked",
        "smoke_test_status": readiness.smoke_test_status if readiness else "blocked",
        "binding_eligibility_status": (
            readiness.binding_eligibility_status if readiness else "denied"
        ),
        "quarantined": installation.quarantined,
        "runtime_blocked": installation.runtime_blocked,
    }


def build_revision_conflict_view(
    *,
    resource_type: str,
    resource_id: str,
    submitted_revision: str | None,
    current_revision: str | None,
    reload_url: str,
) -> RevisionConflictView:
    return RevisionConflictView(
        resource_type=resource_type,
        resource_id=resource_id,
        submitted_revision=submitted_revision,
        current_revision=current_revision,
        reload_url=reload_url,
        retry_url=reload_url,
    )


def authorized_binding_context_options(tenant_id: str) -> tuple[dict[str, str], ...]:
    return (
        {
            "context_type": "profile",
            "context_id": f"{tenant_id}:qa-profile",
            "label": "QA runtime profile",
        },
        {
            "context_type": "workflow_role",
            "context_id": f"{tenant_id}:workflow-reviewer",
            "label": "Workflow reviewer role",
        },
    )


def parse_manifest_text(
    raw_manifest: str,
) -> tuple[dict[str, object], list[BrowserFormError]]:
    raw_manifest = raw_manifest.strip()
    if not raw_manifest:
        return {}, [BrowserFormError("manifest", "Manifest YAML or JSON is required.")]
    try:
        parsed = json.loads(raw_manifest)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            return {}, [BrowserFormError("manifest", "Manifest must be valid JSON.")]
        try:
            parsed = yaml.safe_load(raw_manifest)
        except yaml.YAMLError:
            return {}, [
                BrowserFormError("manifest", "Manifest YAML could not be parsed.")
            ]
    if not isinstance(parsed, dict):
        return {}, [BrowserFormError("manifest", "Manifest must parse to an object.")]
    return dict(parsed), []


def _string(form: Mapping[str, Any], key: str) -> str:
    value = form.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def _split_values(raw_value: str) -> set[str]:
    return {
        item.strip()
        for chunk in raw_value.splitlines()
        for item in chunk.split(",")
        if item.strip()
    }


def _idempotency_key(form: Mapping[str, Any]) -> str:
    return _string(form, "idempotency_key") or str(uuid4())
