from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REDIS_HOST: str
    REDIS_PORT: int
    PROFILING_ENABLED: bool = True
    SLOW_THRESHOLD_MS: float = 500.0
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    FROM_EMAIL: str = "noreply@skilllink.kz"
    DATABASE_URL_SYNC: str = ""

    class Config:
        env_file = ".env"

settings  = Settings()