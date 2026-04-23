from __future__ import annotations

import platform

from pydantic import BaseModel

from multi_agent_platform.config.settings import Settings
from multi_agent_platform.runtime.workflow_bundle import CompiledWorkflowBundle


class VersionBundle(BaseModel):
    service: str
    version: str
    commit_sha: str
    build_time: str
    python_version: str
    auth_policy_version: str = "2026-04-22"
    surface_policy_version: str = "2026-04-22"
    claim_mapping_version: str = "2026-04-22"


class RunVersionBundle(BaseModel):
    workflow_version_bundle_id: str
    workflow_lineage_id: str
    workflow_key: str
    compiled_bundle_digest: str
    compiler_version: str
    pinned_skill_versions: dict[str, str]
    subworkflow_version_refs: dict[str, str]


def get_version_bundle(settings: Settings) -> VersionBundle:
    return VersionBundle(
        service=settings.app_name,
        version=settings.app_version,
        commit_sha=settings.commit_sha,
        build_time=settings.build_time,
        python_version=platform.python_version(),
    )


def get_workflow_registry_compiler_version() -> str:
    return "workflow-registry-0.1"


def build_run_version_bundle(
    *,
    workflow_version_bundle_id: str,
    compiled_bundle: CompiledWorkflowBundle,
) -> RunVersionBundle:
    raw_skills = compiled_bundle.dependencies.get("skills", [])
    raw_subworkflows = compiled_bundle.dependencies.get("subworkflows", [])
    skills = raw_skills if isinstance(raw_skills, list) else []
    subworkflows = raw_subworkflows if isinstance(raw_subworkflows, list) else []
    return RunVersionBundle(
        workflow_version_bundle_id=workflow_version_bundle_id,
        workflow_lineage_id=compiled_bundle.workflow_lineage_id,
        workflow_key=compiled_bundle.workflow_key,
        compiled_bundle_digest=compiled_bundle.digest(),
        compiler_version=compiled_bundle.compiler_version,
        pinned_skill_versions={
            str(item["skill_slug"]): str(item["skill_version"])
            for item in skills
            if isinstance(item, dict)
            and "skill_slug" in item
            and "skill_version" in item
        },
        subworkflow_version_refs={
            str(item["alias"]): str(item["workflow_version_ref"])
            for item in subworkflows
            if isinstance(item, dict)
            and "alias" in item
            and "workflow_version_ref" in item
        },
    )
