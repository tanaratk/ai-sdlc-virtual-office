from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+psycopg2://ai_sdlc_user:password@localhost:5432/ai_sdlc"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # OpenAI (optional)
    openai_api_key: str = ""


settings = Settings()
