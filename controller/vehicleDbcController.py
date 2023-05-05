from models import (
	SelectedDIDVehicle,
	Vehicle,
	FileFields,
	VehicleDBCDids,
	VehicleModel,
)
from controller.dbcController import DBCDecoder
from bson import DBRef, ObjectId
from uuid import uuid4
import random, string
from subscribers import DataController


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
							"start_bit": did.start_bit,
							"hex_data": did.hex_data,
							# "did": did.did,
						}
						for did in vehicle_dbc.dids_list
					] if vehicle_dbc else []
				}
			return None
		except Exception as e:
			print(e)
			return None

	@staticmethod
	async def get_vehicle_vin_chipid(vehicle_id):
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

			### Specifically for the prototype
			def callback(device_id: str, decoded_data: str, success: bool):
				if success:
					vehicle_dbc.device_id = device_id
					vehicle_dbc.save()
					vehicle.chipId = device_id
					vehicle.save()
			dbc_proto = DataController(frame_id = 1971, inpt_data_hex = "22F190", callback = callback)
			dbc_proto.configure()
			dbc_proto.publish()
			await dbc_proto.wait_for_data_async(timeout = 100)
			return vehicle.chipId
			### End of prototype
		except Exception as e:
			print(e)
			return None

	@staticmethod
	def add_update_vehicle_dids(vehicle_id, dids_list):
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
						start_bit = did.start_bit,
						hex_data = did.hex_data,
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
							"start_bit": did.start_bit,
							"hex_data": did.hex_data,
							# "did": did.did,
						}
						for did in vehicle_dbc.dids_list
					]
				}
			return None
		except Exception as e:
			print(e)
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
			print(e)
			return None
