from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool


class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]
    total: int
