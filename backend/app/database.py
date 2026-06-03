from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_uri)
db = client.get_default_database()

links_collection = db["links"]
analytics_collection = db["analytics"]
admins_collection = db["admins"]
blocked_domains_collection = db["blocked_domains"]


async def create_indexes() -> None:
    await links_collection.create_index("slug", unique=True)
    await links_collection.create_index("original_url")
    await analytics_collection.create_index("slug")
    await analytics_collection.create_index("clicked_at")
    await admins_collection.create_index("email", unique=True)
    await blocked_domains_collection.create_index("domain", unique=True)
