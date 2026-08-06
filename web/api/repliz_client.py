"""
web.api.repliz_client — Thin client for the Repliz public API.

Repliz API docs (reverse-engineered from jipraks/yt-short-clipper):
  Auth: HTTP Basic (access_key, secret_key) — get these from your Repliz
        dashboard under API / Developer settings.
  GET  https://api.repliz.com/public/account   -> list connected accounts
  POST https://api.repliz.com/public/schedule  -> publish/schedule a post

Place this file at: web/api/repliz_client.py
"""

from __future__ import annotations

import os
import requests
from requests.auth import HTTPBasicAuth

REPLIZ_BASE_URL = "https://api.repliz.com/public"


class ReplizError(Exception):
    pass


def _auth() -> HTTPBasicAuth:
    access_key = os.environ.get("REPLIZ_ACCESS_KEY", "")
    secret_key = os.environ.get("REPLIZ_SECRET_KEY", "")
    if not access_key or not secret_key:
        raise ReplizError(
            "REPLIZ_ACCESS_KEY / REPLIZ_SECRET_KEY belum di-set. "
            "Ambil dari dashboard Repliz (repliz.com/user/dashboard -> API settings)."
        )
    return HTTPBasicAuth(access_key, secret_key)


def list_accounts(page: int = 1, limit: int = 50) -> list[dict]:
    """Return connected social accounts from Repliz."""
    resp = requests.get(
        f"{REPLIZ_BASE_URL}/account",
        params={"page": page, "limit": limit},
        auth=_auth(),
        timeout=10,
    )
    if resp.status_code != 200:
        raise ReplizError(_extract_error(resp))
    return resp.json().get("docs", [])


def schedule_post(
    account_id: str,
    title: str,
    description: str,
    video_url: str,
    thumbnail_url: str = "",
    schedule_at: str | None = None,
) -> dict:
    """
    Schedule/publish a video post to a single connected account.

    video_url must be a publicly reachable URL (e.g. your ngrok tunnel +
    the /api/outputs/{job_id}/{filename} endpoint already exposed by
    web/api/routes/files.py).

    schedule_at: ISO 8601 datetime string, must be in the future
                 (Repliz caps this at 7 days out). Omit to publish ASAP.
    """
    payload = {
        "title": title,
        "description": description,
        "type": "video",
        "medias": [{"type": "video", "thumbnail": thumbnail_url, "url": video_url}],
        "accountId": account_id,
    }
    if schedule_at:
        payload["scheduleAt"] = schedule_at

    resp = requests.post(
        f"{REPLIZ_BASE_URL}/schedule",
        json=payload,
        auth=_auth(),
        headers={"accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise ReplizError(_extract_error(resp))
    return resp.json()


def _extract_error(resp: requests.Response) -> str:
    try:
        data = resp.json()
        return data.get("message", f"HTTP {resp.status_code}")
    except Exception:
        return f"HTTP {resp.status_code}: {resp.text[:200]}"
