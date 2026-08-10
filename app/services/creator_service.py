from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.category import Category
from app.db.models.creator import Creator
from app.db.models.creator import CreatorCategory
from app.db.models.creator import CreatorPlatform
from app.db.models.platform import Platform
from app.schemas.creator import CreatorCreate


def normalize_username(username: str) -> str:
    """
    Normalize username for consistent duplicate checking.
    """
    return username.strip().lower()


def normalize_profile_url(url: str) -> str:
    """
    Normalize profile URL.

    - Removes leading/trailing whitespace
    - Converts scheme and hostname to lowercase
    - Removes query parameters
    - Removes URL fragments
    - Removes trailing slash from path
    """
    url = str(url).strip()

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            "",
            "",
        )
    )


def create_creator(
    db: Session,
    data: CreatorCreate,
    current_user_id: int,
) -> Creator:
    try:
        # ---------------------------------------------------------
        # 1. Validate platforms
        # ---------------------------------------------------------

        platform_ids = [platform_data.platform_id for platform_data in data.platforms]

        # Prevent the same platform from being supplied twice
        if len(platform_ids) != len(set(platform_ids)):
            raise ValueError("A creator cannot have the same platform more than once.")

        result = db.execute(
            select(Platform).where(
                Platform.id.in_(platform_ids),
                Platform.is_active.is_(True),
            )
        )

        platforms = list(result.scalars().all())

        if len(platforms) != len(platform_ids):
            raise ValueError("One or more platforms are invalid or inactive.")

        platform_map = {platform.id: platform for platform in platforms}

        # ---------------------------------------------------------
        # 2. Validate categories
        # ---------------------------------------------------------

        category_ids = data.category_ids

        if category_ids:
            # Prevent duplicate category IDs
            if len(category_ids) != len(set(category_ids)):
                raise ValueError("Duplicate category IDs are not allowed.")

            result = db.execute(
                select(Category).where(
                    Category.id.in_(category_ids),
                    Category.is_active.is_(True),
                )
            )

            categories = list(result.scalars().all())

            if len(categories) != len(category_ids):
                raise ValueError("One or more categories are invalid or inactive.")

        # ---------------------------------------------------------
        # 3. Normalize and validate platform data
        # ---------------------------------------------------------

        normalized_platforms = []

        for platform_data in data.platforms:
            normalized_username = normalize_username(platform_data.username)

            normalized_url = normalize_profile_url(str(platform_data.profile_url))

            # Check duplicate URL
            existing_url = db.execute(
                select(CreatorPlatform).where(
                    CreatorPlatform.profile_url == normalized_url
                )
            ).scalar_one_or_none()

            if existing_url:
                raise ValueError("A creator with this profile URL already exists.")

            # Check duplicate platform + username
            existing_username = db.execute(
                select(CreatorPlatform).where(
                    CreatorPlatform.platform_id == platform_data.platform_id,
                    CreatorPlatform.username == normalized_username,
                )
            ).scalar_one_or_none()

            if existing_username:
                platform_name = platform_map[platform_data.platform_id].name

                raise ValueError(
                    f"Username '{normalized_username}' "
                    f"already exists on {platform_name}."
                )

            normalized_platforms.append(
                {
                    "platform_id": platform_data.platform_id,
                    "profile_url": normalized_url,
                    "username": normalized_username,
                    "audience_count": platform_data.audience_count,
                    "reel_rate": platform_data.reel_rate,
                    "story_rate": platform_data.story_rate,
                    "dedicated_video_rate": (platform_data.dedicated_video_rate),
                    "integrated_video_rate": (platform_data.integrated_video_rate),
                    "ugc_video_rate": (platform_data.ugc_video_rate),
                }
            )

        # ---------------------------------------------------------
        # 4. Create creator
        # ---------------------------------------------------------

        creator = Creator(
            name=data.name.strip(),
            gender=data.gender,
            age_group=data.age_group,
            email=data.email,
            phone=data.phone,
            state=data.state,
            city=data.city,
            created_by=current_user_id,
            updated_by=current_user_id,
        )

        db.add(creator)

        # Flush so creator.id becomes available
        db.flush()

        # ---------------------------------------------------------
        # 5. Create creator-platform records
        # ---------------------------------------------------------

        for platform_data in normalized_platforms:
            creator_platform = CreatorPlatform(
                creator_id=creator.id,
                platform_id=platform_data["platform_id"],
                profile_url=platform_data["profile_url"],
                username=platform_data["username"],
                audience_count=platform_data["audience_count"],
                reel_rate=platform_data["reel_rate"],
                story_rate=platform_data["story_rate"],
                dedicated_video_rate=(platform_data["dedicated_video_rate"]),
                integrated_video_rate=(platform_data["integrated_video_rate"]),
                ugc_video_rate=(platform_data["ugc_video_rate"]),
                created_by=current_user_id,
                updated_by=current_user_id,
            )

            db.add(creator_platform)

        # ---------------------------------------------------------
        # 6. Create creator-category relationships
        # ---------------------------------------------------------

        for category_id in category_ids:
            creator_category = CreatorCategory(
                creator_id=creator.id,
                category_id=category_id,
            )

            db.add(creator_category)

        # ---------------------------------------------------------
        # 7. Commit everything together
        # ---------------------------------------------------------

        db.commit()

        # Reload creator from database
        db.refresh(creator)

        return creator

    except Exception:
        db.rollback()
        raise


def get_creator_by_id(
    db: Session,
    creator_id: int,
) -> Creator | None:
    result = db.execute(
        select(Creator)
        .options(
            selectinload(Creator.platforms).selectinload(CreatorPlatform.platform),
            selectinload(Creator.categories).selectinload(CreatorCategory.category),
        )
        .where(Creator.id == creator_id)
    )

    return result.scalar_one_or_none()
