"""Tests for CORS origin parsing — guards the OPTIONS-preflight-400 regression.

Starlette matches the browser ``Origin`` header against ``allow_origins`` by
exact string, so a trailing slash or an unparsed comma-separated list silently
breaks every preflight. ``Settings.cors_origins`` normalizes both.
"""

from __future__ import annotations

from app.core.config import Settings


def test_single_origin() -> None:
    s = Settings(web_origin="https://opportunity-pulse.vercel.app")
    assert s.cors_origins == ["https://opportunity-pulse.vercel.app"]


def test_trailing_slash_stripped() -> None:
    # Browsers send Origin without a trailing slash; the stored value must match.
    s = Settings(web_origin="https://opportunity-pulse.vercel.app/")
    assert s.cors_origins == ["https://opportunity-pulse.vercel.app"]


def test_comma_separated_list_with_whitespace() -> None:
    s = Settings(web_origin="https://prod.vercel.app, https://preview.vercel.app/ ")
    assert s.cors_origins == [
        "https://prod.vercel.app",
        "https://preview.vercel.app",
    ]


def test_empty_segments_dropped() -> None:
    s = Settings(web_origin="https://a.app,,  ,https://b.app")
    assert s.cors_origins == ["https://a.app", "https://b.app"]


def test_preflight_returns_allow_origin_header(client) -> None:
    """An OPTIONS preflight from the allowed origin gets 200 + ACAO (not 400)."""
    resp = client.options(
        "/opportunities?page=1&limit=20",
        headers={
            "Origin": "http://localhost:3000",  # the test-env WEB_ORIGIN default
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
