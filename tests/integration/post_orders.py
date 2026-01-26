import pytest


async def test_create_post(async_client):
    payload = {
        "title": "Test title",
        "content": "Test content",
    }

    response = await async_client.post(
        "/api/v1/posts_orders/",
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]


async def test_get_post(async_client):
    create = await async_client.post(
        "/api/v1/posts_orders/",
        json={"title": "Hello", "content": "World"},
    )

    post_id = create.json()["id"]

    response = await async_client.get(
        f"/api/v1/posts_orders/{post_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == post_id


async def test_update_post(async_client):
    create = await async_client.post(
        "/api/v1/posts_orders/",
        json={"title": "Old", "content": "Text"},
    )
    post_id = create.json()["id"]

    response = await async_client.put(
        f"/api/v1/posts_orders/{post_id}",
        json={"title": "New", "content": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New"


async def test_delete_post(async_client):
    create = await async_client.post(
        "/api/v1/posts_orders/",
        json={"title": "Delete", "content": "Me"},
    )
    post_id = create.json()["id"]

    response = await async_client.delete(
        f"/api/v1/posts_orders/{post_id}"
    )

    assert response.status_code == 204
