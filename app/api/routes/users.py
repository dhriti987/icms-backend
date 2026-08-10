from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.admin import require_super_admin

# from app.api.dependencies.auth import get_current_user
from app.db.database import get_db
from app.db.models.permission import Permission
from app.db.models.user import User
from app.schemas.user import (
    MessageResponse,
    UserDetailResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import (
    activate_user,
    assign_permission,
    create_user,
    deactivate_user,
    delete_user,
    get_user,
    get_users,
    revoke_permission,
    update_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    user_data: UserCreate,
    current_user: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return create_user(
        db,
        current_user,
        user_data,
    )


@router.get(
    "",
    response_model=UserListResponse,
)
def list_users_endpoint(
    _: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    users, total = get_users(db)

    return UserListResponse(
        items=users,
        total=total,
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
)
def get_user_endpoint(
    user_id: int,
    _: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    user, permissions = get_user(
        db,
        user_id,
    )

    return UserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        user_type=user.user_type,
        is_active=user.is_active,
        permissions=permissions,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    return update_user(
        db,
        target_user,
        user_data,
        current_user,
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
)
def delete_user_endpoint(
    user_id: int,
    current_user: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    delete_user(
        db,
        current_user,
        target_user,
    )

    return MessageResponse(message="User deleted successfully.")


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user_endpoint(
    user_id: int,
    current_user: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    return deactivate_user(
        db,
        current_user,
        target_user,
    )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
def activate_user_endpoint(
    user_id: int,
    current_user: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    return activate_user(
        db,
        current_user,
        target_user,
    )


@router.post(
    "/{user_id}/permissions/{permission_id}",
    response_model=MessageResponse,
)
def assign_permission_endpoint(
    user_id: int,
    permission_id: int,
    _: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    permission = db.get(
        Permission,
        permission_id,
    )

    if permission is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    assign_permission(
        db,
        target_user,
        permission,
    )

    return MessageResponse(message="Permission assigned successfully.")


@router.delete(
    "/{user_id}/permissions/{permission_id}",
    response_model=MessageResponse,
)
def revoke_permission_endpoint(
    user_id: int,
    permission_id: int,
    _: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    target_user, _ = get_user(
        db,
        user_id,
    )

    permission = db.get(
        Permission,
        permission_id,
    )

    if permission is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    revoke_permission(
        db,
        target_user,
        permission,
    )

    return MessageResponse(message="Permission revoked successfully.")
