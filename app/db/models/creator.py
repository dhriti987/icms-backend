from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
    PrimaryKeyConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from enum import Enum


class AgeGroup(str, Enum):
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_PLUS = "45+"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    gender: Mapped[Gender | None] = mapped_column(
        SQLEnum(
            Gender,
            name="gender",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=True,
    )

    age_group: Mapped[AgeGroup | None] = mapped_column(
        SQLEnum(
            AgeGroup,
            name="age_group",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    platforms = relationship(
        "CreatorPlatform",
        back_populates="creator",
        cascade="all, delete-orphan",
    )

    categories = relationship(
        "CreatorCategory",
        back_populates="creator",
        cascade="all, delete-orphan",
    )


class CreatorPlatform(Base):
    __tablename__ = "creator_platforms"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    creator_id: Mapped[int] = mapped_column(
        ForeignKey(
            "creators.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    platform_id: Mapped[int] = mapped_column(
        ForeignKey(
            "platforms.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    profile_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    audience_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    reel_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    story_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    dedicated_video_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    integrated_video_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    ugc_video_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    creator = relationship(
        "Creator",
        back_populates="platforms",
    )

    platform = relationship(
        "Platform",
        back_populates="creator_platforms",
    )

    __table_args__ = (
        UniqueConstraint(
            "platform_id",
            "username",
            name="uq_creator_platform_platform_username",
        ),
    )


class CreatorCategory(Base):
    __tablename__ = "creator_categories"

    creator_id: Mapped[int] = mapped_column(
        ForeignKey(
            "creators.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    creator = relationship(
        "Creator",
        back_populates="categories",
    )

    category = relationship(
        "Category",
        back_populates="creator_categories",
    )

    __table_args__ = (
        # Prevent the same category from being
        # assigned to the same creator twice.
        PrimaryKeyConstraint(
            "creator_id",
            "category_id",
            name="pk_creator_category",
        ),
    )
