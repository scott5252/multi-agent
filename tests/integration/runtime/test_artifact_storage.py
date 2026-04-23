from __future__ import annotations


async def test_artifact_storage_fixture_round_trip(filesystem_storage_provider) -> None:
    await filesystem_storage_provider.put("tenant/result.json", b"{}")
    payload = await filesystem_storage_provider.get("tenant/result.json")
    assert payload == b"{}"


async def test_artifact_storage_can_round_trip_workflow_registry_bundle(
    filesystem_storage_provider, workflow_registry_artifact_prefix
) -> None:
    key = f"{workflow_registry_artifact_prefix}/bundles/demo.json"
    expected = b'{"workflow":"demo"}'

    handle = await filesystem_storage_provider.put(key, expected)
    payload = await filesystem_storage_provider.get(handle.key)

    assert handle.key == key
    assert payload == expected
