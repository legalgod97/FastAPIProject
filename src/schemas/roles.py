from pydantic import BaseModel
from uuid import UUID


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None



class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    model_config = {
        "from_attributes": True
    }