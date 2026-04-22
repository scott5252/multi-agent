from __future__ import annotations

from multi_agent_platform.storage.providers.s3 import S3StorageProvider


async def test_filesystem_storage_provider_round_trip(
    filesystem_storage_provider,
) -> None:
    handle = await filesystem_storage_provider.put("tenant/a.txt", b"hello")
    payload = await filesystem_storage_provider.get("tenant/a.txt")
    assert handle.provider == "filesystem"
    assert payload == b"hello"


async def test_s3_storage_provider_returns_s3_url(tmp_path) -> None:
    provider = S3StorageProvider(bucket="demo", root=tmp_path)
    handle = await provider.put("artifact.bin", b"abc")
    assert handle.url == "s3://demo/artifact.bin"
