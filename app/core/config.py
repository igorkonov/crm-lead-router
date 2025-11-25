from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "CRM Lead Router"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./crm_lead_router.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
