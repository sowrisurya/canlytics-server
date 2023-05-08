from utils.redisQueue import REDIS_CLIENT

subscribers = REDIS_CLIENT.pubsub()
subscribers.subscribe("dataAdderSubscribe")
while True:
    message = subscribers.get_message(ignore_subscribe_messages=True, timeout=1)
    if message is not None:
        print(message)