from utils import InfluxClient, INFLUX_DBNAME
import datetime
from models import (
	Vehicle,
	VehicleDBCDids
)
from schemas import (
	VehicleLogsObject,
)
import asyncio, time
from backgroundTasks.vehicleLogsTask import wait_for_data_async
from subscribers import StatusGetter
from utils import Logger
from subscribers.vehicleLogsSubscriber import VehicleLogsSubscriber
from subscribers.snapshotSubscriber import SnapShotSubscriber

logger = Logger(__name__)

class VehicleLogsController:

	@staticmethod
	def get_vehicle_logs(vehicle_id, start_time = None, end_time = None, page = 1, limit = 10):
		try:
			if not end_time:
				end_time = datetime.datetime.utcnow()
			if not start_time:
				start_time = end_time - datetime.timedelta(days = 1)

			vehicle = Vehicle.objects(vin = vehicle_id).first()
			if not vehicle:
				return None
			
			vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
			if not vehicle_dbc:
				return None
			influx_client = InfluxClient()
			query = f"""from(bucket: "{INFLUX_DBNAME}")
|> range(start: {start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}, stop: {end_time.strftime("%Y-%m-%dT%H:%M:%SZ")})
|> filter(fn: (r) => r["_measurement"] == "{vehicle_dbc.device_id}")
|> sort(columns: ["_time"], desc: true)
|> limit(n: {page*limit})
"""
			add_data = {
				"check": [],
				"decoded_data": [],
				"diag_name": [],
				"frame_id": [],
				"input_data": [],
				"parameter_name": [],
				"raw_data": [],
				"received_data": [],
				"success": [],
				"time": [],
				"vin": [],
			}
			for _ in influx_client.query(query):
				for __ in _:
					add_data[__["_field"]].append(__["_value"])
					if len(add_data["time"]) != len(list(_)):
						add_data["time"].append(__["_time"])
						add_data["vin"].append(vehicle_id)

			return [
				VehicleLogsObject(
					check = ch,
					decoded_data = dd,
					diag_name = dn,
					frame_id = fi,
					input_data = id,
					parameter_name = pn,
					raw_data = rd,
					received_data = rcvd,
					success = sc,
					time = t,
					vin = v,
				)
				for ch, dd, dn, fi, id, pn, rd, rcvd, sc, t, v in zip(
					add_data["check"],
					add_data["decoded_data"],
					add_data["diag_name"],
					add_data["frame_id"],
					add_data["input_data"],
					add_data["parameter_name"],
					add_data["raw_data"],
					add_data["received_data"],
					add_data["success"],
					add_data["time"],
					add_data["vin"],
				)
			]
		except Exception as e:
			logger.error(f"Error: {e}")
			return None
		
	@staticmethod
	async def get_live_logs_v2(vehicle_ids, dids_list, timeout = 5):
		st = time.time()
		logs_controller = VehicleLogsSubscriber(
			vehicle_ids = vehicle_ids,
			dids_list = dids_list,
			timeout = timeout
		)
		logs = await logs_controller.get_logs()
		print("Time taken: ", time.time() - st)
		return logs

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
		num_callback_called = 0
		def callback(crnt_msg, data):
			nonlocal num_callback_called
			num_callback_called += 1
			if num_callback_called > len(dids_list) * len(vehicle_ids):
				all_msgs_received.set()
			log_data = StatusGetter.diagonostic_callback(crnt_msg, data, add_to_influx=False)
			if not log_data:
				return
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
					"frame_id": log_data["frame_id"],
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
	
	@staticmethod
	async def get_vehicle_snapshot(vehicle_ids, dids_list):
		ret_data = []
		for vehicle_id in vehicle_ids:
			vehicle = Vehicle.objects(vin = vehicle_id).first()
			if not vehicle:
				return None
			vehicle_dbc = VehicleDBCDids.objects(vehicle = vehicle).first()
			if not vehicle_dbc:
				return None
			vss = SnapShotSubscriber(device_id = vehicle_dbc.device_id)
			read_time = datetime.datetime.now()
			ecu_logs, dtc_data, odo_read = await vss.take_snapshot(dids = dids_list)
			ret_data.append({
				"vin": vehicle_id,
				"read_time": read_time,
				"odo_read": odo_read,
				"ecu_logs": ecu_logs,
				# "dtc": dtc_data,
			})
		return ret_data