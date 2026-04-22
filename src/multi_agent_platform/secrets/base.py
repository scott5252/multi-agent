from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SecretValue(BaseModel):
    reference: str
    value: str


class SecretProvider(ABC):
    provider_name: str

    @abstractmethod
    async def resolve(self, reference: str) -> SecretValue:
        raise NotImplementedError
