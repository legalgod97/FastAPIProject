from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.comments import CommentModel


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: CommentModel) -> None:
        self.session.add(comment)

    async def get_by_id(
        self,
        comment_id: UUID,
        *,
        with_role: bool = False,
    ) -> CommentModel | None:
        stmt = select(CommentModel).where(CommentModel.id == comment_id)

        if with_role:
            stmt = stmt.options(selectinload(CommentModel.role_o2o))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, comment: CommentModel) -> None:
        await self.session.delete(comment)