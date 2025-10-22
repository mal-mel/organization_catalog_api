import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Organization Catalog API")
    VERSION: str = os.getenv("VERSION", "VERSION")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "catalog_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "catalog_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "organization_catalog")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Security
    API_KEY: str = os.getenv("API_KEY", "test-api-key-123")
    API_KEY_NAME: str = os.getenv("API_KEY_NAME", "API_KEY")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()