from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_cloud_project: str = ""
    google_cloud_location: str = "europe-west1"
    firestore_collection_jobs: str = "job_listings"
    rss_feed_urls: list[str] = []
    embedding_model: str = "text-embedding-004"
    gemini_model: str = "gemini-2.5-flash"
    match_threshold: float = 0.65

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
