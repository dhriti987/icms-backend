from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.platform import PlatformListResponse
from app.services.platform_service import get_all_platforms


router = APIRouter(
    prefix="/platforms",
    tags=["Platforms"],
)


@router.get(
    "",
    response_model=PlatformListResponse,
)
def list_platforms(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    platforms = get_all_platforms(
        db=db,
        active_only=active_only,
    )

    return PlatformListResponse(
        platforms=platforms,
        total=len(platforms),
    )
