from rq import Connection, Queue, Worker
from config import DevelopmentConfig
from redis import Redis

with Connection(connection=Redis(host=DevelopmentConfig.REDIS_HOST,
                                port=DevelopmentConfig.REDIS_PORT,
                                password=DevelopmentConfig.REDIS_PASSWORD)):
    queue = Queue()
    Worker(queue).work()