from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.users import Base
from src.models.users import UserModel


class RoleModel(Base):
    __tablename__ = 'role'

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()

    user: Mapped["UserModel"] = relationship(
        back_populates="role",
        uselist=False
    )

