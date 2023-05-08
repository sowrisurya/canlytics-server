# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from awsiot import mqtt_connection_builder, mqtt5_client_builder
from awscrt import mqtt, mqtt5
from concurrent.futures import Future
from utils.consts import (
	MQTT_CLIENT_ID,
	MQTT_HOST,
	MQTT_ROOT_CA,
	MQTT_PRIVATE_KEY,
	MQTT_CERTIFICATE
)
import threading, time
import logging

TIMEOUT = 100
logger = logging.getLogger(__name__)

class MQTTClient(object):
	def __new__(cls, callback = None):
		if not hasattr(cls, 'instance'):
			cls.instance = super(MQTTClient, cls).__new__(cls)
		cls.callback = callback
		return cls.instance

	def __init__(self, client_id = MQTT_CLIENT_ID, host = MQTT_HOST, rootCAPath = MQTT_ROOT_CA, privateKeyPath = MQTT_PRIVATE_KEY, certificatePath = MQTT_CERTIFICATE, port = 8883, callback = None):
		self.__client = mqtt5_client_builder.mtls_from_path(
			endpoint = host,
			port = port,
			cert_filepath = certificatePath,
			pri_key_filepath = privateKeyPath,
			ca_filepath = rootCAPath,
			client_id = client_id,
			on_publish_received = self.on_publish_callback_fn,
			on_lifecycle_stopped = self.on_lifecycle_stopped,
			on_lifecycle_connection_success = self.on_lifecycle_connection_success,
			on_lifecycle_connection_failure = self.on_lifecycle_connection_failure,
		)
		self.__callback = callback
		self.__future_stopped = Future()
		self.__future_connection_success = Future()

		self.__client.start()
		lifecycle_connect_success_data = self.__future_connection_success.result(TIMEOUT)
		connack_packet = lifecycle_connect_success_data.connack_packet
		negotiated_settings = lifecycle_connect_success_data.negotiated_settings
		print(f"Connected to endpoint:'{host}' with Client ID:'{client_id}' with reason_code:{repr(connack_packet.reason_code)}")

	def on_publish_callback_fn(self, publish_packet):
		publish_packet = publish_packet.publish_packet
		assert isinstance(publish_packet, mqtt5.PublishPacket)
		if self.__callback is not None:
			self.__callback(publish_packet)

	def on_connection_interrupted(self, connection, error, **kwargs):
		print(f"MQTT connection interrupted: {error}")

	def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
		print(f"MQTT connection resumed with return code: {return_code}")

	# Callback for the lifecycle event Stopped
	def on_lifecycle_stopped(self, lifecycle_stopped_data: mqtt5.LifecycleStoppedData):
		print("Lifecycle Stopped", lifecycle_stopped_data)
		self.__future_stopped.set_result(lifecycle_stopped_data)


	# Callback for the lifecycle event Connection Success
	def on_lifecycle_connection_success(self, lifecycle_connect_success_data: mqtt5.LifecycleConnectSuccessData):
		print("Lifecycle Connection Success")
		if not self.__future_connection_success.done():
			self.__future_connection_success.set_result(lifecycle_connect_success_data)
		else:
			print("Connection success already received")

	# Callback for the lifecycle event Connection Failure
	def on_lifecycle_connection_failure(self, lifecycle_connection_failure: mqtt5.LifecycleConnectFailureData):
		print("Lifecycle Connection Failure")
		print("Connection failed with exception:{}".format(lifecycle_connection_failure.exception))

	@property
	def client(self):
		return self.__client
	
	def ackCallback(self, mid, data):
		print("Received ack for message: " + str(mid) + " data: " + str(data))

	def subscribe(self, topic):
		print(f"Subscribing to topic: {topic}")
		subscribr_future = self.__client.subscribe(
			subscribe_packet = mqtt5.SubscribePacket(
				subscriptions = [
					mqtt5.Subscription(topic_filter = topic, qos = mqtt5.QoS.AT_LEAST_ONCE, no_local = False)	
				]
			)
		)
		subscribr_future.result()

	def publish(self, topic, message) -> bool:
		pubs = self.__client.publish(
			publish_packet = mqtt5.PublishPacket(
				topic = topic,
				payload = message,
				qos = mqtt5.QoS.AT_LEAST_ONCE
			)
		)
		pubs.result()

	def unsubscribe(self, topic):
		self.__client.unsubscribe(topic)

	def disconnect(self):
		self.__client.stop()