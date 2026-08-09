from sqlalchemy import select

from app.core.permissions import PERMISSION_DEFINITIONS
from app.db.database import SessionLocal
from app.db.models.permission import Permission


def seed_permissions() -> None:
    db = SessionLocal()

    try:
        created_count = 0
        existing_count = 0

        for module, actions in PERMISSION_DEFINITIONS.items():
            for action in actions:
                existing_permission = db.scalar(
                    select(Permission).where(
                        Permission.module == module,
                        Permission.action == action,
                    )
                )

                if existing_permission:
                    existing_count += 1
                    continue

                permission = Permission(
                    module=module,
                    action=action,
                )

                db.add(permission)
                created_count += 1

        db.commit()

        print("\nPermission seeding completed.")
        print(f"Created:  {created_count}")
        print(f"Existing: {existing_count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()
