from typing import Literal
from pydantic import BaseModel


class DeleteResult(BaseModel):
    status: Literal["deleted"]