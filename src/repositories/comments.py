from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.comments import CommentModel


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: CommentModel) -> None:
        self.session.add(comment)

    async def get_by_id(
            self,
            comment_id: UUID,
    ) -> CommentModel | None:
        stmt = (
            select(CommentModel)
            .where(CommentModel.id == comment_id)
            .options(selectinload(CommentModel.role_o2o))
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, comment_id: UUID) -> None:
        stmt = delete(CommentModel).where(CommentModel.id == comment_id)
        await self.session.execute(stmt)