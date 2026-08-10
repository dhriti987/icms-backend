from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
)
from app.services.category_service import (
    create_category,
    deactivate_category,
    get_all_categories,
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_category(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=CategoryListResponse,
)
def list_categories(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    categories = get_all_categories(
        db=db,
        active_only=active_only,
    )

    return CategoryListResponse(
        categories=categories,
        total=len(categories),
    )


@router.patch(
    "/{category_id}/deactivate",
    response_model=CategoryResponse,
)
def deactivate_category_api(
    category_id: int,
    db: Session = Depends(get_db),
):
    try:
        return deactivate_category(
            db=db,
            category_id=category_id,
        )

    except ValueError as exc:
        if str(exc) == "Category not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
