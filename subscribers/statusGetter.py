from utils import INFLUX_CLIENT, REDIS_CLIENT
from typing import Callable
from utils.mqttClient import MQTTClient
from utils.consts import MQTT_TOPIC
from models import VehicleDBCDids, GPSCoord
import json, datetime, asyncio, time
from utils import Logger

logger = Logger(__name__)

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
		try:
			vehicle_status = VehicleDBCDids.objects(device_id = device_id).first()
			if vehicle_status is None:
				return
			vehicle_status.current_status = status
			vehicle_status.save()
			# print(f"Device ID: {device_id}, Status: {status}")
		except Exception as e:
			print(e)
		# logger.info(f"Device ID: {device_id}, Status: {status}")

	@staticmethod
	def handle_gps_message(device_id, gps_msg):
		try:

			lat, long = [ float(_.split(":")[1]) for _ in gps_msg.split(",")]
			vehicle_status = VehicleDBCDids.objects(device_id = device_id).first()
			if vehicle_status is None:
				return
			vehicle_status.gps = GPSCoord(
				lat = lat,
				lng = long,
				requested_at = datetime.datetime.now()
			)
			vehicle_status.save()
		except Exception as e:
			print(e)
			return
		# logger.info(f"Device ID: {device_id}, GPS: {gps_msg}")

	@staticmethod
	def diagonostic_callback(crnt_msg: dict, data: str, add_to_influx: bool = True, data_type: int = 0):
		if not data.startswith("client_id:") and "|" not in data:
			return None, None
		device_id, hex_data = data.split("|")
		device_id = device_id.lstrip("client_id:")

		hex_data = "".join([ _ if len(_) == 2 else f"0{_[0]}" for _ in hex_data.split(" ")])
		# while " 0 " in hex_data:
		# 	hex_data = hex_data.replace(" 0 ", " 00 ")
		# if hex_data.endswith(" 0"):
		# 	hex_data = hex_data[:-2] + " 00"
		### Start Prototype ###
		# if success_message and hex_data[2:].startswith(self.__inpt_data[2:]):
		# 	self.__max_clients -= 1

		# success_message = hex_data[:2] == "62"
		# inpt_data = "22F190"
		# frame_id = "1971"
		# diag_name = "DiagName"

		inpt_data = crnt_msg["input_data"]
		frame_id = str(crnt_msg["frame_id"])
		diag_name = crnt_msg["diag_name"]
		parameter_name = crnt_msg.get("parameter_name", "")

		success_message = hex_data[:2] == "62"
		if not success_message:
			log_data = {
				"raw_data": hex_data,
				"success": str(success_message),
				"check": None,
				"input_data": inpt_data,
				# "did": json_message.get("did"),
				"decoded_data": "NO DATA",
				"diag_name": diag_name,
				"parameter_name": parameter_name,
				"frame_id": frame_id,
			}
			return device_id, log_data

		### End Prototype ###
		strip_len = len(inpt_data.replace(" ", ""))
		check_msg = hex_data[2:strip_len]
		raw_data = hex_data[strip_len:]
		if len(raw_data) % 2 != 0:
			raw_data = raw_data[:-1]
		decoded_data = None
		try:
			if data_type == 0:
				decoded_data = bytes.fromhex(raw_data).decode()
				decoded_data = decoded_data.replace("\x00", "")
			elif data_type == 1:
				decoded_data = int(raw_data, 16)
			elif data_type == 3:
				decoded_data = raw_data
		except Exception as e:
			logger.error(f"Error: {e}")
			# return device_id, None
		# elif data_type == "time":
		# 	decoded_data

		logger.info(f"Device ID: {device_id}")
		logger.info(f"Success: {success_message}")
		logger.info(f"Check: {check_msg}")
		logger.info(f"Data: {raw_data}")
		logger.info(f"Decoded: {decoded_data}")
		logger.info("--------------\n\n")
		
		log_data = {
			"raw_data": raw_data,
			"success": str(success_message),
			"check": check_msg,
			"input_data": inpt_data,
			# "did": json_message.get("did"),
			"decoded_data": decoded_data,
			"diag_name": diag_name,
			"parameter_name": parameter_name,
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
			return device_id, log_data
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
	def status_diagonostic_callback(data):
		print(f"Received data: {data}")
		if data.startswith("server>") or "|" not in data:
			return	
		if data.startswith("client_id:"):
			return
		# logger.info(f"Current clients: {self.__crnt_clients}")
		if data.startswith("gps-client_id"):
			device_id, gps_msg = data.split("|")
			device_id = device_id.replace("gps-client_id:", "")
			print(f"Device ID: {device_id}, GPS: {gps_msg}")
			StatusGetter.handle_gps_message(device_id, gps_msg)
		elif data.startswith("status-client_id"):
			device_id, status = data.split("|")
			device_id = device_id.replace("status-client_id:", "")
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
	def publish(diag_name: str, frame_id: str, inpt_data_hex: str):
		if len(inpt_data_hex) % 2 != 0:
			raise Exception("Invalid input data")
		if inpt_data_hex.startswith("0x"):
			inpt_data_hex = inpt_data_hex[2:]
		data_hex = inpt_data_hex.ljust(16, '0').replace(" ", "")
		data_hex = " ".join(data_hex[i:i+2] for i in range(0, len(data_hex), 2))
		pub_message = "server>{} {}<".format(frame_id, data_hex)
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