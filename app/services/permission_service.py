from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.permission import Permission


def get_permissions(
    db: Session,
) -> list[Permission]:
    return list(
        db.scalars(
            select(Permission).order_by(
                Permission.module,
                Permission.action,
            )
        ).all()
    )
