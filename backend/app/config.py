from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Black Swan AI War Room"
    environment: str = "development"

    database_url: str = "sqlite:///./war_room.db"

    allowed_origins: str = "http://localhost:5173"
    max_request_bytes: int = 1_000_000

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.1:8b"
    enable_ollama: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()