from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PermissionResponse(BaseModel):
    module: str
    actions: list[str]


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    username: str
    email: str
    user_type: str
    is_active: bool
    permissions: dict[str, list[str]] | dict[str, bool]