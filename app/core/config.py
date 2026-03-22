from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    upload_directory: str
    max_image_size: int
    redis_url: str
    bias_factor: float
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


settings = Settings()
