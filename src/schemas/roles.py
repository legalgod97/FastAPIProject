from uuid import UUID
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    id: UUID | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleRead(RoleBase):
    id: UUID

    model_config = {
        "from_attributes": True
    }
