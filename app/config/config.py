from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int = 0
    cache_ttl: int = 60

    model_config = SettingsConfigDict(env_file=".env.example")

# create instance of this class
settings = Settings()