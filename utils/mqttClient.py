from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from utils.consts import (
	MQTT_CLIENT_ID,
	MQTT_HOST,
	MQTT_ROOT_CA,
	MQTT_PRIVATE_KEY,
	MQTT_CERTIFICATE
)
import logging

logger = logging.getLogger(__name__)

class MQTTClient(object):
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(MQTTClient, cls).__new__(cls)
		return cls.instance

	def __init__(self, client_id = MQTT_CLIENT_ID, host = MQTT_HOST, rootCAPath = MQTT_ROOT_CA, privateKeyPath = MQTT_PRIVATE_KEY, certificatePath = MQTT_CERTIFICATE, port = 8883):
		self.__client = AWSIoTMQTTClient(client_id)
		self.__client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
		self.__client.configureEndpoint(host, port)

		self.__client.configureAutoReconnectBackoffTime(1, 32, 10)
		self.__client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
		self.__client.configureDrainingFrequency(2)  # Draining: 2 Hz
		self.__client.configureConnectDisconnectTimeout(10)  # 10 sec
		self.__client.configureMQTTOperationTimeout(60)  # 5 sec

		self.__client.connect()

	@property
	def client(self):
		return self.__client
	
	def ackCallback(self, mid, data):
		print("Received ack for message: " + str(mid) + " data: " + str(data))
	
	def subscribe(self, topic, callback, async_subscribe = False):
		if async_subscribe:
			self.__client.subscribeAsync(topic, QoS = 1, ackCallback = self.ackCallback, messageCallback = callback)
		else:
			self.__client.subscribe(topic, QoS = 1, callback = callback)

	def publish(self, topic, message) -> bool:
		logger.info(f"Publishing message: {message} to topic: {topic}")
		return self.__client.publish(topic, message, 1)

	def unsubscribe(self, topic):
		self.__client.unsubscribe(topic)

	def disconnect(self):
		self.__client.disconnect()