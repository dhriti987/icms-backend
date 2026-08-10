from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models.platform import Platform


PLATFORMS = [
    "Instagram",
    "YouTube",
]


def seed_platforms():
    db = SessionLocal()

    try:
        for platform_name in PLATFORMS:
            result = db.execute(select(Platform).where(Platform.name == platform_name))

            existing_platform = result.scalar_one_or_none()

            if existing_platform:
                print(f"Already exists: {platform_name}")
                continue

            platform = Platform(
                name=platform_name,
                is_active=True,
            )

            db.add(platform)

            print(f"Added: {platform_name}")

        db.commit()

        print("\nPlatform seeding completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_platforms()
