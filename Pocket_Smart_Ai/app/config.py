from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"

    # Set SECRET_KEY in .env for production.
    secret_key: str = "change-this-development-secret"

    gemini_api_key: str = ""

    gemini_model: str = "gemini-3.6-flash"

    database_url: str = f"sqlite:///{BASE_DIR / 'pocketsmart.db'}"

    cors_origins: str = (
        "http://127.0.0.1:8000,http://localhost:8000"
    )

    use_mock_ai: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
        case_sensitive=False
    )

    @property
    def cors_list(self) -> list[str]:
        return [
            item.strip()
            for item in self.cors_origins.split(",")
            if item.strip()
        ]


settings = Settings()
