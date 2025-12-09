from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.models.users import Base
from infrastructure.db.models.users import UserModel


class RoleModel(Base):
    __tablename__ = 'role'

    name: Mapped[str] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()

    user: Mapped["UserModel"] = relationship(
        back_populates="role",
        uselist=False
    )

