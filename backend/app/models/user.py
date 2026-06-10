"""User, profile, and skill models."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import AuthProvider, Intent, UserRole

profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("profile_id", UUID(as_uuid=True), ForeignKey("user_profiles.id"), primary_key=True),
    Column("skill_id", UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True),
    Column("proficiency", String(32), nullable=True),
)


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        ENUM(AuthProvider, name="auth_provider"), default=AuthProvider.local
    )
    hashed_pw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oauth_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(ENUM(UserRole, name="user_role"), default=UserRole.user)
    settings_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class Skill(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "skills"

    canonical_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embedding_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class UserProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    experience_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    intents: Mapped[list[Intent]] = mapped_column(
        ARRAY(ENUM(Intent, name="intent")), default=list
    )
    locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_remote_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    resume_blob_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    user: Mapped[User] = relationship(back_populates="profile")
    skills: Mapped[list[Skill]] = relationship(secondary=profile_skills)
