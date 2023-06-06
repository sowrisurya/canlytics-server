from utils import MQTTClientV2
import asyncio, time, threading, redis
from .snapshotConsts import (
	HEX_MAP,
	READ_PARAMS,
	DTC_CODES,
	FAULT_TYPES,
	NRC_CODES
)
from .statusGetter import StatusGetter

class SnapShotSubscriber:
	def __init__(self, device_id):
		self.__mqtt_client = MQTTClientV2(callback = self.msg_callback)
		self.__thrd = threading.Thread(target = self.__mqtt_client.wait, daemon=True)
		self.__redis_client = redis.Redis()
		self.__thrd.start()
		self.__crnt_msg = None
		self.__device_id = device_id
		self.__resp_msg = []

	def msg_callback(self, msg):
		msg = msg.lower()
		if not msg.startswith("client_id:"):
			return
		msg = msg.split(":")[1].strip()
		device_id, raw_data = msg.split("|")
		if device_id != self.__device_id:
			return
		hex_msg = raw_data.split(" ")
		for i in range(len(hex_msg)):
			if len(hex_msg[i]) == 1:
				hex_msg[i] = "0" + hex_msg[i]
		self.__resp_msg.append("".join(hex_msg).upper())

	def get_msg(self):
		return self.__crnt_msg

	async def wait(self, timeout = 5, tot_msgs = 1):
		st = time.time()
		while len(self.__resp_msg) < tot_msgs and (time.time() - st < timeout):
			await asyncio.sleep(1)
		crnt_msg = self.__crnt_msg
		self.__crnt_msg = None
		return crnt_msg

	async def publish(self, msg, resp_msgs = 1):
		with self.__redis_client.lock(f"publish_msg_{self.__device_id}", sleep = 0.01):
			self.__mqtt_client.publish(msg)
			self.__crnt_msg = msg
			crnt_msg = await self.wait(tot_msgs = resp_msgs)
		return crnt_msg

	async def read_odo_reading(self):
		crnt_msg = await self.publish(f"server>{self.__device_id} 716 22 DD 01<")
		odo_reading = self.__resp_msg[0]
		self.__resp_msg = []
		if odo_reading is None:
			return None
		if len(odo_reading) < 6:
			return None
		odo_reading = odo_reading[6:]
		try:
			odo_reading = int(odo_reading, 16)
			return odo_reading
		except ValueError:
			return None

	def parse_dtc_msg(self, dtc_msg):
		all_msgs = []
		dtc_msg = dtc_msg[6:]
		for i in range(0, len(dtc_msg), 8):
			if len(dtc_msg[i:]) < 8:
				continue
			msg = dtc_msg[i:i+8]
			hex_code = msg[0:4]
			dtc_code = msg[0:6]
			dtc_code = HEX_MAP[msg[0]] + msg[1:6]
			dtc_status = msg[6:8]

			fetch_dtc_code = dtc_code[0:5]
			fetch_fault_code = dtc_code[5:7]
			description = f"{DTC_CODES.get(fetch_dtc_code, None)} - {FAULT_TYPES.get(fetch_fault_code, None)}"
			all_msgs.append({
				"hex": hex_code, 
				"code": dtc_code, 
				"status": dtc_status, 
				"description": description
			})
		return all_msgs		

	def parse_dtc_msgs(self, dtc_msgs):
		all_msgs = []
		for msg in dtc_msgs:
			if len(msg) < 6:
				continue
			all_msgs.extend(self.parse_dtc_msg(msg))
		return all_msgs

	async def read_dtc_info(self, dids):
		did_dtcs = []
		for dtc_did in dids:
			crnt_msg = await self.publish(f"server>{self.__device_id} {dtc_did.frame_id} 19 02 AF<", resp_msgs = 2)
			dtc_info = self.__resp_msg
			self.__resp_msg = []
			if len(dtc_info) == 0:
				return None
			did_dtcs.append({
				"ecu_name": dtc_did.name,
				"did": dtc_did.frame_id,
				"messages": self.parse_dtc_msgs(dtc_info)
			})
		return did_dtcs
	
	def decode_message(self, read_data, msg, type = 0):
		if msg[:2] != "62":
			return None
		msg = msg[len(read_data):]
		if len(msg) == 0:
			return None
		if type == 0:
			try:
				decoded_data = bytes.fromhex(msg).decode()
				decoded_data = decoded_data.replace("\x00", "")
				decoded_data = decoded_data.replace("\\x", "")
				return decoded_data
			except Exception as e:
				print(e)
				return "Decode Error"
		elif type == 3:
			return "Data Not Processed"

	async def read_ecu_dids(self, dids):
		logs_messages = []
		for ecu_did in dids:
			for param in READ_PARAMS:
				raad_param = param['read'].replace(" ", "")
				crnt_msg = await self.publish(f"server>{self.__device_id} {ecu_did.frame_id} {param['read']}<")
				if len(self.__resp_msg) == 0:
					continue
				msgs = self.__resp_msg
				self.__resp_msg = []
				if len(msgs) == 0:
					continue
				dec_msg = msgs[0]
				decoded_data = self.decode_message(raad_param, dec_msg)
				success = True
				if decoded_data is None:
					decoded_data = "Negative Response"
					success = False
				logs_messages.append({
					"raw_data": StatusGetter.add_spaces_hex(dec_msg),
					"success": str(success),
					"check": dec_msg[2:len(raad_param)] if len(dec_msg) >= len(raad_param) else "",
					"input_data": StatusGetter.add_spaces_hex(param["read"]),
					# "did": json_message.get("did"),
					"decoded_data": decoded_data,
					"diag_name": ecu_did.name,
					"parameter_name": param["param"],
					"frame_id": ecu_did.frame_id,
					"received_data": StatusGetter.add_spaces_hex(dec_msg),
				})
		return logs_messages

	async def take_snapshot(self, dids):
		dtc_data = await self.read_dtc_info(dids)
		logs = await self.read_ecu_dids(dids)
		odo_read = await self.read_odo_reading()
		return logs, dtc_data, odo_read

	def stop(self):
		try:
			self.__mqtt_client.stop()
			self.__thrd.join()
		except Exception as e:
			print(e)