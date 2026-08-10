from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.platform import Platform


def get_all_platforms(
    db: Session,
    active_only: bool = True,
) -> list[Platform]:
    query = select(Platform).order_by(Platform.name)

    if active_only:
        query = query.where(Platform.is_active.is_(True))

    result = db.execute(query)

    return list(result.scalars().all())
