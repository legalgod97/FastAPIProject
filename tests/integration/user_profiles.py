import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    payload = {
        "name": "Test User",
        "extra_field_1": "value",
        "extra_field_2": 42,
    }

    resp = await async_client.post("/api/v1/users_profiles/", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    assert "id" in data
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_user(async_client):
    create_resp = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "Getter", "extra_field_1": "val", "extra_field_2": 3},
    )
    user_id = create_resp.json()["id"]

    get_resp = await async_client.get(f"/api/v1/users_profiles/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == user_id
    assert data["name"] == "Getter"


@pytest.mark.asyncio
async def test_update_user(async_client):
    create_resp = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "Old Name", "extra_field_1": "val", "extra_field_2": 5},
    )
    user_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/users_profiles/{user_id}",
        json={"name": "New Name"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_user(async_client):
    create_resp = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "To Delete", "extra_field_1": "val", "extra_field_2": 10},
    )
    user_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/api/v1/users_profiles/{user_id}")
    assert delete_resp.status_code == 204

    check_resp = await async_client.get(f"/api/v1/users_profiles/{user_id}")
    assert check_resp.status_code == 404
