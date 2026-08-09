from typing import Callable, Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.database import get_db
from app.db.models.permission import Permission
from app.db.models.user_permission import UserPermission
from app.db.models.user import User
from app.db.models.user import UserType


def require_permission(
    module: str,
    action: str,
) -> Callable:
    def permission_checker(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ],
    ) -> User:
        # Super Admin has unrestricted access.
        if current_user.user_type == UserType.SUPER_ADMIN:
            return current_user

        # Find the requested permission assigned to this user.
        permission_exists = db.scalar(
            select(Permission.id)
            .join(
                UserPermission,
                UserPermission.permission_id == Permission.id,
            )
            .where(
                UserPermission.user_id == current_user.id,
                Permission.module == module,
                Permission.action == action,
            )
        )

        if permission_exists is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"You do not have permission to " f"{action.lower()} {module}."
                ),
            )

        return current_user

    return permission_checker
