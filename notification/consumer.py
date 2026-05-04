import redis as redis_lib
import time
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

redis = redis_lib.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password if settings.redis_password else None,
    decode_responses=True
)

STREAMS = {
    "order_completed": "notification-group-orders",
    "refund_order": "notification-group-refunds",
}

for stream, group in STREAMS.items():
    try:
        redis.xgroup_create(stream, group, id="0", mkstream=True)
    except:
        print(f"Grupa {group} već postoji.")

while True:
    for stream, group in STREAMS.items():
        try:
            results = redis.xreadgroup(group, "notification-consumer",
                                       {stream: ">"}, count=1, block=1000)
            if results:
                for result in results:
                    data = result[1][0][1]
                    entry_id = result[1][0][0]

                    if stream == "order_completed":
                        print(f"Obaveštenje: Porudžbina {data.get('pk', 'N/A')} "
                              f"je uspešno kreirana i plaćena.")
                    elif stream == "refund_order":
                        print(f"Obaveštenje: Za porudžbinu {data.get('pk', 'N/A')} "
                              f"je iniciran povrat sredstava.")

                    redis.xack(stream, group, entry_id)
        except Exception as e:
            print(f"Greška: {e}")
    time.sleep(1)