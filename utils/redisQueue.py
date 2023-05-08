from redis import Redis, StrictRedis
from rq import Queue

REDIS_CLIENT = StrictRedis(host='localhost', port=6379, db=0)
# REDIS_QUEUE = Queue(connection=Redis(host='localhost', port=6379, db=1))
