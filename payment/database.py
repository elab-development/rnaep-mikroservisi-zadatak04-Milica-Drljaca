from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from redis_om import get_redis_connection

class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env")
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

settings = Settings()

redis = get_redis_connection(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True
)
