from concurrent.futures import Future
from utils.consts import (
	MQTT_CLIENT_ID,
	MQTT_HOST,
	MQTT_ROOT_CA,
	MQTT_PRIVATE_KEY,
	MQTT_CERTIFICATE,
	MQTT_TOPIC,
)
import time
import paho.mqtt.client as mqtt
from utils.logger import Logger

logger = Logger(__name__)

class MQTTClientV2(object):
	def __init__(self, callback = None):
		self.__callback = callback
		self.__create_new_client()
		self.__subscribed = False

	def __create_new_client(self):
		def on_disconnect(*args, **kwargs):
			print("Disconnected with result code ", args, kwargs)

		def on_connect(mqttc, userdata, flags, rc, properties=None):
			# print("connected to endpoint %s with result code %s", MQTT_HOST, rc)
			# print("userdata: %s, flags: %s properties: %s", userdata, flags, properties)
			self.__client.is_connected = True
			self.__client.subscribe(MQTT_TOPIC, qos = 1, options = None, properties = None)
			# print("Subscribed to topic: ", MQTT_TOPIC)
			# time.sleep(1)
			self.__subscribed = True

		def on_message(client, userdata, msg):
			# print("Message received ", msg.payload.decode("utf-8"))
			if self.__callback:
				self.__callback(msg.payload.decode("utf-8"))

		self.__client = mqtt.Client(protocol=mqtt.MQTTv5)
		self.__client.tls_set(ca_certs = MQTT_ROOT_CA, certfile = MQTT_CERTIFICATE, keyfile = MQTT_PRIVATE_KEY, tls_version=2)
		self.__client.on_connect = on_connect
		self.__client.on_disconnect = on_disconnect
		self.__client.on_message = on_message
		self.__client.connect(MQTT_HOST, 8883, 60)
		self.__client.subscribe(MQTT_TOPIC)
		while self.__client.is_connected == False:
			time.sleep(0.1)
		time.sleep(1)

	def publish(self, payload: str, topic = MQTT_TOPIC):
		while not self.__subscribed:
			time.sleep(0.1)
		msg_info = self.__client.publish(topic, payload, qos = 1)
		msg_info.wait_for_publish()

	def wait(self):
		self.__client.loop_forever()
		# task = asyncio.create_task()
		# await task

	def stop(self):
		self.__client.disconnect()
		self.__client.loop_stop()
