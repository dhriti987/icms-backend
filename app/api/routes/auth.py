from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError

from app.schemas.auth import RefreshTokenRequest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)

from app.api.dependencies.auth import get_current_user
from app.db.models.permission import Permission
from app.db.models.user_permission import UserPermission

# from app.db.models.user import User
from app.db.models.user import UserType


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == login_data.username))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(user.id)

    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> TokenResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    try:
        payload = decode_token(refresh_data.refresh_token)

        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        raise credentials_exception

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
)
def get_current_user_info(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    permissions = db.scalars(
        select(Permission)
        .join(
            UserPermission,
            UserPermission.permission_id == Permission.id,
        )
        .where(UserPermission.user_id == current_user.id)
    ).all()

    permission_map: dict[str, list[str]] = {}

    for permission in permissions:
        permission_map.setdefault(
            permission.module,
            [],
        ).append(permission.action.value)

    if current_user.user_type == UserType.SUPER_ADMIN:
        return {
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "user_type": current_user.user_type.value,
                "is_active": current_user.is_active,
            },
            "permissions": {"all": True},
        }

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "user_type": current_user.user_type.value,
            "is_active": current_user.is_active,
        },
        "permissions": permission_map,
    }
