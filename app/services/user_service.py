from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password

# from app.db.models.user import UserType
from app.db.models.permission import Permission
from app.db.models.user import User
from app.db.models.user_permission import UserPermission
from app.schemas.user import UserCreate, UserUpdate


def create_user(
    db: Session,
    current_user: User,
    user_data: UserCreate,
) -> User:
    existing_username = db.scalar(
        select(User).where(User.username == user_data.username)
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    existing_email = db.scalar(select(User).where(User.email == user_data.email))

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        user_type=user_data.user_type,
        is_active=True,
        created_by=current_user.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_users(
    db: Session,
) -> tuple[list[User], int]:
    users = list(db.scalars(select(User).order_by(User.id)).all())

    total = db.scalar(select(func.count()).select_from(User)) or 0

    return users, total


def get_user(
    db: Session,
    user_id: int,
) -> tuple[User, list[Permission]]:
    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    permissions = list(
        db.scalars(
            select(Permission)
            .join(
                UserPermission,
                UserPermission.permission_id == Permission.id,
            )
            .where(UserPermission.user_id == user.id)
            .order_by(
                Permission.module,
                Permission.action,
            )
        ).all()
    )

    return user, permissions


def update_user(
    db: Session,
    target_user: User,
    user_data: UserUpdate,
    current_user: User,
) -> User:
    if user_data.username is not None:
        existing_username = db.scalar(
            select(User).where(
                User.username == user_data.username,
                User.id != target_user.id,
            )
        )

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        target_user.username = user_data.username

    if user_data.email is not None:
        existing_email = db.scalar(
            select(User).where(
                User.email == user_data.email,
                User.id != target_user.id,
            )
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        target_user.email = user_data.email
    target_user.updated_by = current_user.id

    db.commit()
    db.refresh(target_user)

    return target_user


def delete_user(
    db: Session,
    current_user: User,
    target_user: User,
) -> None:
    if current_user.id == target_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete your own account.",
        )

    db.delete(target_user)
    db.commit()


def deactivate_user(
    db: Session,
    current_user: User,
    target_user: User,
) -> User:
    if current_user.id == target_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot deactivate your own account.",
        )

    if not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive.",
        )

    target_user.is_active = False
    target_user.updated_by = current_user.id

    db.commit()
    db.refresh(target_user)

    return target_user


def activate_user(
    db: Session,
    current_user: User,
    target_user: User,
) -> User:
    if target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active.",
        )

    target_user.is_active = True
    target_user.updated_by = current_user.id

    db.commit()
    db.refresh(target_user)

    return target_user


def assign_permission(
    db: Session,
    user: User,
    permission: Permission,
) -> None:
    existing = db.scalar(
        select(UserPermission).where(
            UserPermission.user_id == user.id,
            UserPermission.permission_id == permission.id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission is already assigned to this user.",
        )

    user_permission = UserPermission(
        user_id=user.id,
        permission_id=permission.id,
    )

    db.add(user_permission)
    db.commit()


def revoke_permission(
    db: Session,
    user: User,
    permission: Permission,
) -> None:
    user_permission = db.scalar(
        select(UserPermission).where(
            UserPermission.user_id == user.id,
            UserPermission.permission_id == permission.id,
        )
    )

    if user_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission is not assigned to this user.",
        )

    db.delete(user_permission)
    db.commit()
