from redis import Redis, StrictRedis
from utils.consts import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
from rq import Queue

REDIS_CLIENT = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
# REDIS_QUEUE = Queue(connection=Redis(host='localhost', port=6379, db=1))
