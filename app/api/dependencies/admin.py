from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.db.models.user import UserType
from app.db.models.user import User


def require_super_admin(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    if current_user.user_type != UserType.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required.",
        )

    return current_user
