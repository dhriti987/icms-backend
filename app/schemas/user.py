from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models.user import UserType
from app.schemas.permission import PermissionResponse


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    user_type: UserType = UserType.USER


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )
    email: EmailStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    user_type: UserType
    is_active: bool


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int


class UserDetailResponse(UserResponse):
    permissions: list[PermissionResponse]


class MessageResponse(BaseModel):
    message: str
