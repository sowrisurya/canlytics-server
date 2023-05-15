from utils import MQTTClient
import time, json, asyncio
from utils import MQTT_TOPIC, REDIS_CLIENT
import threading


class DataAdderQueue(object):
	def __init__(self):
		self.__mqtt_client = MQTTClient(callback=self.recv_data_callback)
		self.__subscriber = REDIS_CLIENT.pubsub()
		self.__subscriber.subscribe("dataAdderPublish")
		self.__crnt_msg = None

	# def add_data(self, data):
	# 	REDIS_QUEUE.enqueue(self.__mqtt_client.publish, MQTT_TOPIC, data)

	def wait_for_messages(self):
		while True:
			msg = self.__subscriber.get_message(ignore_subscribe_messages=True)
			if msg is not None:
				data = json.loads(msg["data"].decode("utf-8"))
				if not str(data["data"]).startswith("server>"):
					continue
				self.__crnt_msg = data
				self.__mqtt_client.publish(MQTT_TOPIC, data["data"])
				self.wait_for_mqtt_msg(timeout = 30)
				time.sleep(2)
			else:
				time.sleep(0.1)

	async def wait_for_messages_async(self):
		while True:
			msg = self.__subscriber.get_message(ignore_subscribe_messages=True)
			if msg is not None:
				data = json.loads(msg["data"].decode("utf-8"))
				if not str(data["data"]).startswith("server>"):
					continue
				self.__crnt_msg = data
				self.__mqtt_client.publish(MQTT_TOPIC, data["data"])
				await self.wait_for_mqtt_msg_async(timeout = 30)
				await asyncio.sleep(2)
			else:
				await asyncio.sleep(0.1)

	def wait_for_mqtt_msg(self, timeout = 10):
		start_time = time.time()
		while self.__crnt_msg is not None and time.time() - start_time < timeout:
			time.sleep(0.1)

	async def wait_for_mqtt_msg_async(self, timeout = 10):
		start_time = time.time()
		while self.__crnt_msg is not None and time.time() - start_time < timeout:
			await asyncio.sleep(0.1)

	def recv_data_callback(self, message):
		try:
			# data = message.payload.decode("utf-8")
			data = message["payload"]
		except Exception as e:
			data = message
		if data is None or not isinstance(data, str):
			return
		if data.startswith("server>"):
			return
		data = data.lower()
		REDIS_CLIENT.publish("dataAdderSubscribe", json.dumps({"crnt_msg": self.__crnt_msg, "data": data}))
		self.__crnt_msg = None

	async def configure(self):
		await self.__mqtt_client.subscribe(MQTT_TOPIC)
		# def run_loop():
		# 	while True:
		# 		try:
		# 			self.__mqtt_client.subscribe(MQTT_TOPIC)
		# 		except Exception as e:
		# 			print("Error in subscribing to topic: {}".format(e))
		# 			time.sleep(1)
		# thrd = threading.Thread(target=run_loop, daemon=True, name="mqtt-subscriber")
		# thrd.start()
		# return thrd