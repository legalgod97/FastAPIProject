

async def test_create_user(async_client):
    payload = {
        "name": "Test User",
    }

    resp = await async_client.post(
        "/api/v1/users_profiles/",
        json=payload,
    )

    assert resp.status_code == 201

    data = resp.json()
    assert "id" in data
    assert data["name"] == payload["name"]


async def test_get_user(async_client):
    create = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "Getter"},
    )

    user_id = create.json()["id"]

    resp = await async_client.get(
        f"/api/v1/users_profiles/{user_id}"
    )

    assert resp.status_code == 200
    assert resp.json()["id"] == user_id


async def test_update_user(async_client):
    create = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "Old Name"},
    )

    user_id = create.json()["id"]

    resp = await async_client.put(
        f"/api/v1/users_profiles/{user_id}",
        json={"name": "New Name"},
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_delete_user(async_client):
    create = await async_client.post(
        "/api/v1/users_profiles/",
        json={"name": "To Delete"},
    )

    user_id = create.json()["id"]

    resp = await async_client.delete(
        f"/api/v1/users_profiles/{user_id}"
    )

    assert resp.status_code == 204

    check = await async_client.get(
        f"/api/v1/users_profiles/{user_id}"
    )

    assert check.status_code == 404