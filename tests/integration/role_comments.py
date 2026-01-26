

async def test_create_role(async_client):
    resp = await async_client.post(
        "/api/v1/roles_comments/",
        json={"name": "Admin"},
    )
    assert resp.status_code == 201

    role_id = resp.json()["id"]

    get_resp = await async_client.get(f"/api/v1/roles_comments/{role_id}")
    assert get_resp.status_code == 200

async def test_get_role(async_client):
    import asyncio
    print("Current loop in test_get_role:", asyncio.get_running_loop())
    create = await async_client.post(
        "/api/v1/roles_comments/",
        json={"name": "Moderator"},
    )
    role_id = create.json()["id"]

    resp = await async_client.get(f"/api/v1/roles_comments/{role_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Moderator"

async def test_update_role(async_client):
    create = await async_client.post(
        "/api/v1/roles_comments/",
        json={"name": "User"},
    )
    role_id = create.json()["id"]

    resp = await async_client.put(
        f"/api/v1/roles_comments/{role_id}",
        json={"name": "SuperUser"},
    )
    assert resp.status_code == 200

    check = await async_client.get(f"/api/v1/roles_comments/{role_id}")
    assert check.json()["name"] == "SuperUser"

async def test_delete_role(async_client):
    create = await async_client.post(
        "/api/v1/roles_comments/",
        json={"name": "To be deleted"},
    )
    role_id = create.json()["id"]

    resp = await async_client.delete(f"/api/v1/roles_comments/{role_id}")
    assert resp.status_code == 204

    check = await async_client.get(f"/api/v1/roles_comments/{role_id}")
    assert check.status_code == 404