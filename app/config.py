from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    DATABASE_URL: str = "postgresql://snapshort_user:snapshort_pass@localhost:5432/snapshort"

    AWS_REGION: str = "us-east-1"
    DYNAMODB_TABLE_NAME: str = "snapshort-links"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    DYNAMODB_ENDPOINT_URL: str = ""

    SHORT_CODE_LENGTH: int = 7
    BASE_URL: str = "http://localhost:8000"

    DEFAULT_LINK_TTL_DAYS: int = 0


settings = Settings()
