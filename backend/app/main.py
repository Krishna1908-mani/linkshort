import logging
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from .config import get_settings
from .database import create_indexes, links_collection, analytics_collection
from .deps import RateLimitMiddleware, SecurityHeadersMiddleware
from .routers import auth, links, admin
from .security import verify_password
from .utils import parse_analytics, is_expired

settings = get_settings()
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger("linkshort")

app = FastAPI(
    title="LinkShort Pro FastAPI Backend",
    description="Full-stack URL Shortener API with QR code, analytics, password protection, expiry, and admin panel.",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router, prefix="/api")
app.include_router(links.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    await create_indexes()
    logger.info("LinkShort Pro FastAPI backend started")


@app.get("/health")
async def health():
    return {"success": True, "message": "LinkShort FastAPI backend is running"}


@app.get("/{slug}")
async def redirect_slug(slug: str, request: Request):
    link = await links_collection.find_one({"slug": slug})
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if not link.get("is_active", True):
        raise HTTPException(status_code=403, detail="This link is disabled")
    if is_expired(link):
        raise HTTPException(status_code=410, detail="This link has expired")
    if link.get("password_hash"):
        return HTMLResponse(password_form(slug))
    await record_click(link, slug, request)
    return RedirectResponse(url=link["original_url"], status_code=link.get("redirect_type", 302))


@app.post("/{slug}/unlock")
async def unlock_slug(slug: str, request: Request, password: str = Form(...)):
    link = await links_collection.find_one({"slug": slug})
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if is_expired(link):
        raise HTTPException(status_code=410, detail="This link has expired")
    if not verify_password(password, link.get("password_hash", "")):
        return HTMLResponse(password_form(slug, "Wrong password. Try again."), status_code=401)
    await record_click(link, slug, request)
    return RedirectResponse(url=link["original_url"], status_code=302)


async def record_click(link: dict, slug: str, request: Request) -> None:
    analytics = parse_analytics(request)
    analytics.update({"link_id": str(link["_id"]), "slug": slug})
    await analytics_collection.insert_one(analytics)
    await links_collection.update_one(
        {"_id": link["_id"]},
        {"$inc": {"click_count": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}}
    )


def password_form(slug: str, error: str = "") -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Password Required</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; }}
            .card {{ width: 360px; background: #111827; border: 1px solid #334155; border-radius: 18px; padding: 28px; box-shadow: 0 20px 50px rgba(0,0,0,.35); }}
            input {{ width: 100%; padding: 14px; border-radius: 10px; border: 1px solid #475569; background: #020617; color: white; margin: 12px 0; box-sizing: border-box; }}
            button {{ width: 100%; padding: 14px; border-radius: 10px; border: 0; background: linear-gradient(135deg, #2563eb, #7c3aed); color: white; font-weight: 700; cursor: pointer; }}
            .error {{ color: #fca5a5; margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <form class="card" method="post" action="/{slug}/unlock">
            <h2>Protected Link</h2>
            <p>This short link requires a password.</p>
            <div class="error">{error}</div>
            <input type="password" name="password" placeholder="Enter password" required />
            <button type="submit">Open Link</button>
        </form>
    </body>
    </html>
    """
