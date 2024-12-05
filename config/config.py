from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_DB_USER: str
    SERVICE_DB_PASSWORD: str
    SERVICE_DB_HOSTNAME: str
    SERVICE_DB_PORT: str
    SERVICE_DB : str
    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_USER: str
    MONGO_PASS: str
    MONGO_DB: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()