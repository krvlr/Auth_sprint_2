import time

from elasticsearch import Elasticsearch
from redis import Redis
from settings import test_settings

if __name__ == "__main__":
    es_client = Elasticsearch(
        hosts=f"{test_settings.elastic_host}:{test_settings.elastic_port}",
        validate_cert=False,
        use_ssl=False,
    )

    redis_client = Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port,
        ssl=False,
        socket_connect_timeout=100,
    )

    while True:
        if es_client.ping() and redis_client.ping():
            break
        time.sleep(1)
