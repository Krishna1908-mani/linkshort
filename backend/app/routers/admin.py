from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from ..database import blocked_domains_collection, links_collection, analytics_collection
from ..schemas import BlockDomainRequest, ApiMessage
from ..security import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def admin_stats(admin: dict = Depends(get_current_admin)):
    total_links = await links_collection.count_documents({})
    active_links = await links_collection.count_documents({"is_active": True})
    total_click_docs = await analytics_collection.count_documents({})
    blocked_domains = await blocked_domains_collection.count_documents({})
    return {
        "total_links": total_links,
        "active_links": active_links,
        "total_clicks": total_click_docs,
        "blocked_domains": blocked_domains,
    }


@router.post("/blocked-domains", response_model=ApiMessage)
async def block_domain(payload: BlockDomainRequest, admin: dict = Depends(get_current_admin)):
    domain = payload.domain.lower().replace("https://", "").replace("http://", "").split("/")[0].removeprefix("www.")
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
    await blocked_domains_collection.update_one(
        {"domain": domain},
        {"$set": {"domain": domain, "reason": payload.reason, "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return ApiMessage(success=True, message=f"Domain blocked: {domain}")


@router.get("/blocked-domains")
async def list_blocked_domains(admin: dict = Depends(get_current_admin)):
    domains = []
    async for doc in blocked_domains_collection.find({}).sort("created_at", -1):
        domains.append({"id": str(doc["_id"]), "domain": doc["domain"], "reason": doc.get("reason"), "created_at": doc.get("created_at")})
    return domains


@router.delete("/blocked-domains/{domain}", response_model=ApiMessage)
async def unblock_domain(domain: str, admin: dict = Depends(get_current_admin)):
    clean = domain.lower().removeprefix("www.")
    await blocked_domains_collection.delete_one({"domain": clean})
    return ApiMessage(success=True, message=f"Domain removed: {clean}")
