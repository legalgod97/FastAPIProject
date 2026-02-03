import pytest
from src.schemas.posts import PostCreate, PostUpdate
from src.services.posts import create_post, get_post, update_post, delete_post
from src.exceptions.common import NotFoundError


@pytest.mark.asyncio
async def test_create_post(db_session):
    payload = PostCreate(title="Test title", content="Test content")
    post = await create_post(db_session, payload)

    assert post.id is not None
    assert post.title == payload.title
    assert post.content == payload.content


@pytest.mark.asyncio
async def test_get_post(db_session):
    payload = PostCreate(title="Hello", content="World")
    post = await create_post(db_session, payload)

    fetched = await get_post(db_session, post.id)
    assert fetched.id == post.id
    assert fetched.title == post.title
    assert fetched.content == post.content


@pytest.mark.asyncio
async def test_update_post(db_session):
    payload = PostCreate(title="Old", content="Text")
    post = await create_post(db_session, payload)

    updated = await update_post(
        db_session,
        post.id,
        PostUpdate(title="New", content="Updated")
    )

    assert updated.id == post.id
    assert updated.title == "New"
    assert updated.content == "Updated"


@pytest.mark.asyncio
async def test_delete_post(db_session):
    payload = PostCreate(title="Delete", content="Me")
    post = await create_post(db_session, payload)

    await delete_post(db_session, post.id)

    with pytest.raises(NotFoundError):
        await get_post(db_session, post.id)
