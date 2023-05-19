from models import Vehicle
from utils import MQTTClientV2, REDIS_CLIENT
from subscribers.statusGetter import StatusGetter
import threading, datetime, time, asyncio

class VehicleLogsSubscriber:
	def __init__(self, vehicle_ids, dids_list, timeout = 100, add_to_influx = True, callback = None):
		self.__device_ids = {
			vehicle.chipId: vehicle
			for vehicle in Vehicle.objects(vin__in = vehicle_ids) 
		}
		self.__dids_list = dids_list
		self.__timeout = timeout
		self.__mqtt_client = MQTTClientV2(self.callback if not callback else callback)
		self.set_crnt_msg()
		self.__msgs_recieved = 0
		self.__logs = []
		self.__add_to_influx = add_to_influx
		self.__thrd = threading.Thread(target = self.__mqtt_client.wait, daemon=True)
		self.__thrd.start()

	def callback(self, message: str):
		message = message.lower()
		if message.startswith("server:"):
			return
		with REDIS_CLIENT.lock("vehicle_logs_lock", sleep = 0.01):
			if not self.crnt_msg:
				return
			device_id, log_data = StatusGetter.diagonostic_callback(crnt_msg=self.crnt_msg, data=message, add_to_influx = self.__add_to_influx)

			if device_id not in self.__device_ids:
				return

			self.__msgs_recieved += 1

			if self.__msgs_recieved == len(self.__device_ids):
				self.set_crnt_msg()
				self.__msgs_recieved = 0

			if log_data is not None:
				log_data["time"] = datetime.datetime.utcnow()
				log_data["device_id"] = device_id
				log_data["vin"] = self.__device_ids[device_id].vin
				self.__logs.append(log_data)

	async def wait_for_msgs_recvd(self):
		st = time.time()
		while self.crnt_msg is not None and time.time() - st < self.__timeout:
			await asyncio.sleep(0.1)

	def set_crnt_msg(self, value = None):
		self.__crnt_msg = value

	@property
	def crnt_msg(self):
		return self.__crnt_msg

	def publish(self, input_data_hex: str, diag_name: str, frame_id: str, parameter_name: str, device_id: str = ""):
		data_hex = input_data_hex.replace(" ", "")
		# data_hex = data_hex.ljust(16, '0')
		data_hex = " ".join(data_hex[i:i+2] for i in range(0, len(data_hex), 2))
		pub_message = f"server:>{device_id} {frame_id} {data_hex}<"
		self.set_crnt_msg({
			"diag_name": diag_name,
			"parameter_name": parameter_name,
			"frame_id": frame_id,
			"input_data": data_hex,
			"data": pub_message
		})
		self.__mqtt_client.publish(pub_message)

	def publish_raw(self, device_id: str, message):
		pub_message = f"server:>{device_id} {message}<"
		self.set_crnt_msg({
			"diag_name": "raw",
			"parameter_name": "raw",
			"frame_id": "raw",
			"input_data": message,
			"data": pub_message
		})
		self.__mqtt_client.publish(pub_message)

	async def publish_all(self):
		for did in self.__dids_list:
			for device_id in self.__device_ids.keys():
				# print("Publishing for device: ", device_id)
				self.publish(input_data_hex = did.hex_data, diag_name = did.diag_name, frame_id = did.frame_id, device_id = device_id, parameter_name = did.parameter_name)
			await self.wait_for_msgs_recvd()

		self.__mqtt_client.stop()
		self.__thrd.join()
		del self.__mqtt_client
		del self.__thrd

	async def get_logs(self):
		await self.publish_all()
		return self.__logs
