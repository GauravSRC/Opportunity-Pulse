"""Shared schema primitives."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    limit: int
    total: int


class Ack(BaseModel):
    ok: bool = True
    detail: str | None = None
