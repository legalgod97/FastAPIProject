from uuid import UUID
from pydantic import BaseModel


class UserCreatedEvent(BaseModel):
    user_id: UUID
    name: str


class UserUpdatedEvent(BaseModel):
    user_id: UUID
    name: str


class UserDeletedEvent(BaseModel):
    user_id: UUID