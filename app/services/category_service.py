from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.category import Category
from app.schemas.category import CategoryCreate


def create_category(
    db: Session,
    data: CategoryCreate,
) -> Category:
    name = data.name.strip()

    existing_category = db.execute(
        select(Category).where(Category.name == name)
    ).scalar_one_or_none()

    if existing_category:
        raise ValueError("Category with this name already exists.")

    category = Category(
        name=name,
        is_active=True,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def deactivate_category(
    db: Session,
    category_id: int,
) -> Category:
    category = db.execute(
        select(Category).where(Category.id == category_id)
    ).scalar_one_or_none()

    if category is None:
        raise ValueError("Category not found.")

    if not category.is_active:
        raise ValueError("Category is already inactive.")

    category.is_active = False

    db.commit()
    db.refresh(category)

    return category


def get_all_categories(
    db: Session,
    active_only: bool = True,
) -> list[Category]:
    query = select(Category).order_by(Category.name)

    if active_only:
        query = query.where(Category.is_active.is_(True))

    result = db.execute(query)

    return list(result.scalars().all())
