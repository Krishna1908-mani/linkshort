from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = Field(default=5000, alias="PORT")
    mongo_uri: str = Field(default="mongodb://127.0.0.1:27017/linkshortener_fastapi", alias="MONGO_URI")
    base_url: str = Field(default="http://localhost:5000", alias="BASE_URL")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    jwt_secret: str = Field(default="change_this_secret_key", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    admin_email: str = Field(default="admin@linkshort.com", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")
    rate_limit_window_seconds: int = Field(default=900, alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_max_requests: int = Field(default=120, alias="RATE_LIMIT_MAX_REQUESTS")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
