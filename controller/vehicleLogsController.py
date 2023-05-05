from utils.influxClient import InfluxClient
import datetime
from models import (
	Vehicle,
	VehicleDBCDids
)
from schemas import (
	VehicleLogsObject,
)
import pandas as pd
from subscribers.dataAdder import DataController


class VehicleLogsController:

	@staticmethod
	def get_flux_duration(num):
		flux_range_time = ""
		if num / 60 >= 0:
			flux_range_time = f"{int(num%60)}s"
			num = num // 60
		if num / 60 > 0:
			flux_range_time = f"{int(num%60)}m" + flux_range_time
			num = num // 60
		if num / 24 > 0:
			flux_range_time = f"{int(num%24)}h" + flux_range_time
			num = num // 24
		if num > 0:
			flux_range_time = f"{int(num)}d" + flux_range_time
		
		return flux_range_time

	@staticmethod
	def get_vehicle_logs(vehicle_id, start_time = None, end_time = None, did = None, limit = None):
		try:
			if not end_time:
				end_time = datetime.datetime.utcnow()
			if not start_time:
				start_time = end_time - datetime.timedelta(days = 1)

			flux_range_time = VehicleLogsController.get_flux_duration((end_time - start_time).total_seconds())
			timeshift_duration = VehicleLogsController.get_flux_duration((datetime.datetime.utcnow() - end_time).total_seconds())

			vehicle = Vehicle.objects(vin = vehicle_id).first()
			if vehicle:
				vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
				if vehicle_dbc:
					influx_client = InfluxClient()
					query = f"""from(bucket: "vehicleDiagnostic")
|> range(start: -{flux_range_time})
|> timeShift(duration: {timeshift_duration})
|> filter(fn: (r) => r["_measurement"] == "{vehicle_dbc.device_id}")
|> group(columns: ["_measurement", "_time"])"""
					data = [
						log_measure
						for table in influx_client.query(query)
						if (
							log_measure := {
								record["_field"]: record["_value"]
								for record in table
							}
						)
						if (log_measure.update({"time": list(table)[0]["_time"]})) or True
					]
					return [
						VehicleLogsObject(**item)
						for item in data
					] if data else None
		except Exception as e:
			print(e)
			return None

	@staticmethod
	async def get_live_logs(vehicle_ids, dids_list, timeout = 10):
		vehicle_logs_data = {
			vehicle_dbc.device_id: {
				"vehicle_id": vehicle_id,
				"logs": []
			}
			for vehicle_id in vehicle_ids
			if (vehicle := Vehicle.objects(vin = vehicle_id).first())
			if (vehicle_dbc := VehicleDBCDids.objects(vehicle = vehicle).first())
		}

		def callback(device_id: str, raw_data: str, input_data: str, decoded_data: str, success: bool, diag_name: str, frame_id: int, **kwargs):
			if success:
				vehicle_logs_data[device_id]["logs"].append({
					"time": datetime.datetime.utcnow(),
					"raw_data": raw_data,
					"input_data": input_data,
					"decoded_data": decoded_data,
					"diag_name": diag_name,
					"vin": vehicle_logs_data[device_id]["vehicle_id"],
					"frame_id": frame_id,
				})

		for did in dids_list:
			data_controller = DataController(
				frame_id = did.frame_id,
				inpt_data_hex = did.hex_data.ljust(16, "0"),
				callback = callback,
				max_clients = len(vehicle_ids),
			)
			data_controller.configure()
			data_controller.publish()
			await data_controller.wait_for_data_async(timeout=timeout)
			data_controller.kill()

		return [
			{
				"time": item["time"],
				"raw_data": item["raw_data"],
				"input_data": item["input_data"],
				"decoded_data": item["decoded_data"],
				"diag_name": item["diag_name"],
				"vin": vehicle_logs_data[device_id]["vehicle_id"],
				"frame_id": 0,
			}
			for device_id in vehicle_logs_data
			for item in vehicle_logs_data[device_id]["logs"]
		]