from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    language: Mapped[str | None] = mapped_column(
        String(10),
        default="ru",
        nullable=False
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        default="USD",
        nullable=False
    )

    regions: Mapped[list["Region"]] = relationship(
        secondary="user_regions",
        back_populates="users",
        lazy="selectin"
    )


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    ps_locale: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False
    )

    users: Mapped[list["User"]] = relationship(
        secondary="user_regions",
        back_populates="regions",
        lazy="selectin"
    )


class UserRegion(Base):
    __tablename__ = "user_regions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id"),
        primary_key=True
    )
