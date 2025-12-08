from fastapi import APIRouter, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.notifications import NotificationModel
from src.models.posts import PostModel, post_notification

router = APIRouter(prefix="/posts", tags=["post_notifications"])


@router.post("/")
async def create_post_notification(data: dict, session: AsyncSession):
    post_id = UUID(data["post_id"])
    notification_data = data["notification"]
    notification_id = UUID(notification_data["id"])

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    notification = (await session.execute(
        select(NotificationModel).where(NotificationModel.id == notification_id)
    )).scalar_one_or_none()
    if not notification:
        raise HTTPException(404, "Notification not found")

    existing = (await session.execute(
        select(post_notification).where(
            and_(
                post_notification.c.post_id == post_id,
                post_notification.c.notification_id == notification_id
            )
        )
    )).first()

    if existing:
        raise HTTPException(400, "Relation already exists")

    await session.execute(
        post_notification.insert().values(
            post_id=post_id,
            notification_id=notification_id
        )
    )
    await session.commit()

    return {"status": "created"}


@router.get("/{post_id}")
async def get_post_notifications(post_id: UUID, session: AsyncSession):
    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    result = await session.execute(
        select(post_notification.c.notification_id).where(
            and_(
                post_notification.c.post_id == post_id
            )
        )
    )
    notification_ids = result.scalars().all()

    notifications = []
    for n_id in notification_ids:
        notification = (await session.execute(
            select(NotificationModel).where(NotificationModel.id == n_id)
        )).scalar_one_or_none()
        if notification:
            notifications.append({
                "id": str(notification.id),
                "message": notification.message,
                "type": notification.type.value,
                "is_read": notification.is_read
            })

    return {"post_id": str(post_id), "notifications": notifications}


@router.put("/")
async def update_post_notification(data: dict, session: AsyncSession):
    post_id = UUID(data["post_id"])
    notification_data = data["notification"]
    notification_id = UUID(notification_data["id"])

    post = (await session.execute(
        select(PostModel).where(PostModel.id == post_id)
    )).scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")

    notification = (await session.execute(
        select(NotificationModel).where(NotificationModel.id == notification_id)
    )).scalar_one_or_none()
    if not notification:
        raise HTTPException(404, "Notification not found")

    existing_link = (await session.execute(
        select(post_notification).where(
            and_(
                post_notification.c.post_id == post_id,
                post_notification.c.notification_id == notification_id
            )
        )
    )).first()
    if not existing_link:
        raise HTTPException(404, "Notification link not found")

    notification.message = notification_data["message"]
    notification.type = notification_data["type"]
    notification.is_read = notification_data["is_read"]

    await session.commit()

    return {"status": "updated"}


@router.delete("/{post_id}/notifications/{notification_id}")
async def delete_post_notification(post_id: UUID, notification_id: UUID, session: AsyncSession):

    existing_link = (await session.execute(
        select(post_notification).where(
            and_(
                post_notification.c.post_id == post_id,
                post_notification.c.notification_id == notification_id
            )
        )
    )).first()
    if not existing_link:
        raise HTTPException(404, "Notification link not found")

    await session.execute(
        post_notification.delete().where(
            and_(
                post_notification.c.post_id == post_id,
                post_notification.c.notification_id == notification_id
            )
        )
    )
    await session.commit()

    return {"status": "deleted"}
