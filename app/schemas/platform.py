from pydantic import BaseModel, ConfigDict


class PlatformResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool


class PlatformListResponse(BaseModel):
    platforms: list[PlatformResponse]
    total: int
