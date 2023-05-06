from utils.influxClient import InfluxClient
from typing import Callable
from utils.mqttClient import MQTTClient
from utils.consts import MQTT_TOPIC
import json, datetime, asyncio, time
import logging

logger = logging.getLogger(__name__)

class DataController:
	def __init__(self, frame_id: int, inpt_data_hex: str, diag_name: str = "", max_clients: int = 1, callback : Callable = None) -> None:
		if len(inpt_data_hex) % 2 != 0:
			raise Exception("Invalid input data")
		if max_clients < 1:
			raise Exception("Invalid max clients")
		if inpt_data_hex.startswith("0x"):
			inpt_data_hex = inpt_data_hex[2:]
		try:
			int(inpt_data_hex, 16)
		except:
			raise Exception("Invalid input data")
		self.__mqtt_client = MQTTClient()
		self.__influx_client = InfluxClient()
		self.__inpt_data = inpt_data_hex.lower()
		self.__max_clients = max_clients
		self.__callback = callback
		self.__frame_id = frame_id
		self.__diag_name = diag_name

	def configure(self):
		self.__mqtt_client.subscribe(MQTT_TOPIC, self.__vehicle_diagnostic_callback)

	def __vehicle_diagnostic_callback(self, client, userdata, message):
		data : str = message.payload.decode("utf-8").lower()
		if data.startswith("server>") and not data.startswith("client_id:") and "|" not in data:
			return
		logger.info(f"Received data: {data}")
		device_id, hex_data = data.split("|")
		device_id = device_id.lstrip("client_id:")
		hex_data = hex_data.replace(" ", "")
		success_message = hex_data[:2] == "62"
		if success_message and hex_data[2:].startswith(self.__inpt_data[2:]):
			self.__max_clients -= 1

		check_msg = hex_data[2:len(self.__inpt_data)]
		raw_data = hex_data[len(self.__inpt_data):]
		if len(raw_data) % 2 != 0:
			raw_data = raw_data[:-1]
		decoded_data = bytes.fromhex(raw_data).decode()
		decoded_data = decoded_data.replace("\x00", "")
		log_msg = f"Device ID: {device_id}, Success: {success_message}, Check: {check_msg}, Data: {raw_data}, Decoded: {decoded_data}"
		logger.info(log_msg)
		try:
			self.__influx_client.write(
				measurement = device_id, 
				tags = {},
				fields = {
					"raw_data": raw_data,
					"success": str(success_message),
					"check": check_msg,
					"input_data": self.__inpt_data,
					# "did": json_message.get("did"),
					"decoded_data": decoded_data,
					"diag_name": self.__diag_name,
					"frame_id": str(self.__frame_id),
				}
			)
		except Exception as e:
			logger.error(f"Error: {e}")
		if self.__callback:
			self.__callback(
				device_id = device_id, 
				raw_data = raw_data, 
				input_data =  self.__inpt_data,
				decoded_data = decoded_data, 
				success = success_message,
				diag_name = self.__diag_name,
				frame_id = self.__frame_id,
			)

	async def wait_for_data_async(self, timeout = 10):
		while self.__max_clients > 0 and timeout > 0:
			await asyncio.sleep(1) 
			timeout -= 1

	def wait_for_data(self, timeout = 10):
		while self.__max_clients > 0 and timeout > 0:
			time.sleep(1)
			timeout -= 1

	def publish(self):
		frame_id_hex = hex(self.__frame_id)[2:]
		data_hex = self.__inpt_data.ljust(16, '0')
		data_hex = " ".join(data_hex[i:i+2] for i in range(0, len(data_hex), 2))
		pub_message = "SERVER>{} {}<".format(frame_id_hex, data_hex)
		logger.info(f"Publishing: {pub_message}")
		self.__mqtt_client.publish(MQTT_TOPIC, pub_message)

	def kill(self):
		self.__mqtt_client.unsubscribe(MQTT_TOPIC)
		self.__mqtt_client.disconnect()