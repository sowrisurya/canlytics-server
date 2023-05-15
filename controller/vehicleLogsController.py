from utils import InfluxClient, REDIS_CLIENT
import datetime
from models import (
	Vehicle,
	VehicleDBCDids
)
from schemas import (
	VehicleLogsObject,
)
import pandas as pd
import asyncio, json, time
from backgroundTasks.vehicleLogsTask import wait_for_data_async
from subscribers import StatusGetter
import logging

logger = logging.getLogger(__name__)


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
						if (log_measure.update({"vin": vehicle_id})) or True
					]
					return [
						VehicleLogsObject(**item)
						for item in data
					] if data else None
		except Exception as e:
			logger.error(f"Error: {e}")
			return None

	@staticmethod
	async def get_live_logs(vehicle_ids, dids_list, timeout = 100):
		vehicle_logs_data = {
			vehicle_dbc.device_id: {
				"vehicle_id": vehicle_id,
				"logs": []
			}
			for vehicle_id in vehicle_ids
			if (vehicle := Vehicle.objects(vin = vehicle_id).first())
			if (vehicle_dbc := VehicleDBCDids.objects(vehicle = vehicle).first())
		}
		all_msgs_received = asyncio.Event()

		def callback(crnt_msg, data):
			log_data = StatusGetter.diagonostic_callback(crnt_msg, data, add_to_influx=False)
			if log_data["success"] == "True":
				device_id = log_data["device_id"]
				if device_id not in vehicle_logs_data:
					return
				vehicle_logs_data[device_id]["logs"].append({
					"time": datetime.datetime.utcnow(),
					"raw_data": log_data["raw_data"],
					"input_data": log_data["input_data"],
					"decoded_data": log_data["decoded_data"],
					"diag_name": log_data["diag_name"],
					"vin": vehicle_logs_data[device_id]["vehicle_id"],
					"frame_id": int(log_data["frame_id"]),
				})
				if len(vehicle_logs_data[device_id]["logs"]) == len(dids_list):
					all_msgs_received.set()

		event_loop = asyncio.get_event_loop()
		task = event_loop.create_task(wait_for_data_async(callback = callback, timeout = timeout, async_event = all_msgs_received))
		for did in dids_list:
			try:
				StatusGetter.publish(diag_name=did.diag_name, frame_id=did.frame_id, inpt_data_hex=did.hex_data)
			except Exception as e:
				logger.error(f"Error: {e}")
				pass
		await all_msgs_received.wait()

		return [
			{
				"time": item["time"],
				"raw_data": item["raw_data"],
				"input_data": item["input_data"],
				"decoded_data": item["decoded_data"],
				"diag_name": item["diag_name"],
				"vin": vehicle_logs_data[device_id]["vehicle_id"],
				"frame_id": item["frame_id"],
			}
			for device_id in vehicle_logs_data
			for item in vehicle_logs_data[device_id]["logs"]
		]