import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from .config import get_settings

settings = get_settings()
request_log: dict[str, deque] = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_max_requests
        bucket = request_log[ip]
        while bucket and bucket[0] < now - window:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        bucket.append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
