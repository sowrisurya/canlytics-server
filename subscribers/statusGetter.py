from utils import INFLUX_CLIENT, REDIS_CLIENT
from typing import Callable
from utils.mqttClient import MQTTClient
from utils.consts import MQTT_TOPIC
from models import VehicleDBCDids
import json, datetime, asyncio, time
import logging

logger = logging.getLogger(__name__)

class StatusGetter:
	# def __init__(self, max_clients = 1):
	# 	# self.__mqtt_client = MQTTClient()	
	# 	self.__running = False
	# 	self.__messages_received = True
	# 	self.__max_clients = max_clients
	# 	self.__crnt_clients = max_clients

	@staticmethod
	def publish_message(data: dict):
		REDIS_CLIENT.publish("dataAdderPublish", json.dumps(data))

	@staticmethod
	def handle_status_message(device_id, status):
		vehicle_status = VehicleDBCDids.objects(device_id = device_id).first()
		if vehicle_status is None:
			return
		vehicle_status.current_status = status
		logger.info(f"Device ID: {device_id}, Status: {status}")

	@staticmethod
	def handle_gps_message(deivce_id, gps_msg):
		logger.info(f"Device ID: {deivce_id}, GPS: {gps_msg}")

	@staticmethod
	def diagonostic_callback(crnt_msg: dict, data: str, add_to_influx: bool = True):
		if not data.startswith("client_id:") and "|" not in data:
			return
		device_id, hex_data = data.split("|")
		device_id = device_id.lstrip("client_id:")
		hex_data = hex_data.replace(" ", "")

		### Start Prototype ###
		# if success_message and hex_data[2:].startswith(self.__inpt_data[2:]):
		# 	self.__max_clients -= 1

		# success_message = hex_data[:2] == "62"
		# inpt_data = "22F190"
		# frame_id = "1971"
		# diag_name = "DiagName"
		success_message = hex_data[:2] == "62"
		logger.info(crnt_msg)
		inpt_data = crnt_msg["input_data"]
		frame_id = str(crnt_msg["frame_id"])
		diag_name = crnt_msg["diag_name"]

		### End Prototype ###


		check_msg = hex_data[2:len(inpt_data)]
		raw_data = hex_data[len(inpt_data):]
		if len(raw_data) % 2 != 0:
			raw_data = raw_data[:-1]
		decoded_data = bytes.fromhex(raw_data).decode()
		decoded_data = decoded_data.replace("\x00", "")
		logger.info("Device ID: ", device_id, end=", ")
		logger.info("Success: ", success_message, end=", ")
		logger.info("Check: ", check_msg, end=", ")
		logger.info("Data: ", raw_data, end=", ")
		logger.info("Decoded: ", decoded_data, end=" ")
		logger.info("--------------\n\n")
		
		log_data = {
			"raw_data": raw_data,
			"success": str(success_message),
			"check": check_msg,
			"input_data": inpt_data,
			# "did": json_message.get("did"),
			"decoded_data": decoded_data,
			"diag_name": diag_name,
			"frame_id": frame_id,
		}
		try:
			if add_to_influx:
				INFLUX_CLIENT.write(
					measurement = device_id, 
					tags = {},
					fields = log_data
				)
		except Exception as e:
			logger.error(f"Error: {e}")
		finally:
			log_data["device_id"] = device_id
			return log_data
		# if self.__callback:
		# 	self.__callback(
		# 		device_id = device_id, 
		# 		raw_data = raw_data, 
		# 		input_data =  self.__inpt_data,
		# 		decoded_data = decoded_data, 
		# 		success = success_message,
		# 		diag_name = self.__diag_name,
		# 		frame_id = self.__frame_id,
		# 	)

	@staticmethod
	def status_diagonostic_callback(client, userdata, message):
		data : str = message.payload.decode("utf-8").lower()
		logger.info(f"Received data: {data}")
		if data.startswith("server>") or "|" not in data:
			return	
		if data.startswith("client_id:"):
			return
		# logger.info(f"Current clients: {self.__crnt_clients}")
		if data.startswith("gps-client_id"):
			device_id, gps_msg = data.split("|")
			device_id = device_id.lstrip("gps-client_id:")
			StatusGetter.handle_gps_message(device_id, gps_msg)
		elif data.startswith("status-client_id"):
			device_id, status = data.split("|")
			device_id = device_id.lstrip("status-client_id:")
			status = status.lstrip("vehicle is ")
			StatusGetter.handle_status_message(device_id, status)
		# if self.__crnt_clients == 0:
		# 	self.__messages_received = True
		# 	self.__crnt_clients = self.__max_clients

	# def configure(self):
	# 	self.__mqtt_client.subscribe(MQTT_TOPIC, self.__vehicle_diagnostic_callback)
	# 	self.__running = True

	# async def wait_for_messages_received(self):
	# 	logger.info("Waiting for messages to be received")
	# 	while not self.__messages_received:
	# 		await asyncio.sleep(1)
	# 	logger.info("Messages received")

	# async def publish_gps(self):
	# 	await self.wait_for_messages_received()
	# 	self.__mqtt_client.publish(MQTT_TOPIC, f"server>Fetch GPS<")
	# 	self.__messages_received = False
	
	@staticmethod
	def publish_gps():
		StatusGetter.publish_message({"data": f"server>Fetch GPS<"})

	@staticmethod
	def publish_vehicle_status():
		StatusGetter.publish_message({"data": f"server>vehicle status<"})
		# self.__messages_received = False

	@staticmethod
	def publish(diag_name: str, frame_id: int, inpt_data_hex: str):
		frame_id_hex = hex(frame_id)[2:]
		if len(inpt_data_hex) % 2 != 0:
			raise Exception("Invalid input data")
		if inpt_data_hex.startswith("0x"):
			inpt_data_hex = inpt_data_hex[2:]
		try:
			int(inpt_data_hex, 16)
		except:
			raise Exception("Invalid input data")
		data_hex = inpt_data_hex.ljust(16, '0')
		data_hex = " ".join(data_hex[i:i+2] for i in range(0, len(data_hex), 2))
		pub_message = "server>{} {}<".format(frame_id_hex, data_hex)
		StatusGetter.publish_message({
			"diag_name": diag_name,
			"frame_id": frame_id,
			"input_data": inpt_data_hex,
			"data": pub_message
		})

	# async def publish_vehicle_status(self):
	# 	await self.wait_for_messages_received()
	# 	self.__mqtt_client.publish(MQTT_TOPIC, f"server>vehicle status<")
	# 	self.__messages_received = False

	# async def wait(self):
	# 	while self.__running:
	# 		await asyncio.sleep(1)