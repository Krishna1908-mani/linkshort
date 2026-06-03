from collections import Counter, defaultdict
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import DESCENDING
from ..config import get_settings
from ..database import analytics_collection, links_collection
from ..schemas import ShortenRequest, LinkResponse, ApiMessage
from ..security import get_current_admin, hash_password
from ..utils import (
    validate_url, validate_alias, ensure_domain_allowed, generate_unique_slug,
    make_qr_data_uri, link_response, is_expired
)

settings = get_settings()
router = APIRouter(prefix="/links", tags=["Links"])


@router.post("/shorten", response_model=LinkResponse)
async def shorten_url(payload: ShortenRequest):
    original_url = validate_url(payload.original_url.strip())
    custom_alias = validate_alias(payload.custom_alias.strip() if payload.custom_alias else None)
    await ensure_domain_allowed(original_url)

    slug = custom_alias or await generate_unique_slug(payload.slug_length)
    existing = await links_collection.find_one({"slug": slug})
    if existing:
        suggestions = [await generate_unique_slug(payload.slug_length) for _ in range(3)]
        raise HTTPException(status_code=409, detail={"message": "Alias already exists", "suggestions": suggestions})

    short_url = f"{settings.base_url.rstrip('/')}/{slug}"
    now = datetime.now(timezone.utc)
    doc = {
        "original_url": original_url,
        "slug": slug,
        "short_url": short_url,
        "custom_alias": custom_alias,
        "password_hash": hash_password(payload.password) if payload.password else None,
        "expires_at": payload.expires_at,
        "redirect_type": payload.redirect_type,
        "click_count": 0,
        "qr_code": make_qr_data_uri(short_url) if payload.generate_qr else None,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    result = await links_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return link_response(doc)


@router.get("", response_model=list[LinkResponse])
async def list_links(
    search: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=200),
    admin: dict = Depends(get_current_admin),
):
    query = {}
    if search:
        query = {"$or": [
            {"slug": {"$regex": search, "$options": "i"}},
            {"original_url": {"$regex": search, "$options": "i"}},
        ]}
    cursor = links_collection.find(query).sort("created_at", DESCENDING).limit(limit)
    return [link_response(doc) async for doc in cursor]


@router.get("/slug/{slug}/preview", response_model=LinkResponse)
async def preview_by_slug(slug: str):
    link = await links_collection.find_one({"slug": slug})
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if is_expired(link):
        raise HTTPException(status_code=410, detail="Link has expired")
    return link_response(link)


@router.get("/slug/{slug}/analytics")
async def analytics_by_slug(slug: str):
    link = await links_collection.find_one({"slug": slug})
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    clicks = [doc async for doc in analytics_collection.find({"slug": slug}).sort("clicked_at", DESCENDING).limit(500)]
    browsers = Counter(c.get("browser", "Unknown") for c in clicks)
    devices = Counter(c.get("device", "Unknown") for c in clicks)
    operating_systems = Counter(c.get("os", "Unknown") for c in clicks)
    referrers = Counter(c.get("referrer", "Direct") for c in clicks)
    daily = defaultdict(int)
    recent = []
    for c in clicks:
        clicked_at = c.get("clicked_at")
        if clicked_at:
            daily[clicked_at.strftime("%Y-%m-%d")] += 1
        recent.append({
            "browser": c.get("browser", "Unknown"),
            "device": c.get("device", "Unknown"),
            "os": c.get("os", "Unknown"),
            "referrer": c.get("referrer", "Direct"),
            "ip_address": c.get("ip_address", "unknown"),
            "clicked_at": clicked_at,
        })

    return {
        "link": link_response(link),
        "total_clicks": link.get("click_count", 0),
        "daily_clicks": [{"date": k, "clicks": v} for k, v in sorted(daily.items())],
        "recent_clicks": recent[:30],
        "browsers": dict(browsers),
        "devices": dict(devices),
        "operating_systems": dict(operating_systems),
        "referrers": dict(referrers),
    }


@router.delete("/{link_id}", response_model=ApiMessage)
async def delete_link(link_id: str, admin: dict = Depends(get_current_admin)):
    if not ObjectId.is_valid(link_id):
        raise HTTPException(status_code=400, detail="Invalid link id")
    result = await links_collection.delete_one({"_id": ObjectId(link_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    return ApiMessage(success=True, message="Link deleted successfully")
