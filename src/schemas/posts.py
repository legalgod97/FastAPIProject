from uuid import UUID
from pydantic import BaseModel

class PostCreate(BaseModel):
    id: UUID | None = None
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None



