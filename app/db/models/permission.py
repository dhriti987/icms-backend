from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class PermissionAction(str, Enum):
    VIEW = "view"
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"


class Permission(Base):
    __tablename__ = "permissions"

    __table_args__ = (
        UniqueConstraint(
            "module",
            "action",
            name="uq_permission_module_action",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    action: Mapped[PermissionAction] = mapped_column(
        SQLEnum(
            PermissionAction,
            name="permission_action",
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        
        nullable=False,
    )