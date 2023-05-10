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
import threading, time, os, subprocess, sys
import logging, json

TIMEOUT = 100
logger = logging.getLogger(__name__)

class MQTTClient(object):
	# def __new__(cls, callback = None):
	# 	if not hasattr(cls, 'instance'):
	# 		cls.instance = super(MQTTClient, cls).__new__(cls)
	# 	cls.callback = callback
	# 	return cls.instance

	def __create_new_client(self):
		self.__client = mqtt5_client_builder.mtls_from_path(
			endpoint = MQTT_HOST,
			port = 8883,
			cert_filepath = MQTT_CERTIFICATE,
			pri_key_filepath = MQTT_PRIVATE_KEY,
			ca_filepath = MQTT_ROOT_CA,
			client_id = MQTT_CLIENT_ID,
			clean_session = True,
			# on_publish_received = self.on_publish_callback_fn,
			on_lifecycle_stopped = self.on_lifecycle_stopped,
			on_lifecycle_connection_success = self.on_lifecycle_connection_success,
			on_lifecycle_connection_failure = self.on_lifecycle_connection_failure,
			on_connection_interrupted = self.on_connection_interrupted,
			on_lifecycle_attempting_connect  = self.on_lifecycle_attempting_connect,
			on_lifecycle_disconnection = self.on_lifecycle_disconnection,

		)
		self.__client.start()
		lifecycle_connect_success_data = self.__future_connection_success.result(TIMEOUT)
		connack_packet = lifecycle_connect_success_data.connack_packet
		negotiated_settings = lifecycle_connect_success_data.negotiated_settings
		print(f"Connected to endpoint:'{MQTT_HOST}' with Client ID:'{MQTT_CLIENT_ID}' with reason_code:{repr(connack_packet.reason_code)}")

	def __init__(self, callback = None):
		self.__callback = callback
		self.__future_stopped = Future()
		self.__future_connection_success = Future()
		# self.__topic = None
		self.__create_new_client()

	# def on_publish_callback_fn(self, publish_packet):
	# 	print("Received publish:", publish_packet)
	# 	publish_packet = publish_packet.publish_packet
	# 	assert isinstance(publish_packet, mqtt5.PublishPacket)
	# 	if self.__callback is not None:
	# 		self.__callback(publish_packet)
	# 	if self.__topic:
	# 		self.reset_connection()

	def on_connection_interrupted(self, connection, error, **kwargs):
		print(f"MQTT connection interrupted: {error}")

	def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
		print(f"MQTT connection resumed with return code: {return_code}")

	def on_lifecycle_attempting_connect(self, *args, **kwargs):
		print("Lifecycle Attempting Connect")

	# Callback for the lifecycle event Stopped
	def on_lifecycle_stopped(self, lifecycle_stopped_data: mqtt5.LifecycleStoppedData):
		print("Lifecycle Stopped", lifecycle_stopped_data)
		self.__future_stopped.set_result(lifecycle_stopped_data)

	def on_lifecycle_disconnection(self, lifecycle_disconnected_data):
		print("Lifecycle Disconnected", lifecycle_disconnected_data)
		# self.reset_connection()

	# def reset_connection(self):
	# 	self.__future_stopped = Future()
	# 	self.__client.stop()
	# 	del self.__client
	# 	self.__create_new_client()
	# 	self.subscribe(self.__topic)
	# 	time.sleep(5)

	# Callback for the lifecycle event Connection Success
	def on_lifecycle_connection_success(self, lifecycle_connect_success_data: mqtt5.LifecycleConnectSuccessData):
		print("Lifecycle Connection Success")
		if not self.__future_connection_success.done():
			self.__future_connection_success.set_result(lifecycle_connect_success_data)

	# # Callback for the lifecycle event Connection Failure
	def on_lifecycle_connection_failure(self, lifecycle_connection_failure: mqtt5.LifecycleConnectFailureData):
		print("Lifecycle Connection Failure")
		print("Connection failed with exception:{}".format(lifecycle_connection_failure.exception))

	# @property
	# def client(self):
	# 	return self.__client
	
	# def ackCallback(self, mid, data):
	# 	print("Received ack for message: " + str(mid) + " data: " + str(data))

	def subscribe(self, topic):
		proc_params = [
			"D:\\Projects\\pdsl\\canlytics\\server\\mqtt-cli.exe" if sys.platform == "win32" else "/usr/bin/mqtt",
			"sub",
			"-h",
			MQTT_HOST,
			"-p",
			str(8883),
			"--cafile",
			MQTT_ROOT_CA,
			"--cert",
			MQTT_CERTIFICATE,
			"--key",
			MQTT_PRIVATE_KEY,
			"-d",
			"--jsonOutput",
			"-V",
			str(5),
			"-q",
			str(1),
			"-t",
			topic
		]
		with subprocess.Popen(
			proc_params,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT,
			universal_newlines = True,
			cwd = os.getcwd(),
			shell = True if sys.platform == "win32" else False,
		) as proc:
			start_adding = False
			output = ""
			for line in proc.stdout:
				if line.startswith("{"):
					start_adding = True
				elif line.startswith("}"):
					start_adding = False
					output += line
					data = json.loads(output)
					print(data)
					if self.__callback is not None:
						self.__callback(data)
					# print(data)
					output = ""
				if start_adding:
					output += line
				# if "received PUBLISH" in line:
					# print(line)
			# stdout, stderr = proc.communicate()
			# print(stdout)
			# print(stderr)
		# print(f"Subscribing to topic: {topic}")
		# subscribr_future = self.__client.subscribe(
		# 	subscribe_packet = mqtt5.SubscribePacket(
		# 		subscriptions = [
		# 			mqtt5.Subscription(topic_filter = topic, qos = mqtt5.QoS.AT_LEAST_ONCE, no_local = False)	
		# 		]
		# 	)
		# )
		# self.__topic = topic
		# subscribr_future.result()

	# @staticmethod
	def publish(self, topic, message) -> bool:
		# print(f"Publishing to topic: {topic} message: {message}")
		# proc_params = [
		# 	"D:\\Projects\\pdsl\\canlytics\\server\\mqtt-cli.exe" if sys.platform == "win32" else "/usr/bin/mqtt",
		# 	"pub",
		# 	"-h",
		# 	MQTT_HOST,
		# 	"-p",
		# 	str(8883),
		# 	"--cafile",
		# 	MQTT_ROOT_CA,
		# 	"--cert",
		# 	MQTT_CERTIFICATE,
		# 	"--key",
		# 	MQTT_PRIVATE_KEY,
		# 	"-d",
		# 	"-V",
		# 	str(5),
		# 	"-q",
		# 	str(1),
		# 	"-t",
		# 	topic,
		# 	"-m",
		# 	f"{message}"
		# ]
		# proc = subprocess.Popen(
		# 	proc_params,
		# 	stdout = subprocess.PIPE,
		# 	stderr = subprocess.PIPE,
		# 	universal_newlines = True,
		# 	cwd = os.getcwd(),
		# 	shell = True if sys.platform == "win32" else False,
		# )
		# stdout, stderr = proc.communicate()
		# print(stdout)
		# print(stderr)

		pubs = self.__client.publish(
			publish_packet = mqtt5.PublishPacket(
				topic = topic,
				payload = message,
				qos = mqtt5.QoS.AT_LEAST_ONCE
			)
		)
		pubs.result()


	# def unsubscribe(self, topic):
	# 	self.__client.unsubscribe(topic)

	# def disconnect(self):
	# 	self.__client.stop()