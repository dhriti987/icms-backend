from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.creator import CreatorCreate, CreatorResponse
from app.services.creator_service import create_creator

# Use your existing authentication dependency here.
# Replace the import/name below with the one already used
# in your user-management endpoints.
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/creators",
    tags=["Creators"],
)


@router.post(
    "",
    response_model=CreatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_creator(
    data: CreatorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return create_creator(
            db=db,
            data=data,
            current_user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
