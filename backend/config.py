from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/newsfeed"
    llm_provider: str = "anthropic/claude-sonnet-4-20250514"
    llm_api_key: str = ""
    admin_api_key: str = "change-me-in-production"
    youtube_api_key: str = ""
    twitter_bearer_token: str = ""
    github_token: str = ""
    ingest_schedule: str = "0 6 * * *"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
