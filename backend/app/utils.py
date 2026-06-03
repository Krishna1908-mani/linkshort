import base64
import io
import random
import re
import string
from datetime import datetime, timezone
from urllib.parse import urlparse

import qrcode
from fastapi import HTTPException, Request
from user_agents import parse as parse_user_agent
from .database import blocked_domains_collection, links_collection

ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
BASE62 = string.ascii_letters + string.digits


def serialize_doc(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    return result


def validate_url(url: str) -> str:
    if len(url) > 2048:
        raise HTTPException(status_code=400, detail="URL must be less than or equal to 2048 characters")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed")
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL host is required")
    if parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="URLs with embedded username or password are blocked")
    return url


def validate_alias(alias: str | None) -> str | None:
    if not alias:
        return None
    if not ALIAS_PATTERN.match(alias):
        raise HTTPException(status_code=400, detail="Custom alias must be 4-64 characters and contain only letters, numbers, hyphen, or underscore")
    return alias


def get_hostname(url: str) -> str:
    host = urlparse(url).hostname or ""
    return host.lower().removeprefix("www.")


async def ensure_domain_allowed(url: str) -> None:
    host = get_hostname(url)
    async for item in blocked_domains_collection.find({}):
        domain = item.get("domain", "").lower().removeprefix("www.")
        if host == domain or host.endswith("." + domain):
            raise HTTPException(status_code=403, detail=f"This domain is blocked: {domain}")


def make_qr_data_uri(short_url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


async def generate_unique_slug(length: int = 7) -> str:
    for _ in range(30):
        slug = "".join(random.choice(BASE62) for _ in range(length))
        exists = await links_collection.find_one({"slug": slug})
        if not exists:
            return slug
    raise HTTPException(status_code=500, detail="Unable to generate unique slug")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def parse_analytics(request: Request) -> dict:
    ua = parse_user_agent(request.headers.get("user-agent", ""))
    referrer = request.headers.get("referer") or "Direct"
    device = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC" if ua.is_pc else "Other"
    return {
        "ip_address": get_client_ip(request),
        "browser": ua.browser.family or "Unknown",
        "device": device,
        "os": ua.os.family or "Unknown",
        "referrer": referrer,
        "clicked_at": datetime.now(timezone.utc),
    }


def is_expired(link: dict) -> bool:
    expires_at = link.get("expires_at")
    if not expires_at:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > expires_at


def link_response(doc: dict) -> dict:
    short_url = doc.get("short_url") or ""
    return {
        "id": str(doc["_id"]),
        "original_url": doc["original_url"],
        "slug": doc["slug"],
        "short_url": short_url,
        "custom_alias": doc.get("custom_alias"),
        "expires_at": doc.get("expires_at"),
        "redirect_type": doc.get("redirect_type", 302),
        "click_count": doc.get("click_count", 0),
        "qr_code": doc.get("qr_code"),
        "has_password": bool(doc.get("password_hash")),
        "is_active": doc.get("is_active", True),
        "created_at": doc["created_at"],
    }
