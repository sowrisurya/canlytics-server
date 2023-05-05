from utils.influxClient import InfluxClient
from typing import Callable
from utils.mqttClient import MQTTClient
from utils.consts import MQTT_TOPIC
from models import VehicleDBCDids
import json, datetime, asyncio, time

class StatusGetter:
	def __init__(self):
		self.__mqtt_client = MQTTClient()
		self.__running = False

	def __vehicle_diagnostic_callback(self, client, userdata, message):
		data : str = message.payload.decode("utf-8").lower()
		if data.startswith("server>") and not data.startswith("client_id:") and "|" not in data:
			return
		print(f"Received data: {data}")

	def configure(self):
		self.__mqtt_client.subscribe(MQTT_TOPIC, self.__vehicle_diagnostic_callback)
		self.__running = True

	def publish_gps(self):
		self.__mqtt_client.publish(MQTT_TOPIC, f"server>Fetch GPS<")

	def wait(self):
		while self.__running:
			time.sleep(1)