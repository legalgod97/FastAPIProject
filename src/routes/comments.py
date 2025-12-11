from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

from models.comments import CommentModel
from schemas.comments import CommentCreate, CommentUpdate, CommentOut
from src.session import get_async_session


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentOut)
async def create_comment(
    data: CommentCreate,
    session: AsyncSession = Depends(get_async_session),
):
    comment = CommentModel(
        id=uuid4(),
        **data.model_dump(exclude_unset=True)
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(
    comment_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    comment = await session.get(CommentModel, comment_id)

    if not comment:
        raise HTTPException(404, "Comment not found")

    return comment


@router.patch("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    comment = await session.get(CommentModel, comment_id)

    if not comment:
        raise HTTPException(404, "Comment not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(comment, key, value)

    if data.content is not None:
        comment.is_edited = True

    await session.commit()
    await session.refresh(comment)
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    comment = await session.get(CommentModel, comment_id)

    if not comment:
        raise HTTPException(404, "Comment not found")

    await session.delete(comment)
    await session.commit()
    return {"status": "deleted"}