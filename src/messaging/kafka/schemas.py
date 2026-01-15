from pydantic import BaseModel
from uuid import UUID


class UserCreatedEvent(BaseModel):
    user_id: UUID
    name: str
    extra_field_1: str
    extra_field_2: int