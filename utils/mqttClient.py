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
			# client_options = mqtt5.ClientOptions(
			# 	host_name = host,
			# 	session_behavior=mqtt5.ClientSessionBehaviorType.REJOIN_ALWAYS,
			# 	connack_timeout_ms = 5000,
			# ),
			endpoint = host,
			port = port,
			cert_filepath = certificatePath,
			pri_key_filepath = privateKeyPath,
			ca_filepath = rootCAPath,
			client_id = client_id,
			# on_connection_interrupted = self.on_connection_interrupted,
			# on_connection_resumed = self.on_connection_resumed,
			# clean_session = False,
			on_publish_received = self.on_publish_callback_fn,
			on_lifecycle_stopped = self.on_lifecycle_stopped,
			on_lifecycle_connection_success = self.on_lifecycle_connection_success,
			on_lifecycle_connection_failure = self.on_lifecycle_connection_failure,
			# keep_alive_interval_sec = 5,
		)
		self.__callback = callback
		self.__future_stopped = Future()
		self.__future_connection_success = Future()

		# self.__recevd_all_event = threading.Event()

		self.__client.start()
		lifecycle_connect_success_data = self.__future_connection_success.result(TIMEOUT)
		connack_packet = lifecycle_connect_success_data.connack_packet
		negotiated_settings = lifecycle_connect_success_data.negotiated_settings
		print(f"Connected to endpoint:'{host}' with Client ID:'{client_id}' with reason_code:{repr(connack_packet.reason_code)}")

		# self.__client.connect()

		# self.__client = AWSIoTMQTTClient(client_id)
		# self.__client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
		# self.__client.configureEndpoint(host, port)

		# self.__client.configureAutoReconnectBackoffTime(1, 32, 10)
		# self.__client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
		# self.__client.configureDrainingFrequency(2)  # Draining: 2 Hz
		# self.__client.configureConnectDisconnectTimeout(10)  # 10 sec
		# self.__client.configureMQTTOperationTimeout(60)  # 5 sec

		# self.__client.connect()

	def on_publish_callback_fn(self, publish_packet):
		print("received publish packet:")
		# self.__recevd_all_event.set()
		publish_packet = publish_packet.publish_packet
		assert isinstance(publish_packet, mqtt5.PublishPacket)
		if self.__callback is not None:
			self.__callback(publish_packet.payload.decode())
		# print("Publish callback: " + str(publish_packet.topic) + " " + str(publish_packet.payload))
		# print("Publish callback: " + str(payload))
		# print("Publish callback: " + str(data))

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
		# self.__client.start()
		self.__future_connection_success.set_result(lifecycle_connect_success_data)


	# Callback for the lifecycle event Connection Failure
	def on_lifecycle_connection_failure(self, lifecycle_connection_failure: mqtt5.LifecycleConnectFailureData):
		print("Lifecycle Connection Failure")
		print("Connection failed with exception:{}".format(lifecycle_connection_failure.exception))

	@property
	def client(self):
		return self.__client
	
	def ackCallback(self, mid, data):
		print("Received ack for message: " + str(mid) + " data: " + str(data))

	# def subscribe(self, topic, callback, async_subscribe = False):
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
		# if async_subscribe:
		# 	self.__client.subscribeAsync(topic, QoS = 1, ackCallback = self.ackCallback, messageCallback = callback)
		# else:
		# 	self.__client.subscribe(topic, QoS = 1, callback = callback)

	def publish(self, topic, message) -> bool:
		pubs = self.__client.publish(
			# topic = topic,
			# payload = message,
			# qos = mqtt.QoS.EXACTLY_ONCE
			publish_packet = mqtt5.PublishPacket(
				topic = topic,
				payload = message,
				qos = mqtt5.QoS.AT_LEAST_ONCE
			)
		)
		pubs.result()
		# time.sleep(1)
		# logger.info(f"Publishing message: {message} to topic: {topic}")
		# return self.__client.publish(topic, message, 1)

	def unsubscribe(self, topic):
		self.__client.unsubscribe(topic)

	# def wait(self):
	# 	self.__recevd_all_event.wait()

	def disconnect(self):
		self.__client.stop()