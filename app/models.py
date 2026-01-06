from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# Association table for many-to-many relationship between inspirations and tags
inspiration_tag_table = Table(
    "inspiration_tags",
    Base.metadata,
    Column("inspiration_id", ForeignKey("inspirations.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    inspirations: Mapped[List["Inspiration"]] = relationship(
        "Inspiration", secondary=inspiration_tag_table, back_populates="tags"
    )


class Inspiration(Base, TimestampMixin):
    __tablename__ = "inspirations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    color_palette: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nail_shape: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    length: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    price_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration_estimate_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    tags: Mapped[List[Tag]] = relationship(
        "Tag", secondary=inspiration_tag_table, back_populates="inspirations"
    )
    communication_cards: Mapped[List["CommunicationCard"]] = relationship(
        "CommunicationCard", back_populates="inspiration"
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")


class Favorite(Base, TimestampMixin):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    inspiration_id: Mapped[int] = mapped_column(Integer, ForeignKey("inspirations.id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="favorites")
    inspiration: Mapped[Inspiration] = relationship("Inspiration")


class CommunicationCard(Base, TimestampMixin):
    __tablename__ = "communication_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inspiration_id: Mapped[int] = mapped_column(Integer, ForeignKey("inspirations.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    material_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timing_estimate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    inspiration: Mapped[Inspiration] = relationship("Inspiration", back_populates="communication_cards")
