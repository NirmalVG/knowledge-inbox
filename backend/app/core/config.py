from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    cohere_api_key: str
    groq_api_key: str
    database_path: str = "./knowledge_inbox.db"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()