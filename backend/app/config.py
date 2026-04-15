from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    mongodb_url: str
    database_name: str

    # JWT Auth — JWT_SECRET must be set in environment; no default allowed
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60  # 1 hour

    # LLM
    ollama_url: str
    vision_model: str = "qwen2.5-vl-7b-instruct"
    contemplation_model: str = "meta-llama-3.1-8b-instruct"
    text_model: str = "meta-llama-3.1-8b-instruct"
    ollama_timeout: int = 300

    # File upload
    upload_dir: str
    max_upload_size_mb: int = 50
    max_pdf_pages: int = 20


settings = Settings()
