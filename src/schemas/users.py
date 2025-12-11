from uuid import UUID
from pydantic import BaseModel


class UserCreate(BaseModel):
    id: UUID | None = None
    name: str