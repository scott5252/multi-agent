from __future__ import annotations


async def test_artifact_storage_fixture_round_trip(filesystem_storage_provider) -> None:
    await filesystem_storage_provider.put("tenant/result.json", b"{}")
    payload = await filesystem_storage_provider.get("tenant/result.json")
    assert payload == b"{}"
