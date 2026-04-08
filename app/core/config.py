from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    upload_directory: Path = Path("static/images")
    raw_upload_directory: Path = Path("static/images/raw")
    max_image_size: int
    redis_url: str
    bias_factor: float
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    webp_quality: int = 90

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    def create_upload_dirs(self):
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.raw_upload_directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_upload_dirs()
