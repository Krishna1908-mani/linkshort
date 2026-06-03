from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


class ShortenRequest(BaseModel):
    original_url: str = Field(..., min_length=10, max_length=2048)
    custom_alias: Optional[str] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    redirect_type: int = Field(default=302)
    slug_length: int = Field(default=7, ge=5, le=12)
    generate_qr: bool = True

    @field_validator("redirect_type")
    @classmethod
    def validate_redirect_type(cls, value: int) -> int:
        if value not in (301, 302):
            raise ValueError("redirect_type must be 301 or 302")
        return value


class LinkResponse(BaseModel):
    id: str
    original_url: str
    slug: str
    short_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    redirect_type: int
    click_count: int
    qr_code: Optional[str] = None
    has_password: bool
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BlockDomainRequest(BaseModel):
    domain: str
    reason: Optional[str] = "Blocked by admin"


class PasswordUnlockRequest(BaseModel):
    password: str


class ApiMessage(BaseModel):
    success: bool
    message: str


class AnalyticsResponse(BaseModel):
    link: Dict[str, Any]
    total_clicks: int
    daily_clicks: List[Dict[str, Any]]
    recent_clicks: List[Dict[str, Any]]
    browsers: Dict[str, int]
    devices: Dict[str, int]
    operating_systems: Dict[str, int]
    referrers: Dict[str, int]
