from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongodb_url: str
    database_name: str

    # JWT Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # LLM
    ollama_url: str
    vision_model: str = "qwen2.5-vl-7b-instruct"
    contemplation_model: str = "meta-llama-3.1-8b-instruct"
    text_model: str = "meta-llama-3.1-8b-instruct"
    ollama_timeout: int = 300

    # File Upload
    upload_dir: str
    max_upload_size_mb: int = 50
    max_pdf_pages: int = 20

    class Config:
        env_file = ".env"

settings = Settings()