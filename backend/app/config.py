from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongodb_url: str
    database_name: str
    
    # Ollama
    ollama_url: str
    vision_model: str = "llava:7b"
    text_model: str = "llama3.2"
    ollama_timeout: int = 300
    
    # File Upload
    upload_dir: str
    max_upload_size_mb: int = 50
    max_pdf_pages: int = 20

    class Config:
        env_file = ".env"

settings = Settings()