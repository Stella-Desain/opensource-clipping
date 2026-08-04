"""
web.api.routes.repliz_publish — Publish rendered clips to Repliz.

Place this file at: web/api/routes/repliz_publish.py
Then wire it into web/api/app.py (see instructions below the file).
"""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from ..repliz_client import list_accounts, schedule_post, ReplizError

router = APIRouter(prefix="/api/repliz", tags=["repliz"])


class PublishRequest(BaseModel):
    account_ids: list[str]          # one or more Repliz account IDs to post to
    title: str
    description: str = ""
    video_url: str                  # e.g. f"{ngrok_url}/api/outputs/{job_id}/{filename}"
    thumbnail_url: str = ""
    schedule_at: str | None = None  # ISO 8601, optional


@router.get("/accounts")
async def get_repliz_accounts() -> dict:
    """List social accounts connected in the user's Repliz dashboard."""
    try:
        accounts = list_accounts()
    except ReplizError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"accounts": accounts, "total": len(accounts)}


@router.post("/publish")
async def publish_to_repliz(req: PublishRequest) -> dict:
    """Publish/schedule a rendered clip to one or more connected accounts."""
    if not req.account_ids:
        raise HTTPException(status_code=400, detail="account_ids tidak boleh kosong")

    results = []
    for account_id in req.account_ids:
        try:
            result = schedule_post(
                account_id=account_id,
                title=req.title,
                description=req.description,
                video_url=req.video_url,
                thumbnail_url=req.thumbnail_url,
                schedule_at=req.schedule_at,
            )
            results.append({"account_id": account_id, "success": True, "result": result})
        except ReplizError as e:
            results.append({"account_id": account_id, "success": False, "error": str(e)})

    return {"results": results}
