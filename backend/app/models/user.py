"""User, profile, and skill models."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, json_type, str_array
from app.models.enums import AuthProvider, Intent, UserRole

profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("profile_id", GUID(), ForeignKey("user_profiles.id"), primary_key=True),
    Column("skill_id", GUID(), ForeignKey("skills.id"), primary_key=True),
    Column("proficiency", String(32), nullable=True),
)


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        Enum(AuthProvider, native_enum=False), default=AuthProvider.local
    )
    hashed_pw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oauth_sub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False), default=UserRole.user
    )
    settings_json: Mapped[dict] = mapped_column(json_type(), default=dict)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", uselist=False)


class Skill(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "skills"

    canonical_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    aliases: Mapped[list[str]] = mapped_column(str_array(), default=list)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embedding_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class UserProfile(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), index=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    experience_json: Mapped[dict] = mapped_column(json_type(), default=dict)
    intents: Mapped[list[str]] = mapped_column(str_array(), default=list)
    locations: Mapped[list[str]] = mapped_column(str_array(), default=list)
    is_remote_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    resume_blob_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences_json: Mapped[dict] = mapped_column(json_type(), default=dict)

    user: Mapped[User] = relationship(back_populates="profile")
    skills: Mapped[list[Skill]] = relationship(secondary=profile_skills)

    @property
    def intent_enums(self) -> list[Intent]:
        out: list[Intent] = []
        for i in self.intents or []:
            try:
                out.append(Intent(i))
            except ValueError:
                continue
        return out
