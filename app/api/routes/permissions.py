from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.admin import require_super_admin
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.permission import PermissionResponse
from app.services.permission_service import get_permissions


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "",
    response_model=list[PermissionResponse],
)
def list_permissions(
    _: Annotated[
        User,
        Depends(require_super_admin),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return get_permissions(db)
