from utils import MQTTClient
import time, json, asyncio
from utils import MQTT_TOPIC, REDIS_CLIENT
import logging

fh = logging.FileHandler('dataAdderQueue.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger = logging.getLogger(__name__)

class DataAdderQueue(object):
	def __init__(self):
		self.__mqtt_client = MQTTClient(callback=self.recv_data_callback)
		self.__subscriber = REDIS_CLIENT.pubsub()
		self.__subscriber.subscribe("dataAdderPublish")
		self.__crnt_msg = None
		# self.__callbacks = callbacks

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
				# await self.wait_for_mqtt_msg(testing = False, timeout = 30)
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
				print("Publishing: " + data["data"] + " to " + MQTT_TOPIC + " topic")
				self.__mqtt_client.publish(MQTT_TOPIC, data["data"])
				# await self.wait_for_mqtt_msg(testing = False, timeout = 30)
				await asyncio.sleep(2)
			else:
				await asyncio.sleep(0.1)
		# for msg in self.__subscriber.listen():
		# 	if msg is not None and msg["type"] == "message":
		# while True:
		# 	msg = self.__subscriber.get_message()
		# 	if msg is not None:
		# 		self.__crnt_msg = msg
		# 		break
		# 	else:
		# 		time.sleep(0.1)

	async def wait_for_mqtt_msg(self, timeout = 10, testing = True, testing_message = "client_id:simcom_client01|62 F1 90 53 42 4D 31 36 41 45 42 38 4E 57 30 30 30 32 34 35"):
		start_time = time.time()
		while self.__crnt_msg is not None and time.time() - start_time < timeout:
			asyncio.sleep(0.1)
		if testing:
			self.recv_data_callback(testing_message)

	def recv_data_callback(self, message):
	# def recv_data_callback(self, client, userdata, message):
		data = message
		# try:
		# 	data = message.payload.decode("utf-8")
		# except Exception as e:
		# 	data = message
		logger.debug("Received: " + data)
		print("Received: " + data)
		if data is None or not isinstance(data, str):
			return
		if data.startswith("server>"):
			return
		else:
			data = data.lower()
			print("Publishing: " + data + " to dataAdderSubscribe topic")
			crnt_msg = self.__crnt_msg
			REDIS_CLIENT.publish("dataAdderSubscribe", json.dumps({"crnt_msg": crnt_msg, "data": data}))
			self.__crnt_msg = None
			# for callback in self.__callbacks:
			# 	callback(data)


	def configure(self):
		self.__mqtt_client.subscribe(MQTT_TOPIC)

# DATA_ADDER_QUEUE = DataAdderQueue()