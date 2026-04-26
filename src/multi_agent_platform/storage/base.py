from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class ArtifactHandle(BaseModel):
    provider: str
    key: str
    url: str
    size_bytes: int


class StorageProvider(ABC):
    provider_name: str

    @abstractmethod
    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> bytes:
        raise NotImplementedError


def build_artifact_key(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts if part)


def build_debug_evidence_export_key(tenant_id: str, export_id: str) -> str:
    return build_artifact_key("audit-debug", tenant_id, f"{export_id}.json")
