from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TELEGRAM BOT
    BOT_TOKEN: str = ""

    # QDRANT
    QDRANT_URL: str = ""
    QDRANT_COLLECTION_NAME: str = ""

    # EMBEDDING
    EMBEDDING_URL: str = ""
    EMBEDDING_TOKEN: str = ""

    # OPENAI
    OPENAI_API_KEY: str = ""

    # LOG
    LOG_LEVEL: str = ""
    LOG_FILENAME: str = ""

    # POSTGRES
    DB_URL: str = ""
    DB_ECHO: bool = False
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
