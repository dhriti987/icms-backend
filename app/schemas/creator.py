from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.db.models.creator import AgeGroup, Gender


class CreatorPlatformCreate(BaseModel):
    platform_id: int

    profile_url: HttpUrl

    username: str = Field(
        min_length=1,
        max_length=150,
    )

    audience_count: int = Field(
        ge=0,
    )

    reel_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )

    story_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )

    dedicated_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )

    integrated_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )

    ugc_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )


class CreatorCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    gender: Gender | None = None

    age_group: AgeGroup | None = None

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    platforms: list[CreatorPlatformCreate] = Field(
        min_length=1,
    )

    category_ids: list[int] = Field(
        default_factory=list,
    )


class CreatorPlatformUpdate(BaseModel):
    platform_id: int | None = None
    profile_url: HttpUrl | None = None
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    audience_count: int | None = Field(
        default=None,
        ge=0,
    )

    reel_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )
    story_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )
    dedicated_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )
    integrated_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )
    ugc_video_rate: Decimal | None = Field(
        default=None,
        ge=0,
    )


class CreatorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    gender: Gender | None = None
    age_group: AgeGroup | None = None

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )


class PlatformResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CreatorPlatformResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: PlatformResponse
    profile_url: str
    username: str
    audience_count: int

    reel_rate: Decimal | None
    story_rate: Decimal | None
    dedicated_video_rate: Decimal | None
    integrated_video_rate: Decimal | None
    ugc_video_rate: Decimal | None


class CreatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

    gender: Gender | None
    age_group: AgeGroup | None

    email: str | None
    phone: str | None
    state: str | None
    city: str | None

    platforms: list[CreatorPlatformResponse]
    categories: list[CategoryResponse]
