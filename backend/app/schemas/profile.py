"""Profile schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr

from app.models.enums import Intent


class ProfileCreate(BaseModel):
    email: EmailStr
    headline: str | None = None
    skills: list[str] = []
    intents: list[Intent] = []
    locations: list[str] = []
    is_remote_ok: bool = True
    education: dict = {}
    experience: dict = {}
    preferences: dict = {}


class ProfileUpdate(BaseModel):
    headline: str | None = None
    skills: list[str] | None = None
    intents: list[Intent] | None = None
    locations: list[str] | None = None
    is_remote_ok: bool | None = None
    preferences: dict | None = None


class ProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    headline: str | None
    skills: list[str]
    intents: list[Intent]
    locations: list[str]
    is_remote_ok: bool


class ResumeParseResult(BaseModel):
    parsed: bool
    headline: str | None = None
    skills: list[str] = []
    note: str | None = None
