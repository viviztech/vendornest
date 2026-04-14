from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "VendorNest"
    app_env: str = "development"
    app_secret_key: str
    app_base_url: str = "http://localhost:8000"
    debug: bool = True

    # Database
    database_url: str
    async_database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str = "vendornest-media"
    aws_cloudfront_url: str = ""

    # Email (SMTP - Gmail free tier)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""   # Gmail App Password
    smtp_from_email: str = ""
    smtp_from_name: str = "VendorNest"
    ses_reply_to: str = "support@vendornest.in"

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # Delhivery
    delhivery_api_key: str = ""
    delhivery_base_url: str = "https://track.delhivery.com"
    delhivery_pickup_location: str = "VendorNest-Warehouse"

    # WhatsApp
    whatsapp_enabled: bool = False
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""

    # JWT / Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    otp_expire_minutes: int = 10

    # Superadmin
    superadmin_email: str = "admin@vendornest.in"
    superadmin_password: str = "Admin@1234"
    superadmin_name: str = "Super Admin"

    # Defaults
    default_commission_percent: float = 5.0
    default_page_size: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def media_base_url(self) -> str:
        if self.aws_cloudfront_url:
            return self.aws_cloudfront_url
        return f"https://{self.aws_s3_bucket}.s3.{self.aws_region}.amazonaws.com"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
