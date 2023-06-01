from models import (
	SelectedDIDVehicle,
	Vehicle,
	VehicleDBCDids,
)
from controller.dbcController import DBCDecoder
import random, string, asyncio
from subscribers import DataController
from subscribers import StatusGetter
from backgroundTasks.vehicleLogsTask import (
    wait_for_data_async, 
    gps_status_schedule,
    vehicle_logs_schedule,
)
from schemas import (
	VehicleDID,
	List,
)
from subscribers.vehicleLogsSubscriber import VehicleLogsSubscriber

from utils import Logger

logger = Logger(__name__)

class VehicleDbcController:

	@staticmethod
	def get_new_device_id():
		new_device_id = lambda: ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=10))

		device_id = new_device_id()
		while VehicleDBCDids.objects(device_id = device_id).first():
			device_id = new_device_id()
		return device_id

	@staticmethod
	def get_vehicle_dids(vehicle_id):
		try:
			vehicle = Vehicle.objects(vin = vehicle_id).first()
			if vehicle:
				vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
				return {
					"model_id": str(vehicle.model.id),
					"model_name": vehicle.model.name,
					"vehicle_id": vehicle.vin,
					"chip_id": vehicle.chipId,
					"dids_list": [
						{
							"diag_name": did.diag_name,
							"frame_id": did.frame_id,
							# "start_bit": did.start_bit,
							"hex_data": did.hex_data,
							# "did": did.did,
							"data_type": did.data_type,
							"parameter_name": did.parameter_name,
						}
						for did in vehicle_dbc.dids_list
					] if vehicle_dbc else []
				}
			return None
		except Exception as e:
			logger.error(f"Error: {e}")
			return None

	@staticmethod
	async def get_vehicle_vin_chipid(vehicle_id, frame_id, input_data_hex):
		try:
			vehicle : Vehicle = Vehicle.objects(vin = vehicle_id).first()
			if not vehicle:
				return
			vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
			if not vehicle_dbc:
				vehicle_dbc = VehicleDBCDids(
					vehicle = vehicle,
					model = vehicle.model,
					device_id = VehicleDbcController.get_new_device_id(),
				)
				vehicle_dbc.save()

			def callback(message: str):
				message = message.lower()
				if message.startswith("server"):
					return
				device_id, log_data = StatusGetter.diagonostic_callback(
					crnt_msg = log_subscriber.crnt_msg,
					data = message,
					add_to_influx = False
				)
				log_subscriber.set_crnt_msg()
				if log_data and isinstance(log_data, dict) and log_data.get("diag_name", None) == "Vehicle VIN":
					Vehicle.objects(vin = vehicle_id).update(
						set__chipId = device_id
					)
					vehicle_dbc.device_id = device_id
					vehicle_dbc.save()
			log_subscriber = VehicleLogsSubscriber(
				vehicle_ids = [],
				dids_list = [],
				add_to_influx = False,
				callback = callback,
				timeout = 5,
			)
			log_subscriber.publish(
				diag_name = "Vehicle VIN",
				parameter_name = "VIN",
				frame_id = frame_id,
				input_data_hex = input_data_hex,
			)
			await log_subscriber.wait_for_msgs_recvd()

			# if len(logs) == 1:
			# 	log_data = logs[0]
			# 	device_id = log_data["device_id"]

			# def callback(crnt_msg, data):
			# 	log_data = StatusGetter.diagonostic_callback(crnt_msg, data, add_to_influx=False)
			# 	if log_data and isinstance(log_data, dict):
			# 		if log_data.get("diag_name", None) == "VehicleVIN":
			# 			vehicle.chipId = log_data.get("device_id", None)
			# 			vehicle.save()
			# 			vehicle_dbc.device_id = log_data.get("device_id", None)
			# 			vehicle_dbc.save()

			# event_loop = asyncio.get_event_loop()
			# task = event_loop.create_task(wait_for_data_async(callback = callback, timeout = 60))
			# try:
			# 	StatusGetter.publish(diag_name = "VehicleVIN", frame_id = frame_id, inpt_data_hex = input_data_hex)
			# except Exception as e:
			# 	logger.error(f"Error: {e}")
			# await task

			await gps_status_schedule()
			return vehicle.chipId
			### End of prototype
		except Exception as e:
			logger.error(f"Error: {e}")
			return None

	@staticmethod
	def add_update_vehicle_dids(vehicle_id, dids_list: List[VehicleDID]):
		try:
			vehicle : Vehicle = Vehicle.objects(vin = vehicle_id).first()
			if vehicle:
				vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
				### Specifically for the prototype

				### End of prototype
				new_dids_list = [
					SelectedDIDVehicle(
						diag_name = did.diag_name,
						frame_id = did.frame_id,
						parameter_name = did.parameter_name,
						# start_bit = did.start_bit,
						hex_data = did.hex_data,
						data_type = did.data_type,
						# did = did.did,
					)
					for did in dids_list
				]
				if vehicle_dbc:
					vehicle_dbc.dids_list = new_dids_list
					vehicle_dbc.save()
				else:
					vehicle_dbc = VehicleDBCDids(
						vehicle = vehicle,
						model = vehicle.model,
						device_id = VehicleDbcController.get_new_device_id(),
						dids_list = new_dids_list,
					)
					vehicle_dbc.save()
				return {
					"model_id": str(vehicle.model.id),
					"model_name": vehicle.model.name,
					"vehicle_id": vehicle.vin,
					"chip_id": vehicle.chipId,
					"dids_list": [
						{
							"diag_name": did.diag_name,
							"frame_id": did.frame_id,
							"data_type": did.data_type,
							"parameter_name": did.parameter_name,
							"hex_data": did.hex_data,
							# "start_bit": did.start_bit,
							# "did": did.did,
						}
						for did in vehicle_dbc.dids_list
					]
				}
			vehicle_logs_schedule.apply_async()
			return None
		except Exception as e:
			logger.error(f"Error: {e}")
			return None

	@staticmethod
	def decode_vehicle_raw_data(device_id, did, raw_data):
		try:
			vehicle_dbc = VehicleDBCDids.objects(device_id = device_id).first()
			if not vehicle_dbc:
				return None
			vehicle = vehicle_dbc.vehicle
			dbc_decoder = DBCDecoder(file = vehicle_dbc.dbc_file.file)
			data = bytes.fromhex(raw_data)
			decoded_data = dbc_decoder.decode_message(
				message_id = int(did),
				data = data,
			)
			return decoded_data
		except Exception as e:
			logger.error(f"Error: {e}")
			return None
