from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    app_secret_key: str = "dev-secret"

    access_token_ttl_min: int = 15
    refresh_token_ttl_days: int = 7

    database_url: str


settings = Settings()
